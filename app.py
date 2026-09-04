import os
import json
from html import escape
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('jdmt.html')

@app.route('/contact', methods=['POST'])
def contact():
    try:
        data = request.get_json(silent=True) or {}

        name = str(data.get('name', '')).strip()
        email = str(data.get('email', '')).strip()
        project = str(data.get('project', '')).strip()
        message = str(data.get('message', '')).strip()

        if not all((name, email, project, message)):
            return jsonify({'error': 'Please complete all required fields'}), 400

        resend_api_key = os.environ.get('RESEND_API_KEY')
        recipient_email = os.environ.get('RECIPIENT_EMAIL', 'taniegrarj@jdmt-itservices.com')
        sender_email = os.environ.get('SENDER_EMAIL', 'noreply@jdmt-itservices.com')

        if not resend_api_key:
            return jsonify({'error': 'Email service not configured'}), 500

        email_payload = {
            'from': f'JDMT Website <{sender_email}>',
            'to': [recipient_email],
            'reply_to': email,
            'subject': f'New Contact from {name} - {project}',
            'html': f"""
                <h2>New Contact Form Submission</h2>
                <p><strong>Name:</strong> {escape(name)}</p>
                <p><strong>Email:</strong> {escape(email)}</p>
                <p><strong>Project:</strong> {escape(project)}</p>
                <p><strong>Message:</strong></p>
                <p>{escape(message).replace(chr(10), '<br>')}</p>
            """,
        }

        resend_request = Request(
            'https://api.resend.com/emails',
            data=json.dumps(email_payload).encode('utf-8'),
            headers={
                'Authorization': f'Bearer {resend_api_key}',
                'Content-Type': 'application/json',
            },
            method='POST',
        )

        with urlopen(resend_request, timeout=15) as response:
            if response.status not in (200, 201):
                raise RuntimeError('Resend rejected the email request')

        return jsonify({'success': True, 'message': 'Message sent successfully'}), 200

    except (HTTPError, URLError, TimeoutError, RuntimeError):
        app.logger.exception('Unable to send contact email through Resend')
        return jsonify({'error': 'Unable to send your message right now. Please try again later.'}), 502
    except Exception:
        app.logger.exception('Unexpected contact form error')
        return jsonify({'error': 'Unable to send your message right now. Please try again later.'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
