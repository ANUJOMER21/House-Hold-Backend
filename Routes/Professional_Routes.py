from flask import Blueprint, request, jsonify
from models.ServiceProfessional import ServiceProfessional
from models.Service_Request import Service_Request
from app import db
from flask_jwt_extended import create_access_token, jwt_required

professional_bp = Blueprint('professional_bp', __name__)


# Registration route
@professional_bp.route('/professional/register', methods=['POST'])
def professional_register():
    data = request.json
    name = data.get('name')
    description = data.get('description')
    service_type = data.get('service_type')
    experience = data.get('experience')

    mobile = data.get('mobile')
    password = data.get('password')  # Store in plain text (not recommended for production)

    # Check if email or mobile already exists
    if ServiceProfessional.query.filter(
            (ServiceProfessional.mobile == mobile) | (ServiceProfessional.mobile == mobile)).first():
        return jsonify({"message": "Professional with this email or mobile already exists"}), 409

    # Create new professional with plain-text password
    new_professional = ServiceProfessional(
        name=name,
        description=description,
        service_type=service_type,
        experience=experience,
        mobile=mobile,
        approved=False,
        password=password  # Store in plain text (for educational/demo purposes)
    )
    db.session.add(new_professional)
    db.session.commit()
    access_token = create_access_token(identity=new_professional.id)
    return jsonify({"message": "Registration successful", "professional_id": new_professional.id, "access_token": access_token}), 201


# Login route with mobile or email
@professional_bp.route('/professional/login', methods=['POST'])
def professional_login():
    data = request.json
    identifier = data.get('mobile')  # Either email or mobile
    password = data.get('password')

    # Check if identifier is an email or mobile and find the professional
    professional = ServiceProfessional.query.filter(
        (ServiceProfessional.mobile == identifier)
    ).first()

    # If professional does not exist or password is incorrect
    if not professional or professional.password != password:
        return jsonify({"message": "Invalid credentials"}), 401
    access_token = create_access_token(identity=professional.id)
    return jsonify({"message": "Login successful", "professional_id": professional.id,"access_token": access_token}), 200


@professional_bp.route('/professional/service_requests/<int:request_id>/accept', methods=['PATCH'])
@jwt_required()
def accept_request(request_id):
    service_request = Service_Request.query.get_or_404(request_id)

    # Check if the request is already accepted or rejected
    if service_request.service_status != "requested":
        return jsonify({"message": f"Request already {service_request.service_status}"}), 400

    service_request.service_status = "accepted"
    db.session.commit()
    return jsonify({"message": "Request accepted", "request_id": service_request.id}), 200


# Route to reject a service request
@professional_bp.route('/professional/service_requests/<int:request_id>/reject', methods=['PATCH'])
@jwt_required()
def reject_request(request_id):
    service_request = Service_Request.query.get_or_404(request_id)

    # Check if the request is already accepted or rejected
    if service_request.service_status != "requested":
        return jsonify({"message": f"Request already {service_request.service_status}"}), 400

    service_request.service_status = "rejected"
    db.session.commit()
    return jsonify({"message": "Request rejected", "request_id": service_request.id}), 200
