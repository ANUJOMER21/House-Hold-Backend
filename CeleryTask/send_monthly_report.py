from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from celery import Celery
from celery.schedules import crontab
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from flask import render_template_string
from models.Service_Request import Service_Request
from app import db
import smtplib  # or another email library

app = Celery('reminders', broker='your_broker_url')

# Database session setup
Session = sessionmaker(bind=db.engine)
session = Session()


def generate_monthly_report(customer, service_requests):
    # Filter the service requests for the current month and customer
    now = datetime.now()
    start_of_month = datetime(now.year, now.month, 1)
    end_of_month = datetime(now.year, now.month + 1, 1) - timedelta(days=1)

    # Filter service requests for this customer and this month
    filtered_requests = [
        request for request in service_requests
        if request.customer_id == customer.customer_id and start_of_month <= request.date_of_request <= end_of_month
    ]

    # Create a summary of the service requests
    total_requests = len(filtered_requests)
    closed_requests = [req for req in filtered_requests if req.status == 'closed']
    pending_requests = [req for req in filtered_requests if req.status == 'pending']

    # Generate HTML content for the report
    html_content = render_template_string("""
    <html>
    <head><title>Monthly Service Report</title></head>
    <body>
        <h1>Monthly Service Report for {{ customer.customer_name }}</h1>
        <p>Report for the month of {{ now.strftime('%B %Y') }}</p>
        
        <h2>Summary</h2>
        <p>Total requests: {{ total_requests }}</p>
        <p>Closed requests: {{ closed_requests | length }}</p>
        <p>Pending requests: {{ pending_requests | length }}</p>

        <h2>Service Requests</h2>
        <table border="1">
            <tr>
                <th>Service ID</th>
                <th>Date of Request</th>
                <th>Status</th>
                <th>Remarks</th>
            </tr>
            {% for request in filtered_requests %}
            <tr>
                <td>{{ request.service_id }}</td>
                <td>{{ request.date_of_request.strftime('%Y-%m-%d') }}</td>
                <td>{{ request.status }}</td>
                <td>{{ request.remarks }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """, customer=customer, now=now, total_requests=total_requests,
                                          closed_requests=closed_requests, pending_requests=pending_requests,
                                          filtered_requests=filtered_requests)

    return html_content


@app.task
def send_monthly_report():
    from datetime import datetime, timedelta
    now = datetime.now()

    # Get start and end of the last month
    start_of_last_month = datetime(now.year, now.month - 1, 1)
    end_of_last_month = datetime(now.year, now.month, 1) - timedelta(days=1)

    # Query for service requests from the last month
    service_requests = session.query(Service_Request).filter(
        Service_Request.date_of_request >= start_of_last_month,
        Service_Request.date_of_request <= end_of_last_month
    ).all()

    # Generate and send reports for each customer
    customers = set([request.customer for request in service_requests])
    for customer in customers:
        report = generate_monthly_report(customer, service_requests)
        send_alert(report, customer.customer_email)  # Send email to customer

    session.close()


# Schedule to send report on the 1st of every month at midnight
app.conf.beat_schedule = {
    'send-monthly-report': {
        'task': 'send_monthly_report',
        'schedule': crontab(hour=0, minute=0, day_of_month=1),  # First day of the month
    },
}


def send_alert(message, customer_email):
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
