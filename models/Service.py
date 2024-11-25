# Service - It refers to the type of service that the customer is looking for e.g AC servicing, plumbing etc.
from app import db


class Service(db.Model):
    __tablename__ = 'services'  # Change to plural to follow convention

    service_id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(100), nullable=False, unique=True)
    service_price = db.Column(db.Float, nullable=False)
    service_time_required = db.Column(db.Integer, nullable=True)  # time in minutes
    service_description = db.Column(db.Text, nullable=True)
    image = db.Column(db.LargeBinary, nullable=True)  # You might consider using a URL to an image instead

    def __repr__(self):
        return f"<Service(service_id={self.service_id}, service_name='{self.service_name}', service_price={self.service_price})>"

    @property
    def formatted_price(self):
        """Return the price formatted as a currency string."""
        return f"${self.service_price:.2f}"
