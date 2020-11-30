import aiosmtplib
from config import templates, settings
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

async def send_email(email: list, subject: str, sender: str, html: str, **param) -> None:
    message = MIMEMultipart()

    message['Subject'] = subject
    message['From'] = sender
    message['To'] = ','.join(email)

    template = templates.get_template(html)
    html = template.render(**param)

    message.attach(MIMEText(html,'html'))

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.smtp_server,
            port=settings.smtp_port,
            use_tls=settings.smtp_tls,
            username=settings.smtp_username,
            password=settings.smtp_password
        )
    except aiosmtplib.SMTPException as err:
        raise RuntimeError(err)
