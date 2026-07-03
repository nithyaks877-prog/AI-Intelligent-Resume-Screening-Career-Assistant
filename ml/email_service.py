import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")


def send_password_reset_email(to_email: str, reset_link: str):
    """
    Sends a password reset email via Gmail SMTP.
    """

    if not EMAIL_ADDRESS or not EMAIL_APP_PASSWORD:
        raise ValueError(
            "EMAIL_ADDRESS or EMAIL_APP_PASSWORD not found in .env file."
        )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Reset your HireSense AI password"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    text_body = f"""
Hi,

We received a request to reset your HireSense AI password.

Click the link below to set a new password. This link expires in 30 minutes.

{reset_link}

If you didn't request this, you can safely ignore this email.
"""

    html_body = f"""
<html>
  <body style="font-family: Arial, sans-serif; color: #0F172A;">
    <h2>Reset your HireSense AI password</h2>
    <p>We received a request to reset your password.</p>
    <p>
      <a href="{reset_link}"
         style="background-color:#0B0F19;color:#ffffff;padding:12px 24px;
                text-decoration:none;border-radius:8px;display:inline-block;">
        Reset Password
      </a>
    </p>
    <p style="color:#64748B;font-size:13px;">
      This link expires in 30 minutes. If you didn't request this,
      you can safely ignore this email.
    </p>
  </body>
</html>
"""

    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
