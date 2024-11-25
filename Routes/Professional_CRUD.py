from flask import Blueprint, request, jsonify
from models.ServiceProfessional import ServiceProfessional
from app import db

# Create a Blueprint for service professionals
service_professional_bp = Blueprint('service_professional_bp', __name__)

@service_professional_bp.route('/service_professionals', methods=['POST'])
def create_service_professional():
    data = request.json
    new_service_professional = ServiceProfessional(
        name=data['name'],
        mobile=data['mobile'],
        description=data.get('description'),
        service_type=data['service_type'],
        experience=data['experience'],
        password=data['password'],

        approved=False
    )
    db.session.add(new_service_professional)
    db.session.commit()
    return jsonify({"message": "Service Professional created", "id": new_service_professional.id}), 201

@service_professional_bp.route('/service_professionals', methods=['GET'])
def get_service_professionals():
    service_professionals = ServiceProfessional.query.all()
    return jsonify([{
        'id': sp.id,
        'name': sp.name,
        'mobile': sp.mobile,
        'date_created': sp.date_created.isoformat(),
        'description': sp.description,
        'service_type': sp.service_type,
        'experience': sp.experience,
        'approved':sp.approved
    } for sp in service_professionals]), 200

@service_professional_bp.route('/service_professionals/<int:id>', methods=['GET'])
def get_service_professional(id):
    service_professional = ServiceProfessional.query.get_or_404(id)
    return jsonify({
        'id': service_professional.id,
        'name': service_professional.name,
        'mobile' : service_professional.mobile,
        'date_created': service_professional.date_created.isoformat(),
        'description': service_professional.description,
        'service_type': service_professional.service_type,
        'experience': service_professional.experience,

        'approved':service_professional.approved
    }), 200

@service_professional_bp.route('/service_professionals/<int:id>', methods=['PUT'])
def update_service_professional(id):
    service_professional = ServiceProfessional.query.get_or_404(id)
    data = request.json

    service_professional.name = data.get('name', service_professional.name)
    service_professional.description = data.get('description', service_professional.description)
    service_professional.service_type = data.get('service_type', service_professional.service_type)
    service_professional.experience = data.get('experience', service_professional.experience)

    db.session.commit()
    return jsonify({"message": "Service Professional updated"}), 200

@service_professional_bp.route('/service_professionals/<int:id>', methods=['DELETE'])
def delete_service_professional(id):
    service_professional = ServiceProfessional.query.get_or_404(id)
    db.session.delete(service_professional)
    db.session.commit()
    return jsonify({"message": "Service Professional deleted"}), 204
