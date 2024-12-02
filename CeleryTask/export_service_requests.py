from celery import Celery
import csv
from sqlalchemy.orm import sessionmaker
import os  # For securely accessing environment variables

from models.Service_Request import Service_Request
from app import db, create_app  # Ensure you import the app factory function

# Configure Celery
app = Celery('reminders', broker='your_broker_url')

@app.task
def export_service_requests():
    # Create an application context for the current task
    with create_app().app_context():  # Assuming you have a factory function `create_app`
        # Database session setup within the app context
        Session = sessionmaker(bind=db.engine)
        session = Session()

        try:
            # Query for closed service requests
            closed_requests = session.query(Service_Request).filter(Service_Request.status == 'closed').all()

            # Export data to CSV
            csv_filename = 'service_requests.csv'
            with open(csv_filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['service_id', 'customer_id', 'professional_id', 'date_of_request', 'remarks'])

                for request in closed_requests:
                    writer.writerow([request.id, request.customer_id, request.professional_id, request.date_of_request, request.remarks])

            print(f"CSV file '{csv_filename}' created successfully.")
        except Exception as e:
            print(f"Error during export: {e}")
        finally:
            session.close()  # Ensure the session is closed properly
