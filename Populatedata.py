from datetime import datetime
from app import db, create_app  # Assuming your SQLAlchemy instance is named `db` and initialized in `app.py`
from models.Customer import Customer # Import your models
from models.Service_Request import Service_Request
from models.ServiceProfessional import ServiceProfessional
from models.Service import Service

def populate_demo_data():
    app = create_app()
    with app.app_context():
        # Clear existing data
        db.session.query(Service_Request).delete()
        db.session.query(Service).delete()
        db.session.query(Customer).delete()
        db.session.query(ServiceProfessional).delete()


        # Add demo customers
        customers = [
            Customer(
                customer_name="John Doe",
                customer_email="john.doe@example.com",
                customer_phone_number="1234567890",
                customer_address="123 Elm Street, Springfield",
                customer_status="active",
                customer_password="hashed_password_1"
            ),
            Customer(
                customer_name="Jane Smith",
                customer_email="jane.smith@example.com",
                customer_phone_number="0987654321",
                customer_address="456 Oak Avenue, Metropolis",
                customer_status="active",
                customer_password="hashed_password_2"
            ),
            Customer(
                customer_name="Alice Brown",
                customer_email="alice.brown@example.com",
                customer_phone_number="1112223333",
                customer_address="789 Pine Street, Gotham",
                customer_status="inactive",
                customer_password="hashed_password_5"
            ),
            Customer(
                customer_name="Bob White",
                customer_email="bob.white@example.com",
                customer_phone_number="4445556666",
                customer_address="101 Maple Drive, Star City",
                customer_status="active",
                customer_password="hashed_password_6"
            ),
        ]

        db.session.add_all(customers)

        # Add demo services
        services = [
            Service(
                service_name="Plumbing",
                service_price=150.0,
                service_time_required=60,
                service_description="Fixing leaks and other plumbing issues",
                image="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSC4tAahBBN-14dqNlv6B9XTZ_DDgt8zKg99g&s"
            ),
            Service(
                service_name="Electrical Repair",
                service_price=200.0,
                service_time_required=90,
                service_description="Repairing electrical appliances and systems",
                image="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSC4tAahBBN-14dqNlv6B9XTZ_DDgt8zKg99g&s"
            ),
            Service(
                service_name="House Cleaning",
                service_price=100.0,
                service_time_required=120,
                service_description="Thorough cleaning of your house",
                image="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSC4tAahBBN-14dqNlv6B9XTZ_DDgt8zKg99g&s"
            ),
            Service(
                service_name="Carpentry",
                service_price=250.0,
                service_time_required=180,
                service_description="Woodworking and furniture repair",
                image="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSC4tAahBBN-14dqNlv6B9XTZ_DDgt8zKg99g&s"
            ),
        ]

        db.session.add_all(services)

        # Add demo professionals
        professionals = [
            ServiceProfessional(
                name="Mike Johnson",
                mobile="5555555555",
                base_price="100",
                date_created=datetime.utcnow(),
                description="Experienced plumber",
                service_type="Plumbing",
                experience=5,
                approved=True,
                password="hashed_password_3"
            ),
            ServiceProfessional(
                name="Sara Connor",
                mobile="4444444444",
                base_price="150",
                date_created=datetime.utcnow(),
                description="Expert electrician",
                service_type="Electrical Repair",
                experience=8,
                approved=True,
                password="hashed_password_4"
            ),
            ServiceProfessional(
                name="Tom Hardy",
                mobile="7778889999",
                base_price="120",
                date_created=datetime.utcnow(),
                description="Professional cleaner",
                service_type="House Cleaning",
                experience=3,
                approved=True,
                password="hashed_password_7"
            ),
            ServiceProfessional(
                name="Emily Clarke",
                mobile="3334445555",
                base_price="180",
                date_created=datetime.utcnow(),
                description="Skilled carpenter",
                service_type="Carpentry",
                experience=10,
                approved=True,
                password="hashed_password_8"
            ),
        ]

        db.session.add_all(professionals)

        # Commit Customers, Services, and Professionals to the database
        db.session.commit()

        # Add demo service requests
        service_requests = [
            Service_Request(
                service_id=services[0].service_id,
                customer_id=customers[0].customer_id,
                professional_id=professionals[0].id,
                address="123 Elm Street, Springfield",
                price="150.0",
                date_of_request=datetime.now(),
                service_status="requested"
            ),
            Service_Request(
                service_id=services[1].service_id,
                customer_id=customers[1].customer_id,
                professional_id=professionals[1].id,
                address="456 Oak Avenue, Metropolis",
                price="200.0",
                date_of_request=datetime.now(),
                service_status="accepted"
            ),
            Service_Request(
                service_id=services[2].service_id,
                customer_id=customers[2].customer_id,
                professional_id=professionals[2].id,
                address="789 Pine Street, Gotham",
                price="100.0",
                date_of_request=datetime.now(),
                service_status="completed"
            ),
            Service_Request(
                service_id=services[3].service_id,
                customer_id=customers[3].customer_id,
                professional_id=professionals[3].id,
                address="101 Maple Drive, Star City",
                price="250.0",
                date_of_request=datetime.now(),
                service_status="in-progress"
            ),
        ]

        db.session.add_all(service_requests)

        # Commit Service Requests to the database
        db.session.commit()

        print("Demo data populated successfully!")

if __name__ == "__main__":
    populate_demo_data()
