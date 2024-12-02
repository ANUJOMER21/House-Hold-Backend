import redis
import json
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models.Service_Request import Service_Request
from app import db
from Cache.cache_utils import cache_data,redis_client
# Create a Blueprint for service requests
service_request_bp = Blueprint('service_request_bp', __name__)

@service_request_bp.route('/service_requests', methods=['POST'])
@jwt_required()
def create_service_request():
    data = request.json
    new_request = Service_Request(
        service_id=data['service_id'],
        customer_id=data['customer_id'],
        professional_id=data['professional_id'],
        address=data['address'],
        service_status=data.get('service_status', 'requested'),  # Default status
        remarks=data.get('remarks'),
        date_of_request=datetime.utcnow()
    )
    db.session.add(new_request)
    db.session.commit()

    # Invalidate cache for all service requests
    redis_client.delete("all_service_requests")

    return jsonify({"message": "Service Request created", "id": new_request.id}), 201

@service_request_bp.route('/service_requests', methods=['GET'])
@jwt_required()
def get_service_requests():
    def fetch_service_requests():
        requests = Service_Request.query.all()
        return [{
            'id': r.id,
            'service_id': r.service_id,
            'customer_id': r.customer_id,
            'customer_name': r.customer.customer_name,
            'professional_id': r.professional_id,
            'professional_name': r.professional.name,
            'address': r.address,
            'date_of_request': r.date_of_request.isoformat(),
            'date_of_completion': r.date_of_completion.isoformat() if r.date_of_completion else None,
            'service_status': r.service_status,
            'remarks': r.remarks
        } for r in requests]

    service_requests = cache_data("all_service_requests", fetch_service_requests, expiration=300)
    return jsonify(fetch_service_requests()), 200

@service_request_bp.route('/service_requests/<int:id>', methods=['GET'])
@jwt_required()
def get_service_request(id):
    def fetch_service_request():
        service_request = Service_Request.query.get_or_404(id)
        return {
            'id': service_request.id,
            'service_id': service_request.service_id,
            'customer_id': service_request.customer_id,
            'professional_id': service_request.professional_id,
            'address': service_request.address,
            'date_of_request': service_request.date_of_request.isoformat(),
            'date_of_completion': service_request.date_of_completion.isoformat() if service_request.date_of_completion else None,
            'service_status': service_request.service_status,
            'remarks': service_request.remarks
        }

    service_request_key = f"service_request_{id}"
    service_request = cache_data(service_request_key, fetch_service_request, expiration=300)
    return jsonify(service_request), 200

@service_request_bp.route('/service_requests/<int:id>', methods=['PUT'])
@jwt_required()
def update_service_request(id):
    service_request = Service_Request.query.get_or_404(id)
    data = request.json

    service_request.service_id = data.get('service_id', service_request.service_id)
    service_request.customer_id = data.get('customer_id', service_request.customer_id)
    service_request.professional_id = data.get('professional_id', service_request.professional_id)
    service_request.address = data.get('address', service_request.address)
    service_request.date_of_completion = data.get('date_of_completion', service_request.date_of_completion)
    service_request.service_status = data.get('service_status', service_request.service_status)
    service_request.remarks = data.get('remarks', service_request.remarks)

    db.session.commit()

    # Invalidate cache for all service requests and specific service request
    redis_client.delete("all_service_requests")
    redis_client.delete(f"service_request_{id}")

    return jsonify({"message": "Service Request updated"}), 200

@service_request_bp.route('/service_requests/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_service_request(id):
    service_request = Service_Request.query.get_or_404(id)
    db.session.delete(service_request)
    db.session.commit()

    # Invalidate cache for all service requests and specific service request
    redis_client.delete("all_service_requests")
    redis_client.delete(f"service_request_{id}")

    return jsonify({"message": "Service Request deleted"}), 204
