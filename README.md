# Phishing Website Simulator

This is a Flask-based phishing website simulator that mimics login pages for various social media platforms (Google, Facebook, Instagram, Twitter) and captures the credentials entered by users.

## Disclaimer

**This tool is created for educational purposes only.** Using this tool to perform phishing attacks without explicit consent is illegal and unethical. The creator of this tool is not responsible for any misuse or damage caused by this tool.

## Features

- Realistic login pages for multiple social media platforms
- Credential capture and storage
- Admin panel to view captured credentials
- Responsive design for mobile and desktop

## Installation

1. Clone this repository:
```
git clone <repository-url>
```

2. Navigate to the project directory:
```
cd phishing-website-simulator
```

3. Create a virtual environment:
```
python -m venv venv
```

4. Activate the virtual environment:
   - On Windows:
   ```
   venv\Scripts\activate
   ```
   - On macOS/Linux:
   ```
   source venv/bin/activate
   ```

5. Install the required dependencies:
```
pip install -r requirements.txt
```

## Usage

1. Start the Flask application:
```
python app.py
```

2. Access the application in your web browser at `http://127.0.0.1:5000`

3. Choose a social media platform to simulate

4. Send the link to the target (for educational purposes only, with consent)

5. View captured credentials in the admin panel at `http://127.0.0.1:5000/admin`
   - Admin credentials:
     - Username: `cyberwolf`
     - Password: `cyberwolf123`

## Customization

You can customize the appearance of the login pages by modifying the HTML templates in the `templates` directory and the CSS files in the `static/css` directory.

## Security Considerations

- Change the default admin credentials in `app.py`
- Use HTTPS in production to encrypt data transmission
- Implement proper authentication for the admin panel

## License

This project is for educational purposes only. Do not use for illegal activities.
