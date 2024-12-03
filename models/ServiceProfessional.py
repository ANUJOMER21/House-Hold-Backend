from datetime import datetime

from database import db


class ServiceProfessional(db.Model):
    __tablename__ = 'service_professionals'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(10),nullable=False)
    base_price=db.Column(db.String(10),nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    description = db.Column(db.Text, nullable=True)
    service_type = db.Column(db.String(50), nullable=False)  # Example: 'Plumbing', 'Electrician', etc.
    experience = db.Column(db.Integer, nullable=False) # Years of experience
    approved = db.Column(db.Boolean, nullable=True)
    password = db.Column(db.String(256), nullable=False)


    def __repr__(self):
        return f"<ServiceProfessional(id={self.id}, name={self.name}, service_type={self.service_type})>"

    # Optional: validation for experience
    @property
    def experience_level(self):
        """Determines experience level based on years of experience."""
        if self.experience < 1:
            return "Beginner"
        elif 1 <= self.experience < 5:
            return "Intermediate"
        else:
            return "Expert"
