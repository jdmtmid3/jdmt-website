import os
import re
import smtplib
import ssl
from email.message import EmailMessage
from html import escape

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

@app.route('/')
def index():
    return render_template('jdmt.html')

@app.route('/terms-of-use')
def terms_of_use():
    return render_template('legal.html', page='terms')

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('legal.html', page='privacy')

@app.route('/cookie-policy')
def cookie_policy():
    return render_template('legal.html', page='cookies')

@app.route('/faqs')
def faqs():
    return render_template('legal.html', page='faqs')

@app.route('/contact', methods=['POST'])
def contact():
    try:
        data = request.get_json(silent=True) or {}

        name = str(data.get('name', '')).strip()
        email = str(data.get('email', '')).strip()
        project = str(data.get('project', '')).strip()
        message = str(data.get('message', '')).strip()

        # Project is optional in the website form, so it must also be optional
        # here. Previously, inquiries without a project were rejected.
        if not all((name, email, message)):
            return jsonify({'error': 'Please complete all required fields'}), 400

        if not EMAIL_PATTERN.match(email):
            return jsonify({'error': 'Please enter a valid email address'}), 400

        if any(len(value) > limit for value, limit in (
            (name, 120), (email, 254), (project, 160), (message, 5000)
        )):
            return jsonify({'error': 'One or more fields are too long'}), 400

        smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        smtp_username = os.environ.get('SMTP_USERNAME', '').strip()
        smtp_password = os.environ.get('SMTP_PASSWORD', '')
        recipient_email = os.environ.get('RECIPIENT_EMAIL', 'jdmtmid3@gmail.com').strip()

        if not smtp_username or not smtp_password:
            return jsonify({'error': 'Email service not configured'}), 500

        email_message = EmailMessage()
        email_message['From'] = f'JDMT Website <{smtp_username}>'
        email_message['To'] = recipient_email
        email_message['Reply-To'] = email
        email_message['Subject'] = 'New JDMT website inquiry'
        email_message.set_content(
            f'Name: {name}\nEmail: {email}\nProject: {project or "Not specified"}\n\nMessage:\n{message}'
        )
        email_message.add_alternative(
            f"""
                <h2>New Contact Form Submission</h2>
                <p><strong>Name:</strong> {escape(name)}</p>
                <p><strong>Email:</strong> {escape(email)}</p>
                <p><strong>Project:</strong> {escape(project) if project else 'Not specified'}</p>
                <p><strong>Message:</strong></p>
                <p>{escape(message).replace(chr(10), '<br>')}</p>
            """,
            subtype='html',
        )

        tls_context = ssl.create_default_context()
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as smtp:
            smtp.starttls(context=tls_context)
            smtp.login(smtp_username, smtp_password)
            smtp.send_message(email_message)

        return jsonify({'success': True, 'message': 'Message sent successfully'}), 200

    except (smtplib.SMTPException, OSError, ValueError):
        app.logger.exception('Unable to send contact email through SMTP')
        return jsonify({'error': 'Unable to send your message right now. Please try again later.'}), 502
    except Exception:
        app.logger.exception('Unexpected contact form error')
        return jsonify({'error': 'Unable to send your message right now. Please try again later.'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
