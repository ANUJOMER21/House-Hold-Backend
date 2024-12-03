from database import db

class Review(db.Model):
    __tablename__ ='review'

    id=db.Column(db.Integer,primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.service_id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('service_professionals.id'), nullable=False)
    review=db.Column(db.String,nullable=True)
    rating=db.Column(db.Double)
    # Relationships
    service = db.relationship('Service', backref=db.backref('review', lazy=True))
    customer = db.relationship('Customer', backref=db.backref('review', lazy=True))
    professional = db.relationship('ServiceProfessional', backref=db.backref('review', lazy=True))

    def __repr__(self):
        return f"<Review(id={self.id}, review={self.review}, rating={self.rating})>"


