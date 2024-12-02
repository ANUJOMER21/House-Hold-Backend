import os

import matplotlib
from flask import Blueprint, jsonify, Response, send_from_directory
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import func
from datetime import datetime, timedelta
from models import Customer, Service, Service_Request, ServiceProfessional
from app import db
import matplotlib.pyplot as plt
from Graph import graphs
import io

matplotlib.use('Agg')
# Create a blueprint for analysis routes
analysis_blueprint = Blueprint('analysis', __name__)

IMAGE_FOLDER = "Graph/generated_images"
base_image_url = f"http://127.0.0.1:5000/images/"


# API to get an admin's graph
@analysis_blueprint.route('/api/admin/graph', methods=['GET'])
@jwt_required()
def get_admin_graph():
    try:
        admin_revenue_by_service = graphs.admin_revenue_by_service()
        admin_professional_activity_levels = graphs.admin_professional_activity_levels()
        admin_requests_by_status = graphs.admin_requests_by_status()
        admin_top_cities = graphs.admin_top_cities()

        return jsonify({
            "admin_revenue_by_service": base_image_url + admin_revenue_by_service,
            "admin_professional_activity_levels": base_image_url + admin_professional_activity_levels,
            "admin_requests_by_status": base_image_url + admin_requests_by_status,
            "admin_top_cities": base_image_url + admin_top_cities
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@analysis_blueprint.route('/api/user/graph', methods=['GET'])
@jwt_required()
def get_user_graph():
    try:
        id=get_jwt_identity()
        user_requests_by_status = graphs.user_requests_by_status(id)
        user_spending_over_time = graphs.user_spending_over_time(id)
        user_service_usage = graphs.user_service_usage(id)

        return jsonify({
            "user_requests_by_status": base_image_url + user_requests_by_status,
            "user_spending_over_time": base_image_url + user_spending_over_time,
            "user_service_usage": base_image_url + user_service_usage,

        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analysis_blueprint.route('/api/prof/graph', methods=['GET'])
@jwt_required()
def get_prof_graph():
    try:
        id=get_jwt_identity()
        professional_earnings_over_time = graphs.professional_earnings_over_time(id)
        professional_monthly_jobs = graphs.professional_daily_jobs(id)
        professional_completed_pending_jobs = graphs.professional_completed_pending_jobs_daily(id)

        return jsonify({
            "professional_earnings_over_time": base_image_url + professional_earnings_over_time,
            "professional_monthly_jobs": base_image_url + professional_monthly_jobs,
            "professional_completed_pending_jobs": base_image_url + professional_completed_pending_jobs,

        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@analysis_blueprint.route('/api/graph', methods=['GET'])
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
    return send_from_directory(IMAGE_FOLDER, filename)
