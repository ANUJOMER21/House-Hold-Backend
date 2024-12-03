import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from models.Customer import Customer
from models.Service_Request import Service_Request
from database import db
from sqlalchemy.orm import sessionmaker

# Database session setup




def send_daily_reminders_to_customer():
    # Query for pending service requests
    customers = Customer.query.all()

    # Get the professionals associated with the pending requests


    return customers







