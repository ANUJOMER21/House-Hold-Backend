from flask import Blueprint, request, jsonify
from models.Service import Service
from app import db
from flask_jwt_extended import jwt_required
# Create a Blueprint for services
service_bp = Blueprint('service_bp', __name__)

@service_bp.route('/services', methods=['POST'])
@jwt_required()
def create_service():
    data = request.json
    new_service = Service(
        service_name=data['service_name'],
        service_price=data['service_price'],
        service_time_required=data.get('service_time_required'),
        service_description=data.get('service_description'),
        image=data.get('image')  # Assuming image is sent as binary data
    )
    db.session.add(new_service)
    db.session.commit()

    return jsonify({"message": "Service created", "service_id": new_service.service_id}), 201

@service_bp.route('/services', methods=['GET'])
@jwt_required()
def get_services():
    services = Service.query.all()
    return jsonify([{
        'service_id': s.service_id,
        'service_name': s.service_name,
        'service_price': s.service_price,
        'service_time_required': s.service_time_required,
        'service_description': s.service_description,
        'image': s.image # Convert binary image to hex for JSON
    } for s in services]), 200
@service_bp.route('/services_unauth', methods=['GET'])

def get_services_un_auth():
    services = Service.query.all()
    return jsonify([{
        'service_id': s.service_id,
        'service_name': s.service_name,
        'service_price': s.service_price,
        'service_time_required': s.service_time_required,
        'service_description': s.service_description,
        'image': s.image # Convert binary image to hex for JSON
    } for s in services]), 200
@service_bp.route('/services/<int:service_id>', methods=['GET'])
@jwt_required()
def get_service(service_id):
    service = Service.query.get_or_404(service_id)
    return jsonify({
        'service_id': service.service_id,
        'service_name': service.service_name,
        'service_price': service.service_price,
        'service_time_required': service.service_time_required,
        'service_description': service.service_description,
        'image':  service.image   # Convert binary image to hex for JSON
    }), 200

@service_bp.route('/services/<int:service_id>', methods=['PUT'])
@jwt_required()
def update_service(service_id):
    service = Service.query.get_or_404(service_id)
    data = request.json

    service.service_name = data.get('service_name', service.service_name)
    service.service_price = data.get('service_price', service.service_price)
    service.service_time_required = data.get('service_time_required', service.service_time_required)
    service.service_description = data.get('service_description', service.service_description)
    service.image = data.get('image', service.image)  # Assuming image is sent as binary data

    db.session.commit()

    return jsonify({"message": "Service updated"}), 200

@service_bp.route('/services/<int:service_id>', methods=['DELETE'])
@jwt_required()
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()

    return jsonify({"message": "Service deleted"}), 204
