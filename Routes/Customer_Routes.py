from datetime import datetime
from flask import Blueprint, request, jsonify
from models.ServiceProfessional import ServiceProfessional
from models.Service_Request import Service_Request
from models.Customer import Customer
from models.Service import Service
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from database import db
from Cache.cache_utils import cache_data  # Import the caching utility
import json

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
    return jsonify(
        {"message": "Login successful", "customer_id": customer.customer_id, "access_token": access_token}), 200



# Get services with partners
@customer_routes_bp.route('/customer/services_partner', methods=['GET'])
@jwt_required()
def get_services_with_partners():
    cache_key = "services_with_partners"

    def fetch_services_with_partners():
        services = Service.query.all()
        result = []
        for service in services:
            partners = ServiceProfessional.query.filter_by(service_type=service.service_name).all()
            partner_list = [{
                'partner_id': p.id,
                'name': p.name,
                'mobile': p.mobile,
                'base_price': p.base_price,
                'date_created': p.date_created.isoformat(),  # Convert datetime to ISO string
                'description': p.description,
                'experience': p.experience,
                'approved': p.approved
            } for p in partners]

            result.append({
                'service_id': service.service_id,
                'service_name': service.service_name,
                'service_price': service.service_price,
                'service_time_required': service.service_time_required,
                'service_description': service.service_description,
                'image': service.image,
                'partners': partner_list
            })
        return result

    # Cache the result
    response = cache_data(cache_key, fetch_services_with_partners, expiration=300)
    return jsonify(json.loads(response)), 200


# View/Search Services
@customer_routes_bp.route('/services_query', methods=['GET'])
@jwt_required()
def get_services():
    query = request.args.get('query')
    cache_key = f"services_query:{query}" if query else "all_services"

    def fetch_services():
        if query:
            services = Service.query.filter(Service.service_name.ilike(f'%{query}%')).all()
        else:
            services = Service.query.all()
        return [{"service_id": s.service_id, "service_name": s.service_name} for s in services]

    response = cache_data(cache_key, fetch_services, expiration=180)
    return jsonify(json.loads(response)), 200


# Close a service request (No caching needed as this modifies data)
# Close a service request
@customer_routes_bp.route('/customer/update_service_status', methods=['POST'])
@jwt_required()
def updaterequeststatus():
    data = request.json
    service_request_id = data.get('service_id')  # Either email or mobile
    status = data.get('status')
    remark= data.get('remarks')
    print(status)
    service_request = Service_Request.query.get_or_404(service_request_id)

    # Check if the request is already accepted or rejected


    if(status=="completed"):
         service_request.date_of_completion=datetime.utcnow()
    service_request.service_status = status
    service_request.remarks =remark
    db.session.commit()
    return jsonify({"message": "Request accepted", "request_id": service_request.id}), 200


@customer_routes_bp.route('/customer/add_service', methods=['POST'])
@jwt_required()
def customer_add_service():
    id = get_jwt_identity()
    data = request.json
    new_request = Service_Request(
        service_id=data['service_id'],
        customer_id=id,
        professional_id=data['professional_id'],
        address='address',
        price=data['price'],
        service_status='requested',  # Default status
        date_of_request=datetime.utcnow()
    )
    db.session.add(new_request)
    db.session.commit()
    db.session.close()
    return jsonify({"message": "Service Request created"})



# Get service requests by customer
@customer_routes_bp.route('/customer/get_service', methods=['GET'])
@jwt_required()
def get_service_requests_by_customer():
    try:
        # Query service requests by customer_id
        customer_id = get_jwt_identity()
        service_requests = db.session.query(Service_Request).filter_by(customer_id=customer_id).all()

        if not service_requests:
            return jsonify({"message": "No service requests found for the given customer ID"}), 404

        # Build response data
        response_data = []
        for request in service_requests:
            response_data.append({
                "service_request_id": request.id,
                "service_name": request.service.service_name,
                "service_description": request.service.service_description,
                "service_price": request.price,
                "address": request.address,
                "date_of_request": request.date_of_request.strftime('%Y-%m-%d %H:%M:%S') if request.date_of_request else None,
                "date_of_completion": request.date_of_completion.strftime('%Y-%m-%d %H:%M:%S') if request.date_of_completion else None,
                "service_status": request.service_status,
                "remarks": request.remarks,
                "professional": {
                    "name": request.professional.name,
                    "mobile": request.professional.mobile,
                    "service_type": request.professional.service_type,
                    "experience": request.professional.experience
                }
            })

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
