import csv


from models.Service_Request import Service_Request
from database import db
from sqlalchemy.orm import sessionmaker# t if needed for accessing Config
# Database session setup

def export_service_request():

    file_path = "Graph/generated_images/service_requests.csv"

    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header row
        writer.writerow(['service_name', 'customer_name', 'professional_name', 'date_of_request', 'date_of_completion', 'remarks'])

        # Query the database for service requests
        data = Service_Request.query.all()
        for r in data:
            writer.writerow(
                [
                    r.service.service_name if r.service else '',
                    r.customer.customer_name if r.customer else '',
                    r.professional.name if r.professional else '',
                    r.date_of_request.strftime('%Y-%m-%d') if r.date_of_request else '',
                    r.date_of_completion.strftime('%Y-%m-%d') if r.date_of_completion else '',
                    r.remarks if r.remarks else ''
                ]
            )
    return file_path


