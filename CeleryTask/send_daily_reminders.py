import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from celery import Celery
from celery.schedules import crontab
from models.Service_Request import Service_Request
from app import db
from sqlalchemy.orm import sessionmaker

app = Celery('reminders', broker='your_broker_url')
# Database session setup
Session = sessionmaker(bind=db.engine)
session = Session()


@app.task
def send_daily_reminders():
    # Query for pending service requests
    pending_requests = session.query(Service_Request).filter(Service_Request.service_status == 'pending').all()

    # Get the professionals associated with the pending requests
    professionals = [request.professional for request in pending_requests]

    for professional in professionals:
        # Send reminder (e.g., using Google Chat, SMS, or email)
        send_alert( "Reminder to accept/reject your service request", professional.mobile)

    session.close()


# Schedule to run daily at 6 PM
app.conf.beat_schedule = {
    'send-daily-reminders': {
        'task': 'send_daily_reminders',
        'schedule': crontab(hour=18, minute=0),  # 6 PM every day
    },
}

def send_alert(message,customer_email):
    sender_email = "anujomer111@gmail.com"
    receiver_email = customer_email
    password = "An@240702"

    subject = "Alert: Task Complete"

    # Create the email content
    body = f"Task completed successfully!\n\nDetails:\n{message}"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Send the email
    try:
        with smtplib.SMTP('smtp.example.com', 587) as server:
            server.starttls()  # Encrypt connection
            server.login(sender_email, password)
            text = msg.as_string()
            server.sendmail(sender_email, receiver_email, text)
        print("Alert email sent successfully.")
    except Exception as e:
        print(f"Error sending alert email: {e}")
