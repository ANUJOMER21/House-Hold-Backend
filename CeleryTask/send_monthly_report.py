from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from flask import render_template_string
from models.Service_Request import Service_Request
from database import db
import smtplib  # or another email library

# Database session setup
Session = sessionmaker(bind=db.engine)
session = Session()

def generate_weekly_report(customer, service_requests):
    # Calculate the start and end of the current week
    now = datetime.now()
    start_of_week = now - timedelta(days=now.weekday())  # Start of the week (Monday)
    end_of_week = start_of_week + timedelta(days=6)  # End of the week (Sunday)

    # Filter service requests for this customer and this week
    filtered_requests = [
        request for request in service_requests
        if request.customer_id == customer.customer_id and start_of_week <= request.date_of_request <= end_of_week

    ]
    print(filtered_requests)


    # Create a summary of the service requests
    total_requests = len(filtered_requests)
    closed_requests = [req for req in filtered_requests if req.status == 'completed']
    pending_requests = [req for req in filtered_requests if req.status != 'completed']

    # Generate HTML content for the report
    html_content = render_template_string("""
    <html>
    <head><title>Weekly Service Report</title></head>
    <body>
        <h1>Weekly Service Report for {{ customer.customer_name }}</h1>
        <p>Report for the week of {{ start_of_week.strftime('%B %d, %Y') }} to {{ end_of_week.strftime('%B %d, %Y') }}</p>
        
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
    """, customer=customer, start_of_week=start_of_week, end_of_week=end_of_week,
          total_requests=total_requests, closed_requests=closed_requests, pending_requests=pending_requests,
          filtered_requests=filtered_requests)

    return html_content

def send_weekly_report():
    now = datetime.now()

    # Calculate the start and end of the last week
    end_of_last_week = now - timedelta(days=now.weekday() + 1)  # End of the last week (Sunday)
    start_of_last_week = end_of_last_week - timedelta(days=6)  # Start of the last week (Monday)

    # Query for service requests from the last week
    service_requests = session.query(Service_Request).filter(
        Service_Request.date_of_request >= start_of_last_week,
        Service_Request.date_of_request <= end_of_last_week
    ).all()
    print(service_requests)

    # Generate and send reports for each customer
    customers = set([request.customer for request in service_requests])
    for customer in customers:
        report = generate_weekly_report(customer, service_requests)
        # print(report)
        #send_alert(report, customer.customer_email)  # Send email to customer

    session.close()

# Schedule this function to run on a weekly basis (e.g., every Monday at midnight)
