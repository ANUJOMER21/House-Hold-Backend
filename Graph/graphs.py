import matplotlib.pyplot as plt
import pandas as pd
import os
from datetime import datetime
from app import db, create_app
from models.Service_Request import Service_Request
from models.Customer import Customer
from models.ServiceProfessional import ServiceProfessional
from models.Service import Service

IMAGE_FOLDER = "Graph/generated_images"


# Create a folder for storing generated images if it doesn't exist
def create_generated_images_folder():
    folder_path = "generated_images"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path


# User Graphs
def user_spending_over_time(user_id):
    app = create_app()
    with app.app_context():
        spending = db.session.query(
            db.func.strftime('%Y-%m', Service_Request.date_of_request).label('month'),
            db.func.sum(Service_Request.price).label('total_spent')
        ).filter(Service_Request.customer_id == user_id).group_by('month').all()
        save_path = os.path.join(IMAGE_FOLDER, "user_spending_over_time.png")
        df = pd.DataFrame(spending, columns=['Month', 'Total Spent'])
        if not df.empty:
            df['Month'] = pd.to_datetime(df['Month'])
            df.set_index('Month').plot(kind='line', marker='o', legend=False, title='Your Spending Over Time')
            plt.ylabel('Total Spending ($)')
            plt.tight_layout()
            plt.savefig(save_path)
            plt.close()
    return os.path.basename(save_path)


def user_service_usage(user_id):
    app = create_app()
    with app.app_context():
        usage = db.session.query(Service.service_name, db.func.count(Service_Request.id).label('usage')) \
            .join(Service, Service.service_id == Service_Request.service_id) \
            .filter(Service_Request.customer_id == user_id) \
            .group_by(Service.service_name).all()
        save_path = os.path.join(IMAGE_FOLDER, "user_service_usage.png")

        df = pd.DataFrame(usage, columns=['Service', 'Usage'])
        if not df.empty:
            df.plot(kind='bar', x='Service', y='Usage', legend=False, title='Your Service Usage')
            plt.ylabel('Number of Requests')
            plt.xlabel('Service')
            plt.tight_layout()
            plt.savefig(save_path)
            plt.close()
    return os.path.basename(save_path)


def professional_earnings_over_time(pro_id):
    app = create_app()
    with app.app_context():
        # Query for total earnings grouped by day
        earnings = db.session.query(
            db.func.strftime('%m-%d', Service_Request.date_of_request).label('day'),
            db.func.sum(Service_Request.price).label('total_earned')
        ).filter(
            Service_Request.professional_id == pro_id,
            Service_Request.service_status == 'completed'
        ).group_by('day').all()

        if not earnings:
            print("No data available for the given professional.")
            return None

        # Convert the query result to a DataFrame
        df = pd.DataFrame(earnings, columns=['day', 'Total Earned'])
        print(df)
        # Check if DataFrame is empty
        if df.empty:
            print("No data to plot.")
            return None

        # Convert 'day' column to datetime format and plot
       # df['day'] = pd.to_datetime(df['day'], format='%m-%d')
        df.set_index('day').plot(kind='line', marker='o', legend=False, title='Earnings Over Time')
        plt.ylabel('Total Earnings ($)')
        plt.tight_layout()

        # Ensure the image folder exists
        if not os.path.exists(IMAGE_FOLDER):
            os.makedirs(IMAGE_FOLDER)

        # Save the plot to the file
        save_path = os.path.join(IMAGE_FOLDER, "professional_earnings_over_time.png")
        plt.savefig(save_path)
        plt.close()

        return os.path.basename(save_path)

def professional_daily_jobs(pro_id):
    app = create_app()
    with app.app_context():
        # Query for daily job counts
        jobs = db.session.query(
            db.func.strftime('%m-%d', Service_Request.date_of_request).label('day'),
            db.func.count(Service_Request.id).label('job_count')
        ).filter(Service_Request.professional_id == pro_id).group_by('day').all()

        save_path = os.path.join(IMAGE_FOLDER, "professional_daily_jobs.png")

        # Create a DataFrame
        df = pd.DataFrame(jobs, columns=['Day', 'Job Count'])

        if not df.empty:
            # Convert 'Day' to string to keep only 'MM-DD' format
            df.set_index('Day').plot(kind='bar', legend=False, title='Daily Jobs (MM-DD)')
            plt.ylabel('Job Count')
            plt.xlabel('Day (MM-DD)')
            plt.tight_layout()
            plt.savefig(save_path)
            plt.close()

        return os.path.basename(save_path)

def professional_completed_pending_jobs_daily(pro_id):
    app = create_app()
    with app.app_context():
        # Query for daily completed jobs
        completed_jobs = db.session.query(
            db.func.strftime('%m-%d', Service_Request.date_of_request).label('day'),
            db.func.count(Service_Request.id).label('completed_count')
        ).filter(
            Service_Request.professional_id == pro_id,
            Service_Request.service_status == 'completed'
        ).group_by('day').all()

        # Query for daily pending jobs
        pending_jobs = db.session.query(
            db.func.strftime('%m-%d', Service_Request.date_of_request).label('day'),
            db.func.count(Service_Request.id).label('pending_count')
        ).filter(
            Service_Request.professional_id == pro_id,
            Service_Request.service_status != 'completed'
        ).group_by('day').all()

        if not completed_jobs and not pending_jobs:
            print("No data available for the given professional.")
            return None

        # Convert to DataFrames
        completed_df = pd.DataFrame(completed_jobs, columns=['Day', 'Completed Count'])
        pending_df = pd.DataFrame(pending_jobs, columns=['Day', 'Pending Count'])

        # Merge DataFrames and fill missing values with 0
        df = pd.merge(completed_df, pending_df, on='Day', how='outer').fillna(0)
       # print(df)
        # Create the plot if DataFrame is not empty
        if not df.empty:
            df.set_index('Day').plot(kind='bar', title='Daily Completed and Pending Jobs (MM-DD)')
            plt.ylabel('Job Count')
            plt.xlabel('Day (MM-DD)')
            plt.tight_layout()

            # Ensure the image folder exists
            if not os.path.exists(IMAGE_FOLDER):
                os.makedirs(IMAGE_FOLDER)

            save_path = os.path.join(IMAGE_FOLDER, "professional_completed_pending_jobs_daily.png")
            plt.savefig(save_path)
            plt.close()

            return os.path.basename(save_path)
        else:
            print("No data available for the given professional.")
            return None



# Admin Graphs
def admin_revenue_by_service():
    app = create_app()
    with app.app_context():
        revenue = db.session.query(Service.service_name, db.func.sum(Service_Request.price).label('revenue')) \
            .join(Service, Service.service_id == Service_Request.service_id) \
            .group_by(Service.service_name).all()
        save_path = os.path.join(IMAGE_FOLDER, "admin_revenue_by_service.png")

        df = pd.DataFrame(revenue, columns=['Service', 'Revenue'])
        if not df.empty:
            df.plot(kind='bar', x='Service', y='Revenue', legend=False, title='Revenue by Service')
            plt.ylabel('Revenue ($)')
            plt.xlabel('Service')
            plt.tight_layout()
            plt.savefig(save_path)
            plt.close()
    return os.path.basename(save_path)


def admin_professional_activity_levels():
    app = create_app()
    with app.app_context():
        activity_levels = db.session.query(
            ServiceProfessional.approved,
            db.func.count(ServiceProfessional.id).label('count')
        ).group_by(ServiceProfessional.approved).all()
        save_path = os.path.join(IMAGE_FOLDER, "admin_professional_activity_levels.png")
        print("admin_professional_activity_levels")
        df = pd.DataFrame(activity_levels, columns=['Approved', 'Count'])
        df['Approved'] = df['Approved'].map({True: 'Active', False: 'Inactive'})
        if not df.empty:
            df.plot(kind='bar', x='Approved', y='Count', legend=False, title='Professional Activity Levels')
            plt.ylabel('Number of Professionals')
            plt.tight_layout()
            plt.savefig(save_path)
            plt.close()
    return os.path.basename(save_path)


def admin_requests_by_status():
    app = create_app()
    with app.app_context():
        statuses = db.session.query(
            Service_Request.service_status,
            db.func.count(Service_Request.id).label('count')
        ).group_by(Service_Request.service_status).all()
        save_path = os.path.join(IMAGE_FOLDER, "admin_requests_by_status.png")

        df = pd.DataFrame(statuses, columns=['Status', 'Count'])
        if not df.empty:
            df.plot(kind='bar', x='Status', y='Count', legend=False, title='Requests by Status')
            plt.ylabel('Number of Requests')
            plt.tight_layout()
            plt.savefig(save_path)
            plt.close()
    return os.path.basename(save_path)


def admin_top_cities():
    app = create_app()
    with app.app_context():
        cities = db.session.query(
            Service_Request.address,
            db.func.count(Service_Request.id).label('request_count')
        ).group_by(Service_Request.address).order_by(db.func.count(Service_Request.id).desc()).limit(10).all()
        save_path = os.path.join(IMAGE_FOLDER, "admin_top_cities.png")

        df = pd.DataFrame(cities, columns=['City', 'Request Count'])
        if not df.empty:
            df.plot(kind='bar', x='City', y='Request Count', legend=False, title='Top Cities by Requests')
            plt.ylabel('Number of Requests')
            plt.xlabel('City')
            plt.tight_layout()
            plt.savefig(save_path)
            plt.close()
    return os.path.basename(save_path)


def user_requests_by_status(user_id):
    app = create_app()
    with app.app_context():
        statuses = db.session.query(
            Service_Request.service_status,
            db.func.count(Service_Request.id).label('count')
        ).filter(Service_Request.customer_id == user_id).group_by(Service_Request.service_status).all()
        save_path = os.path.join(IMAGE_FOLDER, "user_requests_by_status.png")

        df = pd.DataFrame(statuses, columns=['Status', 'Count'])
        if not df.empty:
            df.plot(kind='pie', y='Count', labels=df['Status'], autopct='%1.1f%%', legend=False,
                    title='Requests by Status')
            plt.ylabel('')
            plt.tight_layout()
            plt.savefig(save_path)
            plt.close()
    return os.path.basename(save_path)


# Generate all graphs
def generate_all_graphs(user_id, pro_id):
    """
    Generates all graphs for user, professional, and admin and saves them to PNG files.
    """
    folder_path = create_generated_images_folder()

    # User Graphs
    user_requests_by_status(user_id)
    user_spending_over_time(user_id, )
    user_service_usage(user_id, )

    # Professional Graphs
    professional_monthly_jobs(pro_id, )
    professional_earnings_over_time(pro_id, )
    professional_completed_pending_jobs(pro_id, )

    # Admin Graphs
    print(admin_requests_by_status())
    admin_top_cities()
    admin_revenue_by_service()
    admin_professional_activity_levels()

    print("All graphs generated successfully!")
    return folder_path


if __name__ == "__main__":
    # Replace with test User and Professional IDs from your database
    test_user_id = 1  # Replace with an actual user ID
    test_pro_id = 1  # Replace with an actual professional ID

    folder_path = generate_all_graphs(test_user_id, test_pro_id)
    print(f"Graphs are saved in the folder: {folder_path}")
