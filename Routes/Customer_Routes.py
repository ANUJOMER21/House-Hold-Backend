from flask import Blueprint, request, jsonify

from models.Service_Request import Service_Request
from models.Customer import Customer
from models.Service import Service
from models.Review import Review
from flask_jwt_extended import create_access_token, jwt_required
from app import db

customer_routes_bp = Blueprint('customer_routes_bp', __name__)


# Registration route
@customer_routes_bp.route('/customer/register', methods=['POST'])
def register_customer():
    data = request.json
    name = data.get('customer_name')
    email = data.get('customer_email')
    phone = data.get('customer_phone_number')
    address = data.get('customer_address')
    password = data.get('customer_password')  # Store in plain text (for demo purposes)

    if Customer.query.filter((Customer.customer_email == email) | (Customer.customer_phone_number == phone)).first():
        return jsonify({"message": "Customer with this email or phone already exists"}), 409

    new_customer = Customer(
        customer_name=name,
        customer_email=email,
        customer_phone_number=phone,
        customer_address=address,
        customer_password=password,
        customer_status="activate"
    )
    db.session.add(new_customer)
    db.session.commit()
    access_token = create_access_token(identity=new_customer.customer_id)
    return jsonify({"message": "Registration successful", "customer_id": new_customer.customer_id,"access_token": access_token}), 201


# Login route
@customer_routes_bp.route('/customer/login', methods=['POST'])
def login_customer():
    data = request.json
    email_or_phone = data.get('identifier')  # Can be email or phone
    password = data.get('customer_password')

    customer = Customer.query.filter(
        (Customer.customer_email == email_or_phone) | (Customer.customer_phone_number == email_or_phone)
    ).first()
    print(password)
    if not customer or customer.customer_password != password:
        return jsonify({"message": "Invalid credentials"}), 401
    access_token = create_access_token(identity=customer.customer_id)
    return jsonify({"message": "Login successful", "customer_id": customer.customer_id,"access_token": access_token}), 200


# View/Search Services
@customer_routes_bp.route('/services', methods=['GET'])
@jwt_required()
def get_services():
    query = request.args.get('query')
    if query:
        services = Service.query.filter(Service.service_name.ilike(f'%{query}%')).all()
    else:
        services = Service.query.all()

    return jsonify([{"service_id": s.service_id, "service_name": s.service_name} for s in services]), 200


# Close a service request
@customer_routes_bp.route('/customer/service_requests/<int:request_id>/complete', methods=['PATCH'])
@jwt_required()
def close_service_request(request_id):
    service_request = Service_Request.query.get_or_404(request_id)
    if service_request.status != "requested":
        return jsonify({"message": "Request cannot be closed"}), 400

    service_request.status = "complete"
    db.session.commit()
    return jsonify({"message": "Service request closed", "request_id": service_request.request_id}), 200




