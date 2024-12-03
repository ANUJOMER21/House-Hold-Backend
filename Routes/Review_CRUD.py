from flask import Blueprint, request, jsonify
from models.Review import Review
from database import db

review_bp = Blueprint('review_bp', __name__)


# Create a review
@review_bp.route('/reviews', methods=['POST'])
def create_review():
    data = request.json
    try:
        new_review = Review(
            service_id=data['service_id'],
            customer_id=data['customer_id'],
            professional_id=data['professional_id'],
            review=data.get('review', ''),
            rating=data.get('rating', 0.0)
        )
        db.session.add(new_review)
        db.session.commit()
        return jsonify({"message": "Review created", "review_id": new_review.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


# Get all reviews or filter by service_id, customer_id, or professional_id
@review_bp.route('/reviews', methods=['GET'])
def get_reviews():
    service_id = request.args.get('service_id')
    customer_id = request.args.get('customer_id')
    professional_id = request.args.get('professional_id')

    query = Review.query
    if service_id:
        query = query.filter_by(service_id=service_id)
    if customer_id:
        query = query.filter_by(customer_id=customer_id)
    if professional_id:
        query = query.filter_by(professional_id=professional_id)

    reviews = query.all()
    reviews_data = [{
        "id": review.id,
        "service_id": review.service_id,
        "customer_id": review.customer_id,
        "professional_id": review.professional_id,
        "review": review.review,
        "rating": review.rating
    } for review in reviews]

    return jsonify(reviews_data), 200


# Get a specific review by id
@review_bp.route('/reviews/<int:review_id>', methods=['GET'])
def get_review(review_id):
    review = Review.query.get_or_404(review_id)
    review_data = {
        "id": review.id,
        "service_id": review.service_id,
        "customer_id": review.customer_id,
        "professional_id": review.professional_id,
        "review": review.review,
        "rating": review.rating
    }
    return jsonify(review_data), 200


# Update a review
@review_bp.route('/reviews/<int:review_id>', methods=['PATCH'])
def update_review(review_id):
    data = request.json
    review = Review.query.get_or_404(review_id)
    if 'review' in data:
        review.review = data['review']
    if 'rating' in data:
        review.rating = data['rating']

    db.session.commit()
    return jsonify({"message": "Review updated", "review_id": review.id}), 200


# Delete a review
@review_bp.route('/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    return jsonify({"message": "Review deleted", "review_id": review.id}), 200
