from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta
import jwt

from .models import Students, Activity, Participation
from . import db

api = Blueprint("api", __name__)

def create_token(user):
    payload = {
        "sub": user.studentID,
        "email": user.studentEmail,
        "exp": datetime.utcnow() + timedelta(hours=2),
    }
    token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")
    # PyJWT >= 2 returns str already
    return token

def token_required(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"error": "Missing or invalid token"}), 401
        token = parts[1]
        try:
            payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload["sub"]
        except Exception as e:
            return jsonify({"error": "Token invalid"}), 401
        return f(user_id, *args, **kwargs)
    return wrapper

@api.route("/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    user = Students.query.filter_by(studentEmail=email).first()
    if not user or not check_password_hash(user.studentPassword, password):
        return jsonify({"error": "Invalid credentials"}), 401
    token = create_token(user)
    return jsonify({"token": token})

@api.route("/students", methods=["GET"])
@token_required
def api_students_list(user_id):
    students = Students.query.all()
    result = [
        {
            "studentID": s.studentID,
            "firstName": s.studentFirstName,
            "lastName": s.studentLastName,
            "email": s.studentEmail,
        }
        for s in students
    ]
    return jsonify(result)

@api.route("/activities", methods=["GET"])
@token_required
def api_activities_list(user_id):
    activities = Activity.query.all()
    result = [
        {
            "activityID": a.activityID,
            "name": a.activityName,
            "category": a.activityCategory,
            "location": a.activityLocation,
        }
        for a in activities
    ]
    return jsonify(result)

@api.route("/participations", methods=["GET"])
@token_required
def api_participations_list(user_id):
    parts = Participation.query.filter_by(studentID=user_id).all()
    result = [
        {
            "participationID": p.participationID,
            "activityID": p.activityID,
            "status": p.applicationStatus,
            "feedback": p.advisorFeedback,
        }
        for p in parts
    ]
    return jsonify(result)
