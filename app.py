from flask import Flask, request, jsonify
from flask_cors import CORS
# from resume_parser import parse_resume
# from parsingOut import create_parsing_out
from job_predictor import predict_job_title
from job_api import fetch_jobs
from dataOut import create_text
import tempfile
import os
import logging
import http.client
import json
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS

app.config['SECRET_KEY'] = 'magazizo3172'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

# Create tables (run once)
with app.app_context():
    db.create_all()

# JWT Authentication Decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

# Signup Endpoint
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'User already exists!'}), 409
        
    new_user = User(
        name=data['name'],
        email=data['email'],
        password=hashed_password
    )
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully!'}), 201

# Login Endpoint
@app.route('/api/login', methods=['POST'])
def login():
    auth = request.get_json()
    user = User.query.filter_by(email=auth['email']).first()

    if not user or not check_password_hash(user.password, auth['password']):
        return jsonify({'message': 'Invalid credentials!'}), 401

    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({'token': token})

# # Route 1: Parse Resume
# @app.route('/api/parse_resume', methods=['POST'])
# @token_required

# def handle_resume_parsing(current_user):

#     try:
#         # Get uploaded file
#         resume_file = request.files['resume']
#         # Save to temp file
#         temp_dir = tempfile.mkdtemp()
#         temp_path = os.path.join(temp_dir, resume_file.filename)
#         resume_file.save(temp_path)
#         # Parse resume
#         parsed_data = parse_resume(temp_path)
#         # create the parsed text
#         text = create_parsing_out(parsed_data)
#         # Predict Job Title
#         prediction_result = predict_job_title(text)
#         # Cleanup temp file
#         os.remove(temp_path)
#         os.rmdir(temp_dir)

#         return jsonify({
#             "predicted_job": prediction_result["title"],
#             "confidence": prediction_result["confidence"]
#         })
    
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
    
# Route 2: Handle Manual Input
@app.route('/api/entered_data', methods=['POST'])
@token_required

def handle_entered_data(current_user):
    
    try:
        data = request.json
        # Create User Profile Sentence
        text = create_text(data)
        # Predict Job Title
        prediction_result = predict_job_title(text)

        return jsonify({
            "predicted_job": prediction_result["title"],
            "confidence": prediction_result["confidence"]
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route 3: Job Search
@app.route('/api/search-from-data', methods=['POST'])
@token_required

def handle_job_search(current_user):

    try:
        input_data = request.json
        date = input_data.get('datePosted')
        experience = input_data.get('experienceLevel')
        jobTitle = input_data.get('Job')

        # setting the required duration
        if date == 'Past 24hrs':
            duration = 0
        elif date == 'Past Week':
            duration = 7
        elif date == 'Past Month':
            duration = 30
        else:
            duration = 356
        
        # setting the experience leve
        if experience == 'Junior level':
            experience_level = "junior"
        elif experience == 'Senior level':
            experience_level = "senior"
        elif experience == 'Executive':
            experience_level = "c_level"
        elif experience == 'Any':
            experience_level = ""
        else:
            experience_level = ""

        conn = http.client.HTTPSConnection("api.theirstack.com")

        payload = f"""
        {{
        "page": 0,
        "limit": 10,
        "job_title_or": [
            "{jobTitle}"
        ],
        "job_seniority_or": [
        "{experience_level}"
        ],
        "posted_at_max_age_days": "{duration}"
        }}
        """

        headers = {
            'Content-Type': "application/json",
            'Authorization': "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbHN3YWdpNzY3QGdtYWlsLmNvbSIsInBlcm1pc3Npb25zIjoidXNlciIsImNyZWF0ZWRfYXQiOiIyMDI1LTA0LTEzVDEwOjMxOjMwLjEzNDI4NSswMDowMCJ9.7q4yN5G6p-ZmSq9y37J-lI6XprvFnB5byaZwpBSwGx8"
        }

        conn.request("POST", "/v1/jobs/search", payload, headers)

        res = conn.getresponse()
        data = res.read()
        response_data = json.loads(data)
        filtered_jobs = []
        for job in response_data.get('data', []):
            filtered = {
                'job_title': job.get('job_title'),
                'company': job.get('company'),
                'date_posted': job.get('date_posted'),
                'source_url': job.get('source_url'),
                'location': job.get('location'),
                'remote': job.get('remote'),
                'employment_statuses': job.get('employment_statuses', [])
            }
            filtered_jobs.append(filtered)

        return jsonify(filtered_jobs)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

if __name__ == '__main__':
    app.run(debug=True, port=5000)