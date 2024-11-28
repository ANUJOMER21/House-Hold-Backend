from datetime import datetime

from flask import Blueprint, request, jsonify
from models.ServiceProfessional import ServiceProfessional
from models.Service_Request import Service_Request
from app import db
from flask_jwt_extended import create_access_token, jwt_required
from flask_jwt_extended import get_jwt_identity
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


@professional_bp.route('/professional/update_service_status', methods=['POST'])
@jwt_required()
def updaterequeststatus():
    data = request.json
    service_request_id = data.get('service_id')  # Either email or mobile
    status = data.get('status')
    service_request = Service_Request.query.get_or_404(service_request_id)

    # Check if the request is already accepted or rejected
    if service_request.service_status != "requested":
        return jsonify({"message": f"Request already {service_request.service_status}"}), 400

    if(status=="completed"):
         service_request.date_of_completion=datetime.utcnow()
    service_request.service_status = status
    db.session.commit()
    return jsonify({"message": "Request accepted", "request_id": service_request.id}), 200



@professional_bp.route('/professional/getcompletedrequest', methods=['GET'])
@jwt_required()
def get_complete_request():
    try:
        # Extract professional_id from JWT token
        professional_id = get_jwt_identity()

        if not professional_id:
            return jsonify({"error": "Unauthorized access"}), 401

        # Query the database for services with the given professional_id and completed status
        completed_services = Service_Request.query.filter_by(
            professional_id=professional_id, service_status='completed'
        ).all()

        # Convert the query results to a list of dictionaries (if needed for JSON response)
        completed_services_list = [
            {
               "id": service.id,
                "name": service.service_id,  # Example attribute
                "address":service.address,
                "date_of_request":service.date_of_request,
                "date_of_completion":service.date_of_completion,
                "service_status": service.service_status
            }
            for service in completed_services
        ]

        return jsonify({
            "completed_services": completed_services_list
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@professional_bp.route('/professional/getnoncompletedrequest', methods=['GET'])
@jwt_required()
def get_non_completed_request():
    try:
        # Extract professional_id from JWT token
        professional_id = get_jwt_identity()
        print(professional_id)
        if not professional_id:
            return jsonify({"error": "Unauthorized access"}), 401

        # Query the database for services with the given professional_id and non-completed status
        other_services = Service_Request.query.filter(
            Service_Request.professional_id == professional_id,
            Service_Request.service_status != 'completed'
        ).all()

        # Convert the query results to a list of dictionaries (if needed for JSON response)
        other_services_list = [
            {
                "id": service.id,
                "name": service.service_id,  # Example attribute
                "address":service.address,
                "date_of_request":service.date_of_request,
                "date_of_completion":service.date_of_completion,
                "service_status": service.service_status
            }
            for service in other_services
        ]

        return jsonify({
            "other_services": other_services_list
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



