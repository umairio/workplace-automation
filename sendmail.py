import os
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import yagmail
from dotenv import load_dotenv

from logger import logger

load_dotenv()
def send_mail(email, image=None):
    """
    :param image: str (path to the image)
    :param email: str (recipient email)
    :return: None
    """
    try:
        sender_email = os.environ.get("MAIL_USERNAME")
        sender_password = os.environ.get("MAIL_PASSWORD")

        yag = yagmail.SMTP(user=sender_email, password=sender_password)

        subject = "Join Our Discord Server!"
        template = """
        <html>
            <body>
                <h2>Welcome!</h2>
                <p>We're excited to invite you to our Discord server.</p>
                <p>You can join us using the following link:</p>
                <p><a href="https://discord.gg/qGMcKAXG">Join Discord Server</a></p>
                <p>Looking forward to seeing you there!</p>
            </body>
        </html>
        """
        yag.send(
            to=email,
            subject=subject,
            contents=template,
            attachments=[image] if image else None
        )

        print(f"Success: Email sent to {email}")

    except Exception as e:
        print(f"Failed to send email to {email}: {e}")

def send_email(email, image=None):
    """
    :param image: str
    :param email: str
    :return: None
    """
    try:
        message = MIMEMultipart()
        message["From"] = os.environ.get("MAIL_USERNAME")
        message["To"] = email
        message["Subject"] = "Check-In Successful"

        # HTML content
        with open("email.html", "r") as file:
            template = file.read()
        if image:
            with open(image, "rb") as img:
                mime_img = MIMEImage(img.read())
                mime_img.add_header("Content-ID", "<image1>")
                message.attach(mime_img)
            template = template.replace(
                "https://gxowkk.stripocdn.email/content/guids/CABINET_1232eee4cab038122cd07270cd3bb85f/images/70451618316407074.png",
                "cid:image1"
            )
        message.attach(MIMEText(template, "html"))
        mail = smtplib.SMTP("smtp.gmail.com", 587, timeout=30)
        mail.starttls()
        mail.login(os.environ.get("MAIL_USERNAME"), os.environ.get("MAIL_PASSWORD"))
        mail.sendmail(os.environ.get("MAIL_USERNAME"), email, message.as_string())
        mail.quit()
        logger.info(f"Success email sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send email to {email}: {e}")
