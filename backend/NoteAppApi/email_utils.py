import os
import requests


def send_brevo_email(
    recipient_email,
    subject,
    html_content
):
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": os.getenv("BREVO_API_KEY"),
        "content-type": "application/json",
    }
    payload = {
        "sender": {
            "name": "Smart Notes",
            "email": "isaacharu17@gmail.com"
        },
        "to": [
            {
                "email": recipient_email
            }
        ],
        "subject": subject,
        "htmlContent": html_content
    }
    response = requests.post(   url,
        json=payload,
        headers=headers
    )
    return response
