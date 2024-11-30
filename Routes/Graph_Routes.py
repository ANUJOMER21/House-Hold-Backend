import os

import matplotlib
from flask import Blueprint, jsonify, Response, send_from_directory
from sqlalchemy import func
from datetime import datetime, timedelta
from models import Customer, Service, Service_Request, ServiceProfessional
from app import db
import matplotlib.pyplot as plt
import io
matplotlib.use('Agg')
# Create a blueprint for analysis routes
analysis_blueprint = Blueprint('analysis', __name__)


@analysis_blueprint.route('/api/analysis/customers', methods=['GET'])
def customer_analysis():
    active_customers = db.session.query(func.count(Customer.customer_id)).filter(
        Customer.customer_status == "active").scalar()
    total_customers = db.session.query(func.count(Customer.customer_id)).scalar()
    new_customers_by_month = db.session.query(func.date_trunc('month', Customer.date_created).label("month"),
                                              func.count().label("count")).group_by("month").all()
    return jsonify({
        'active_customers': active_customers,
        'total_customers': total_customers,
        'new_customers_by_month': [{'month': month, 'count': count} for month, count in new_customers_by_month]
    })


@analysis_blueprint.route('/api/analysis/services', methods=['GET'])
def service_analysis():
    total_services = db.session.query(func.count(Service.service_id)).scalar()
    average_price = db.session.query(func.avg(Service.service_price)).scalar()
    services_by_type = db.session.query(Service.service_name, func.count(Service.service_id)).group_by(
        Service.service_name).all()
    return jsonify({
        'total_services': total_services,
        'average_price': average_price,
        'services_by_type': [{'service_name': name, 'count': count} for name, count in services_by_type]
    })


@analysis_blueprint.route('/api/analysis/service_requests', methods=['GET'])
def service_request_analysis():
    total_requests = db.session.query(func.count(Service_Request.id)).scalar()
    completed_requests = db.session.query(func.count(Service_Request.id)).filter(
        Service_Request.service_status == "closed").scalar()
    completion_rate = completed_requests / total_requests if total_requests > 0 else 0
    requests_by_month = db.session.query(func.date_trunc('month', Service_Request.date_of_request).label("month"),
                                         func.count().label("count")).group_by("month").all()
    return jsonify({
        'total_requests': total_requests,
        'completed_requests': completed_requests,
        'completion_rate': completion_rate,
        'requests_by_month': [{'month': month, 'count': count} for month, count in requests_by_month]
    })


@analysis_blueprint.route('/api/analysis/service_professionals', methods=['GET'])
def service_professional_analysis():
    total_professionals = db.session.query(func.count(ServiceProfessional.id)).scalar()
    professionals_by_type = db.session.query(ServiceProfessional.service_type,
                                             func.count(ServiceProfessional.id)).group_by(
        ServiceProfessional.service_type).all()
    average_experience = db.session.query(func.avg(ServiceProfessional.experience)).scalar()
    return jsonify({
        'total_professionals': total_professionals,
        'professionals_by_type': [{'service_type': service_type, 'count': count} for service_type, count in
                                  professionals_by_type],
        'average_experience': average_experience
    })


@analysis_blueprint.route('/api/analysis/monthly_revenue', methods=['GET'])
def monthly_revenue_analysis():
    revenue_by_month = db.session.query(
        func.date_trunc('month', Service_Request.date_of_completion).label("month"),
        func.sum(Service.service_price).label("total_revenue")
    ).join(Service, Service.service_id == Service_Request.service_id
           ).filter(Service_Request.service_status == "closed"
                    ).group_by("month").all()
    return jsonify({
        'revenue_by_month': [{'month': month, 'total_revenue': revenue} for month, revenue in revenue_by_month]
    })


@analysis_blueprint.route('/api/analysis/top_services', methods=['GET'])
def top_services_analysis():
    top_services = db.session.query(Service.service_name, func.count(Service_Request.id).label("request_count")
                                    ).join(Service_Request, Service_Request.service_id == Service.service_id
                                           ).group_by(Service.service_name
                                                      ).order_by(func.count(Service_Request.id).desc()).limit(5).all()
    return jsonify({
        'top_services': [{'service_name': name, 'request_count': count} for name, count in top_services]
    })


@analysis_blueprint.route('/api/analysis/customer_retention', methods=['GET'])
def customer_retention_analysis():
    repeat_customers = db.session.query(Service_Request.customer_id
                                        ).group_by(Service_Request.customer_id
                                                   ).having(func.count(Service_Request.id) > 1).count()
    total_customers = db.session.query(func.count(Customer.customer_id)).scalar()
    retention_rate = (repeat_customers / total_customers) * 100 if total_customers > 0 else 0
    return jsonify({
        'repeat_customers': repeat_customers,
        'total_customers': total_customers,
        'retention_rate': retention_rate
    })


@analysis_blueprint.route('/api/analysis/service_popularity_over_time', methods=['GET'])
def service_popularity_over_time():
    popularity = db.session.query(
        func.date_trunc('month', Service_Request.date_of_request).label("month"),
        Service.service_name,
        func.count(Service_Request.id).label("request_count")
    ).join(Service, Service.service_id == Service_Request.service_id
           ).group_by("month", Service.service_name
                      ).order_by("month").all()
    return jsonify({
        'popularity': [{'month': month, 'service_name': service_name, 'request_count': request_count}
                       for month, service_name, request_count in popularity]
    })


@analysis_blueprint.route('/api/analysis/service_request_status', methods=['GET'])
def service_request_status_distribution():
    status_distribution = db.session.query(
        Service_Request.service_status,
        func.count(Service_Request.id).label("count")
    ).group_by(Service_Request.service_status).all()
    return jsonify({
        'status_distribution': [{'status': status, 'count': count} for status, count in status_distribution]
    })


@analysis_blueprint.route('/api/analysis/average_completion_time', methods=['GET'])
def average_completion_time():
    completion_time = db.session.query(
        Service.service_name,
        func.avg(
            func.extract('epoch', Service_Request.date_of_completion - Service_Request.date_of_request) / 3600).label(
            "avg_hours")
    ).join(Service, Service.service_id == Service_Request.service_id
           ).filter(Service_Request.service_status == "closed"
                    ).group_by(Service.service_name).all()
    return jsonify({
        'average_completion_time': [{'service_name': service_name, 'avg_hours': avg_hours} for service_name, avg_hours
                                    in completion_time]
    })


@analysis_blueprint.route('/api/analysis/professional_approval_status', methods=['GET'])
def professional_approval_status():
    approval_status = db.session.query(
        ServiceProfessional.approved,
        func.count(ServiceProfessional.id).label("count")
    ).group_by(ServiceProfessional.approved).all()
    return jsonify({
        'approval_status': [{'approved': approved, 'count': count} for approved, count in approval_status]
    })


@analysis_blueprint.route('/api/analysis/service_revenue_contribution', methods=['GET'])
def service_revenue_contribution():
    revenue_contribution = db.session.query(
        Service.service_name,
        func.sum(Service.service_price).label("total_revenue")
    ).join(Service_Request, Service.service_id == Service_Request.service_id
           ).filter(Service_Request.service_status == "closed"
                    ).group_by(Service.service_name).all()
    return jsonify({
        'revenue_contribution': [{'service_name': service_name, 'total_revenue': revenue} for service_name, revenue in
                                 revenue_contribution]
    })


@analysis_blueprint.route('/api/analysis/top_professionals', methods=['GET'])
def top_professionals():
    top_professionals = db.session.query(
        ServiceProfessional.name,
        func.count(Service_Request.id).label("completed_requests")
    ).join(Service_Request, Service_Request.professional_id == ServiceProfessional.id
           ).filter(Service_Request.service_status == "closed"
                    ).group_by(ServiceProfessional.name
                               ).order_by(func.count(Service_Request.id).desc()).limit(5).all()
    return jsonify({
        'top_professionals': [{'name': name, 'completed_requests': completed_requests} for name, completed_requests in
                              top_professionals]
    })


@analysis_blueprint.route('/api/analysis/inactive_customers', methods=['GET'])
def inactive_customers():
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    inactive_customers = db.session.query(Customer.customer_id, Customer.customer_name
                                          ).outerjoin(Service_Request,
                                                      Service_Request.customer_id == Customer.customer_id
                                                      ).filter(
        (Service_Request.date_of_request < six_months_ago) | (Service_Request.date_of_request == None)
        ).all()
    return jsonify({
        'inactive_customers': [{'customer_id': customer_id, 'customer_name': customer_name} for
                               customer_id, customer_name in inactive_customers]
    })



@analysis_blueprint.route('/api/graph',methods=['GET'])
def get_graph():
    IMAGE_FOLDER = "generated_images"
    os.makedirs(IMAGE_FOLDER, exist_ok=True)
    try:
        # Create a sample plot
        plt.figure(figsize=(6, 4))
        plt.plot([1, 2, 3, 4], [10, 20, 25, 30], label="Sample Line")
        plt.xlabel("X-axis")
        plt.ylabel("Y-axis")
        plt.title("Sample Graph")
        plt.legend()

        # Save the plot to a file
        image_path = os.path.join(IMAGE_FOLDER, "graph.png")
        plt.savefig(image_path)
        plt.close()

        # Return the image URL
        image_url = f"http://127.0.0.1:5000/images/graph.png"
        return jsonify({"image_url": image_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@analysis_blueprint.route('/images/<filename>')
def serve_image(filename):
    IMAGE_FOLDER = "generated_images"
    return send_from_directory(IMAGE_FOLDER, filename)
