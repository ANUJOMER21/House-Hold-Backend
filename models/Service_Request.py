# Service - It refers to the type of service that the customer is looking for e.g AC servicing, plumbing etc.
from app import db


class Service_Request(db.Model):
    __tablename__ = 'service_requests'  # It's a good practice to specify the table name

    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.service_id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('service_professionals.id'), nullable=False)
    address = db.Column(db.String, nullable=False)
    date_of_request = db.Column(db.DateTime, nullable=False)
    date_of_completion = db.Column(db.DateTime, nullable=True)
    service_status = db.Column(db.String(20), nullable=False, default="requested")  # requested, accepted, closed
    remarks = db.Column(db.String(255), nullable=True)

    # Relationships
    service = db.relationship('Service', backref=db.backref('service_requests', lazy=True))
    customer = db.relationship('Customer', backref=db.backref('service_requests', lazy=True))
    professional = db.relationship('ServiceProfessional', backref=db.backref('service_requests', lazy=True))

    def __repr__(self):
        return f"<ServiceRequest(id={self.id}, status={self.service_status})>"
