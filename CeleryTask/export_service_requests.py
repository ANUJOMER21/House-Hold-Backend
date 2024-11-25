from celery import Celery
import csv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import sessionmaker

from models.Service_Request import Service_Request
import smtplib  # or another notification method
from app import db

app = Celery('reminders', broker='your_broker_url')

# Database session setup
Session = sessionmaker(bind=db.engine)
session = Session()


@app.task
def export_service_requests():
    # Query for closed service requests
    closed_requests = session.query(Service_Request).filter(Service_Request.status == 'closed').all()

    # Export data to CSV
    csv_filename = 'service_requests.csv'
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['service_id', 'customer_id', 'professional_id', 'date_of_request', 'remarks'])

        for request in closed_requests:
            writer.writerow(
                [request.id, request.customer_id, request.professional_id, request.date_of_request, request.remarks])

    send_alert("CSV Export Complete",)  # Notify admin

    session.close()


def send_alert(message):
    # Print message to the console (or log it to a file)
    print(f"ALERT: {message}")


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
