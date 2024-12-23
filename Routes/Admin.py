from flask import Blueprint, request, jsonify, current_app

from models.ServiceProfessional import ServiceProfessional
from models.Customer import Customer
from database import db
from flask_jwt_extended import create_access_token


# Create a Blueprint for admin
admin_bp = Blueprint('admin_bp', __name__)
from flask_jwt_extended import jwt_required





@admin_bp.route('/admin/login', methods=['POST'])
def admin_login():
    print(current_app.config['ADMIN_PASSWORD'])
    data = request.json
    access_token = create_access_token(identity=data['username'])
    if (data['username'] == current_app.config['ADMIN_USERNAME'] and
            (current_app.config['ADMIN_PASSWORD'] == data['password'])):
        return jsonify({"message": "Login successful", "access_token": access_token}), 200
    return jsonify({"message": "Invalid credentials"}), 401


# Approve a service professional
@admin_bp.route('/admin/professionals/<int:professional_id>/approve', methods=['PATCH'])
@jwt_required()
def approve_professional(professional_id):
    professional = ServiceProfessional.query.get_or_404(professional_id)
    # Implement any additional verification checks here
    professional.approved = True  # Ensure this field exists in your model
    db.session.commit()
    return jsonify({"message": "Service professional approved", "professional_id": professional.id}), 200


@admin_bp.route('/admin/professionals/<int:professional_id>/block', methods=['PATCH'])
@jwt_required()
def block_professional(professional_id):
    professional = ServiceProfessional.query.get_or_404(professional_id)
    # Implement any additional verification checks here
    professional.approved = False  # Ensure this field exists in your model
    db.session.commit()
    return jsonify({"message": "Service professional approved", "professional_id": professional.id}), 200


@admin_bp.route('/admin/customer/<int:customer_id>/block', methods=['PATCH'])
@jwt_required()
def block_customer(customer_id):
    professional = Customer.query.get_or_404(customer_id)
    # Implement any additional verification checks here
    professional.customer_status = "Blocked"  # Ensure this field exists in your model
    db.session.commit()
    return jsonify({"message": "Service professional deactivate", "professional_id": professional.customer_id}), 200


@admin_bp.route('/admin/send_report')
@jwt_required()
def send_report():
    from main import service_export
    a=service_export.delay()

    return jsonify( {
            "Task_ID": a.id,
            "Task_State": a.state,
            "Task_Result": a.result
        }), 202
