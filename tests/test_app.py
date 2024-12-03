import json
from datetime import datetime

import pytest
from main import create_app, db
from models.ServiceProfessional import ServiceProfessional
from models.Review import Review
from models.Service import Service
from models.Customer import Customer
from models.Service_Request import Service_Request


@pytest.fixture
def app():
    # Create a new app instance for testing
    app = create_app()

    # Create a tests client
    with app.app_context():
        db.create_all()  # Create the database schema
        yield app  # Provide the app to the tests
        db.drop_all()  # Clean up the database after tests


@pytest.fixture
def client(app):
    return app.test_client()


# Test for Customer model
def test_create_customer(client):
    response = client.post('/customers', json={
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "customer_phone_number": "+1234567890",
        "customer_address": "123 Elm St",
        "customer_password": "123456"
    })
    assert response.status_code == 201
    assert "message" in response.get_json()


def test_get_customers(client):
    response = client.get('/customers')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)  # Expect a list of customers


# Test for ServiceProfessional model
def test_create_service_professional(client):
    response = client.post('/service_professionals', json={
        "name": "Jane Smith",
        "mobile": "1234567890",
        "description": "Expert Plumber",
        "service_type": "Plumbing",
        "experience": 5,
        "password": "123456"
    })
    assert response.status_code == 201
    assert "message" in response.get_json()


def test_get_service_professionals(client):
    response = client.get('/service_professionals')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)  # Expect a list of service_professionals


# Test for Service model
def test_create_service(client):
    response = client.post('/services', json={
        "service_name": "Home Cleaning",
        "service_price": 100.0,
        "service_time_required": 90,
        "service_description": "Full home cleaning service."
    })
    assert response.status_code == 201
    assert "message" in response.get_json()


def test_get_services(client):
    response = client.get('/services')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)  # Expect a list of services


# Test for Service_Request model
def test_create_service_request(client):
    # Create a customer and a service professional first
    customer_response = client.post('/customers', json={
        "customer_name": "Alice Johnson",
        "customer_email": "alice@example.com",
        "customer_password": "123456"
    })
    professional_response = client.post('/service_professionals', json={
        "name": "Bob Builder",
        "service_type": "Construction",
        "experience": 10,
        "mobile": "1234567890",
        "password": "123456"
    })

    customer_id = customer_response.get_json()["customer_id"]
    professional_id = professional_response.get_json()["id"]

    response = client.post('/service_requests', json={
        "service_id": 1,  # Assuming this service exists
        "customer_id": 1,
        "professional_id": professional_id,
        "address": "456 Maple Ave",
        "remarks": "Looking for urgent service."
    })
    assert response.status_code == 201
    assert "message" in response.get_json()


def test_get_service_requests(client):
    response = client.get('/service_requests')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)  # Expect a list of service requests


def test_adminlogin(client):
    response = client.post('/admin/login', json={
        "username": "admin",
        "password": "admin_password"
    })
    assert response.status_code == 200
    assert "message" in response.get_json()


# Test approving a service professional
def test_approve_professional(client):
    # Admin login to get a JWT token
    admin_login_response = client.post('/admin/login', json={
        "username": "admin",
        "password": "admin_password"
    })
    assert admin_login_response.status_code == 200
    token = admin_login_response.get_json()["access_token"]

    # Create a ServiceProfessional instance
    professional_response = client.post('/service_professionals', json={
        "name": "Bob Builder",
        "service_type": "Construction",
        "experience": 10,
        "password": "123456",
        "mobile": "1234567890"
    })
    assert professional_response.status_code == 201
    professional_id = professional_response.get_json()["id"]

    # Approve the service professional with JWT authentication
    response = client.patch(
        f'/admin/professionals/{professional_id}/approve',
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Service professional approved"
    assert data["professional_id"] == professional_id

    # Verify the professional's status in the database
    updated_professional = ServiceProfessional.query.get(professional_id)
    assert updated_professional.approved is True


# Test creating a review
def test_create_review(client):
    service_id = "1"
    customer_id = "1"
    professional_id = "1"

    response = client.post('/reviews', json={
        "service_id": service_id,
        "customer_id": customer_id,
        "professional_id": professional_id,
        "review": "Great service!",
        "rating": 4.5
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "Review created"
    assert "review_id" in data


# Test retrieving all reviews
def test_get_reviews(client):
    response = client.get('/reviews')
    assert response.status_code == 200
    reviews = response.get_json()
    assert isinstance(reviews, list)


# Test retrieving a specific review by ID
def test_get_review_by_id(client):
    review = Review(service_id=1, customer_id=1, professional_id=1, review="Amazing!", rating=5.0)
    db.session.add(review)
    db.session.commit()

    response = client.get(f'/reviews/{review.id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data["review"] == "Amazing!"
    assert data["rating"] == 5.0


# Test updating a review
def test_update_review(client):
    review = Review(service_id=1, customer_id=1, professional_id=1, review="Good", rating=3.0)
    db.session.add(review)
    db.session.commit()

    response = client.patch(f'/reviews/{review.id}', json={
        "review": "Very good",
        "rating": 4.0
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Review updated"

    updated_review = Review.query.get(review.id)
    assert updated_review.review == "Very good"
    assert updated_review.rating == 4.0


# Test deleting a review
def test_delete_review(client):
    review = Review(service_id=1, customer_id=1, professional_id=1, review="Good", rating=3.0)
    db.session.add(review)
    db.session.commit()

    response = client.delete(f'/reviews/{review.id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Review deleted"

    # Verify the review was deleted from the database
    deleted_review = Review.query.get(review.id)
    assert deleted_review is None


# Test for ServiceProfessional registration
def test_professional_register(client):
    response = client.post('/professional/register', json={
        "name": "John Doe",
        "description": "Expert Plumber",
        "service_type": "Plumbing",
        "experience": 5,
        "mobile": "+1234567890",
        "password": "plainpassword"  # Use plain password for testing
    })
    assert response.status_code == 201
    assert "message" in response.get_json()

    # Check for duplicate registration
    duplicate_response = client.post('/professional/register', json={
        "name": "Jane Doe",
        "description": "Expert Electrician",
        "service_type": "Electrical",
        "experience": 4,
        "mobile": "+1234567890",  # Same mobile to trigger duplicate
        "password": "anotherpassword"
    })
    assert duplicate_response.status_code == 409
    assert "message" in duplicate_response.get_json()


# Test for ServiceProfessional login
def test_professional_login(client):
    # First, register a professional
    client.post('/professional/register', json={
        "name": "John Doe",
        "description": "Expert Plumber",
        "service_type": "Plumbing",
        "experience": 5,
        "mobile": "+1234567890",
        "password": "plainpassword"
    })

    # Now attempt to log in with correct credentials
    response = client.post('/professional/login', json={
        "mobile": "+1234567890",  # Using mobile for login
        "password": "plainpassword"
    })
    assert response.status_code == 200
    assert "message" in response.get_json()

    # Attempt to log in with incorrect credentials
    wrong_response = client.post('/professional/login', json={
        "identifier": "+1234567890",
        "password": "wrongpassword"
    })
    assert wrong_response.status_code == 401
    assert "message" in wrong_response.get_json()


# Test for accepting a service request
def test_accept_service_request(client):
    # Set up a professional and a service request
    registerprof=client.post('/professional/register', json={
        "name": "John Doe",
        "description": "Expert Plumber",
        "service_type": "Plumbing",
        "experience": 5,
        "mobile": "+1234567890",
        "password": "plainpassword"
    })
    assert registerprof.status_code == 201
    token = registerprof.get_json()["access_token"]
    # Create a service request for testing
    service_request = Service_Request(
        service_id="service_001",  # Assuming this ID exists
        customer_id="customer_123",  # Assuming this ID exists
        professional_id="professional_456",
        service_status="requested",  # Status must be "requested"
        address="123 Main St",
        remarks="Urgent plumbing needed.",
        date_of_request=datetime.utcnow()
    )
    db.session.add(service_request)
    db.session.commit()

    # Now accept the service request
    response = client.patch(f'/professional/service_requests/{service_request.id}/accept',
                            headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.get_json()["message"] == "Request accepted"


# Test for rejecting a service request
def test_reject_service_request(client):
    # Set up a professional and a service request
    registerprof= client.post('/professional/register', json={
        "name": "Jane Doe",
        "description": "Expert Electrician",
        "service_type": "Electrical",
        "experience": 4,
        "mobile": "+0987654321",
        "password": "plainpassword"
    })
    assert registerprof.status_code == 201
    token = registerprof.get_json()["access_token"]


    service_request = Service_Request(
        service_id="service_001",  # Assuming this ID exists
        customer_id="customer_123",  # Assuming this ID exists
        professional_id="professional_456",
        service_status="requested",  # Status must be "requested"
        address="123 Main St",
        remarks="Urgent plumbing needed.",
        date_of_request=datetime.utcnow()
    )
    db.session.add(service_request)
    db.session.commit()

    # Now reject the service request
    response = client.patch(f'/professional/service_requests/{service_request.id}/reject',
                            headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.get_json()["message"] == "Request rejected"

    # Try rejecting the same request again
    duplicate_reject_response = client.patch(f'/professional/service_requests/{service_request.id}/reject',
                                             headers={"Authorization": f"Bearer {token}"})
    assert duplicate_reject_response.status_code == 400
    assert "message" in duplicate_reject_response.get_json()


def test_customer_register(client):
    response = client.post('/customer/register', json={
        "customer_name": "Alice",
        "customer_email": "alice@example.com",
        "customer_phone_number": "+1234567890",
        "customer_address": "123 Street",
        "customer_password": "plainpassword"
    })
    assert response.status_code == 201
    assert "message" in response.get_json()

    # Test duplicate registration
    duplicate_response = client.post('/customer/register', json={
        "customer_name": "Bob",
        "customer_email": "alice@example.com",  # Duplicate email
        "customer_phone_number": "+0987654321",
        "customer_address": "456 Street",
        "customer_password": "anotherpassword"
    })
    assert duplicate_response.status_code == 409


def test_customer_login(client):
    client.post('/customer/register', json={
        "customer_name": "Alice",
        "customer_email": "alice@example.com",
        "customer_phone_number": "+1234567890",
        "customer_address": "123 Street",
        "customer_password": "plainpassword"
    })

    response = client.post('/customer/login', json={
        "identifier": "alice@example.com",
        "customer_password": "plainpassword"
    })
    assert response.status_code == 200
    assert "message" in response.get_json()

    # Test invalid credentials
    invalid_response = client.post('/customer/login', json={
        "identifier": "alice@example.com",
        "customer_password": "wrongpassword"
    })
    assert invalid_response.status_code == 401


def test_get_services(client):
    client.post('/customer/register', json={
        "customer_name": "Alice",
        "customer_email": "alice@example.com",
        "customer_phone_number": "+1234567890",
        "customer_address": "123 Street",
        "customer_password": "plainpassword"
    })

    # Add a service for testing
    service = Service(service_name="Plumbing Service"
                      , service_price=100,
                      service_description="Best plumbing service",
                      service_time_required="1 hour")
    db.session.add(service)
    db.session.commit()

    response = client.get('/services?query=Plumbing')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


if __name__ == "__main__":
    pytest.main()
