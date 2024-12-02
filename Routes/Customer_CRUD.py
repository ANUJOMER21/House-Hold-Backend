from flask import Blueprint, request, jsonify

from Cache.cache_utils import redis_client
from models import Customer
from app import db
from models.Customer import Customer
from flask_jwt_extended import jwt_required, get_jwt_identity
from Cache.cache_utils import cache_data  # Import the caching utility
import json

# Create a Blueprint for customers
customer_bp = Blueprint('customer_bp', __name__)


# Create a customer (No caching needed as this action modifies data)
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
    return jsonify({"message": "Customer created", "customer_id": new_customer.customer_id}), 201


# Get all customers
@customer_bp.route('/customers', methods=['GET'])
@jwt_required()
def get_customers():
    cache_key = "all_customers"

    # Function to fetch fresh data
    def fetch_customers():
        customers = Customer.query.all()
        return [{
            'customer_id': c.customer_id,
            'customer_name': c.customer_name,
            'customer_email': c.customer_email,
            'customer_phone_number': c.customer_phone_number,
            'customer_address': c.customer_address,
            'customer_status': c.customer_status
        } for c in customers]

    # Get data from cache or fetch fresh data
    response = cache_data(cache_key, fetch_customers, expiration=120)
    return jsonify(json.loads(response)), 200


# Get a single customer
@customer_bp.route('/customers_one', methods=['GET'])
@jwt_required()
def get_customer():
    customer_id = get_jwt_identity()
    cache_key = f"customer:{customer_id}"

    # Function to fetch fresh data
    def fetch_customer():
        customer = Customer.query.get_or_404(customer_id)
        return {
            'customer_id': customer.customer_id,
            'customer_name': customer.customer_name,
            'customer_email': customer.customer_email,
            'customer_phone_number': customer.customer_phone_number,
            'customer_address': customer.customer_address,
            'customer_status': customer.customer_status
        }

    # Get data from cache or fetch fresh data
    response = cache_data(cache_key, fetch_customer, expiration=60)
    return jsonify(json.loads(response)), 200


# Update a customer (Cache invalidation included)
@customer_bp.route('/customers', methods=['PUT'])
@jwt_required()
def update_customer():
    customer_id = get_jwt_identity()
    customer = Customer.query.get_or_404(customer_id)
    data = request.json

    # Update customer fields
    customer.customer_name = data.get('customer_name', customer.customer_name)
    customer.customer_email = data.get('customer_email', customer.customer_email)
    customer.customer_phone_number = data.get('customer_phone_number', customer.customer_phone_number)
    customer.customer_address = data.get('customer_address', customer.customer_address)

    db.session.commit()

    # Invalidate the cache for this customer
    cache_key = f"customer:{customer_id}"
    redis_client.delete(cache_key)

    return jsonify({"message": "Customer updated"}), 200


# Delete a customer (Cache invalidation included)
@customer_bp.route('/customers/<int:customer_id>', methods=['DELETE'])
@jwt_required()
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()

    # Invalidate the cache for this customer
    cache_key = f"customer:{customer_id}"
    redis_client.delete(cache_key)

    return jsonify({"message": "Customer deleted"}), 204
