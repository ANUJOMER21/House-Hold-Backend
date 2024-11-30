from flask import Blueprint, request, jsonify
from models import Customer
from app import db
from models.Customer import Customer
from flask_jwt_extended import jwt_required, get_jwt_identity

# Create a Blueprint for customers
customer_bp = Blueprint('customer_bp', __name__)


@customer_bp.route('/customers', methods=['POST'])
@jwt_required()
def create_customer():
    data = request.json
    new_customer = Customer(
        customer_name=data['customer_name'],
        customer_email=data['customer_email'],
        customer_phone_number=data.get('customer_phone_number'),
        customer_address=data.get('customer_address'),
        customer_password=data.get('customer_password'),
        customer_status="activate"
    )
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"message": "Customer_Model created", "customer_id": new_customer.customer_id}), 201


@customer_bp.route('/customers', methods=['GET'])
@jwt_required()
def get_customers():
    customers = Customer.query.all()
    return jsonify([{
        'customer_id': c.customer_id,
        'customer_name': c.customer_name,
        'customer_email': c.customer_email,
        'customer_phone_number': c.customer_phone_number,
        'customer_address': c.customer_address,
        'customer_status':c.customer_status
    } for c in customers]), 200


@customer_bp.route('/customers_one', methods=['GET'])
@jwt_required()
def get_customer():
    customer_id = get_jwt_identity()
    Customer_Model = Customer.query.get_or_404(customer_id)
    return jsonify({
        'customer_id': Customer_Model.customer_id,
        'customer_name': Customer_Model.customer_name,
        'customer_email': Customer_Model.customer_email,
        'customer_phone_number': Customer_Model.customer_phone_number,
        'customer_address': Customer_Model.customer_address,
        'customer_status':Customer_Model.customer_status
    }), 200


@customer_bp.route('/customers', methods=['PUT'])
@jwt_required()
def update_customer():
    customer_id = get_jwt_identity()
    Customer_Model = Customer.query.get_or_404(customer_id)
    data = request.json

    Customer_Model.customer_name = data.get('customer_name', Customer_Model.customer_name)
    Customer_Model.customer_email = data.get('customer_email', Customer_Model.customer_email)
    Customer_Model.customer_phone_number = data.get('customer_phone_number', Customer_Model.customer_phone_number)
    Customer_Model.customer_address = data.get('customer_address', Customer_Model.customer_address)

    db.session.commit()
    return jsonify({"message": "Customer_Model updated"}), 200


@customer_bp.route('/customers/<int:customer_id>', methods=['DELETE'])
@jwt_required()
def delete_customer(customer_id):
    Customer_Model = Customer.query.get_or_404(customer_id)
    db.session.delete(Customer_Model)
    db.session.commit()
    return jsonify({"message": "Customer_Model deleted"}), 204
