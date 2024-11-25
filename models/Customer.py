from app import db
from sqlalchemy.orm import validates
import re


class Customer(db.Model):
    __tablename__ = 'customers'  # Changed to plural to follow convention

    customer_id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(120), unique=True, nullable=False)
    customer_phone_number = db.Column(db.String(15),  nullable=True)
    customer_address = db.Column(db.String(255), nullable=True)
    customer_status = db.Column(db.String(255),nullable=True)
    customer_password=db.Column(db.String(255),nullable=False)

    def __repr__(self):
        return f"<Customer(customer_id={self.customer_id}, customer_name='{self.customer_name}', customer_email='{self.customer_email}')>"

    @validates('customer_email')
    def validate_email(self, key, email):
        """Validate email format."""
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            raise ValueError("Invalid email format")
        return email

    @validates('customer_phone_number')
    def validate_phone_number(self, key, phone_number):
        """Validate phone number format."""
        if phone_number and not re.match(r'^\+?1?\d{9,15}$', phone_number):
            raise ValueError("Invalid phone number format")
        return phone_number
