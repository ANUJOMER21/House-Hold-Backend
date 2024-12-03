import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Email credentials
GMAIL_USER = 'anujomer6@gmail.com'
GMAIL_PASSWORD = 'xome mtoa rtrz rpll'

def send_email_with_attachment(subject, body, to_email, attachment_path):
    try:
        # Set up the MIME
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject

        # Attach the email body
        msg.attach(MIMEText(body, 'plain'))

        # Attach the CSV file
        with open(attachment_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())

        # Encode file in ASCII characters for email
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename={attachment_path.split("/")[-1]}',
        )
        msg.attach(part)

        # Connect to Gmail's SMTP server
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Start TLS encryption
            server.login(GMAIL_USER, GMAIL_PASSWORD)  # Login
            server.sendmail(GMAIL_USER, to_email, msg.as_string())  # Send email

        print(f"Email with attachment sent successfully to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def send_email(subject, body, to_email ):
    try:
        # Set up the MIME
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject

        # Attach the email body
        msg.attach(MIMEText(body, 'plain'))

        # Attach the CSV file


        # Connect to Gmail's SMTP server
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Start TLS encryption
            server.login(GMAIL_USER, GMAIL_PASSWORD)  # Login
            server.sendmail(GMAIL_USER, to_email, msg.as_string())  # Send email

        print(f"Email with attachment sent successfully to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")
