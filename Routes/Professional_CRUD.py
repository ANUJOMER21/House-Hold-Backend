import redis
import json
from flask import Blueprint, request, jsonify
from models.ServiceProfessional import ServiceProfessional
from database import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from Cache.cache_utils import cache_data
from Cache.cache_utils import redis_client


# Create a Blueprint for service professionals
service_professional_bp = Blueprint('service_professional_bp', __name__)


# Create a service professional
@service_professional_bp.route('/service_professionals', methods=['POST'])
@jwt_required()
def create_service_professional():
    try:
        data = request.json

        # Input validation
        required_fields = ['base_price', 'name', 'mobile', 'service_type', 'experience', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        new_service_professional = ServiceProfessional(
            base_price=data['base_price'],
            name=data['name'],
            mobile=data['mobile'],
            description=data.get('description'),
            service_type=data['service_type'],
            experience=data['experience'],
            password=data['password'],  # Note: Store securely in real implementations
            approved=False
        )
        db.session.add(new_service_professional)
        db.session.commit()

        # Invalidate the cached list
        redis_client.delete("all_service_professionals")

        return jsonify({"message": "Service Professional created", "id": new_service_professional.id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Get all service professionals
@service_professional_bp.route('/service_professionals', methods=['GET'])
@jwt_required()
def get_service_professionals():
    try:
        def fetch_all_service_professionals():
            service_professionals = ServiceProfessional.query.all()
            return [{
                'id': sp.id,
                'name': sp.name,
                'mobile': sp.mobile,
                'date_created': sp.date_created.isoformat(),
                'description': sp.description,
                'base_price': sp.base_price,
                'service_type': sp.service_type,
                'experience': sp.experience,
                'approved': sp.approved
            } for sp in service_professionals]

        cached_result = cache_data("all_service_professionals", fetch_all_service_professionals, expiration=300)
        return jsonify(fetch_all_service_professionals()), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Get a specific service professional by their ID (JWT identity)
@service_professional_bp.route('/service_professionals_by_id', methods=['GET'])
@jwt_required()
def get_service_professional():
    try:
        id = get_jwt_identity()

        def fetch_service_professional():
            sp = ServiceProfessional.query.get_or_404(id)
            return {
                'id': sp.id,
                'name': sp.name,
                'mobile': sp.mobile,
                'base_price': sp.base_price,
                'date_created': sp.date_created.isoformat(),
                'description': sp.description,
                'service_type': sp.service_type,
                'experience': sp.experience,
                'approved': sp.approved
            }

        cached_result = cache_data(f"service_professional_{id}", fetch_service_professional, expiration=300)
        return jsonify(cached_result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Update a service professional's information
@service_professional_bp.route('/service_professionals', methods=['PUT'])
@jwt_required()
def update_service_professional():
    try:
        id = get_jwt_identity()
        service_professional = ServiceProfessional.query.get_or_404(id)
        data = request.json

        # Update fields only if they are provided
        service_professional.name = data.get('name', service_professional.name)
        service_professional.description = data.get('description', service_professional.description)
        service_professional.experience = data.get('experience', service_professional.experience)
        service_professional.base_price = data.get('base_price', service_professional.base_price)

        db.session.commit()

        # Invalidate cache for the specific service professional and list
        redis_client.delete(f"service_professional_{id}")
        redis_client.delete("all_service_professionals")

        return jsonify({"message": "Service Professional updated"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Delete a service professional by ID
@service_professional_bp.route('/service_professionals/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_service_professional(id):
    try:
        service_professional = ServiceProfessional.query.get_or_404(id)
        db.session.delete(service_professional)
        db.session.commit()

        # Invalidate cache for the specific service professional and list
        redis_client.delete(f"service_professional_{id}")
        redis_client.delete("all_service_professionals")

        return jsonify({"message": "Service Professional deleted"}), 204

    except Exception as e:
        return jsonify({"error": str(e)}), 500
