from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta
import jwt

from .models import Students, Activity, Participation
from . import db

api = Blueprint("api", __name__)


# ======================================================================
# Helpers: JWT
# ======================================================================

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
            payload = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"],
            )
            user_id = payload["sub"]
        except Exception:
            return jsonify({"error": "Token invalid"}), 401

        return f(user_id, *args, **kwargs)

    return wrapper




# ======================================================================
# Auth
# ======================================================================

@api.route("/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = Students.query.filter_by(studentEmail=email).first()
    if not user or not check_password_hash(user.studentPassword, password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_token(user)
    return jsonify({"token": token})


# ======================================================================
# Students
# ======================================================================

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

@api.route("/students", methods=["POST"])
@token_required
def api_create_student(user_id):
    data = request.get_json() or {}

    required_fields = ["firstName", "lastName", "email", "password"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    student = Students(
        studentFirstName=data.get("firstName"),
        studentLastName=data.get("lastName"),
        studentYear=data.get("year"),
        studentEmail=data.get("email"),
        studentPassword=data.get("password"),  # consider hashing
        studentAddress=data.get("address"),
        phoneNumber=data.get("phone")
    )

    db.session.add(student)
    db.session.commit()
    return jsonify({"message": "Student created", "studentID": student.studentID}), 201


@api.route("/students/<int:student_id>", methods=["PUT"])
@token_required
def api_update_student(user_id, student_id):
    student = Students.query.get_or_404(student_id)
    data = request.get_json() or {}

    student.studentFirstName = data.get("firstName", student.studentFirstName)
    student.studentLastName = data.get("lastName", student.studentLastName)
    student.studentYear = data.get("year", student.studentYear)
    student.studentEmail = data.get("email", student.studentEmail)
    student.studentPassword = data.get("password", student.studentPassword)
    student.studentAddress = data.get("address", student.studentAddress)
    student.phoneNumber = data.get("phone", student.phoneNumber)

    db.session.commit()
    return jsonify({"message": "Student updated"})


@api.route("/students/<int:student_id>", methods=["DELETE"])
@token_required
def api_delete_student(user_id, student_id):
    student = Students.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": "Student deleted"})


# ======================================================================
# Activities (LIST + CRUD + SEARCH)
# ======================================================================

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


@api.route("/activities/<int:activity_id>", methods=["GET"])
@token_required
def api_activity_detail(user_id, activity_id):
    a = Activity.query.get_or_404(activity_id)
    return jsonify(
        {
            "activityID": a.activityID,
            "name": a.activityName,
            "category": a.activityCategory,
            "location": a.activityLocation,
            "details": a.activityDetails,
            "startDate": a.activityStartDate,
            "endDate": a.activityEndDate,
            "frequency": a.activityFrequency,
            "advisorID": a.advisorID,
        }
    )


@api.route("/activities", methods=["POST"])
@token_required
def api_create_activity(user_id):
    data = request.get_json() or {}

    # minimal validation; adjust as needed
    if not data.get("name"):
        return jsonify({"error": "Activity name is required"}), 400

    a = Activity(
        activityName=data.get("name"),
        activityCategory=data.get("category"),
        activityLocation=data.get("location"),
        activityDetails=data.get("details"),
        activityStartDate=data.get("startDate"),
        activityEndDate=data.get("endDate"),
        activityFrequency=data.get("frequency"),
        advisorID=data.get("advisorID"),
    )

    db.session.add(a)
    db.session.commit()

    return jsonify(
        {"message": "Activity created", "activityID": a.activityID}
    ), 201


@api.route("/activities/<int:activity_id>", methods=["PUT"])
@token_required
def api_update_activity(user_id, activity_id):
    data = request.get_json() or {}
    a = Activity.query.get_or_404(activity_id)

    a.activityName = data.get("name", a.activityName)
    a.activityCategory = data.get("category", a.activityCategory)
    a.activityLocation = data.get("location", a.activityLocation)
    a.activityDetails = data.get("details", a.activityDetails)
    a.activityStartDate = data.get("startDate", a.activityStartDate)
    a.activityEndDate = data.get("endDate", a.activityEndDate)
    a.activityFrequency = data.get("frequency", a.activityFrequency)
    a.advisorID = data.get("advisorID", a.advisorID)

    db.session.commit()
    return jsonify({"message": "Activity updated"})


@api.route("/activities/<int:activity_id>", methods=["DELETE"])
@token_required
def api_delete_activity(user_id, activity_id):
    a = Activity.query.get_or_404(activity_id)
    db.session.delete(a)
    db.session.commit()
    return jsonify({"message": "Activity deleted"})


@api.route("/activities/search", methods=["GET"])
@token_required
def api_search_activities(user_id):
    keyword = request.args.get("keyword", "").strip()

    if not keyword:
        # if no keyword, just return all activities (or empty list if you prefer)
        activities = Activity.query.all()
    else:
        activities = Activity.query.filter(
            Activity.activityName.ilike(f"%{keyword}%")
        ).all()

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


# ======================================================================
# Participations (LIST + CREATE + UPDATE)
# ======================================================================

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
            "achievements": p.achievements,
            "dateApplied": p.dateApplied,
            "approvalDate": p.approvalDate,
            "advisorID": p.advisorID,
        }
        for p in parts
    ]
    return jsonify(result)


@api.route("/participations", methods=["POST"])
@token_required
def api_create_participation(user_id):
    data = request.get_json() or {}

    if not data.get("activityID"):
        return jsonify({"error": "activityID is required"}), 400

    participation = Participation(
        studentID=user_id,
        activityID=data.get("activityID"),
        advisorID=data.get("advisorID"),
        dateApplied=datetime.utcnow(),
        applicationStatus="Pending",
        advisorFeedback=None,
        achievements=None,
    )

    db.session.add(participation)
    db.session.commit()

    return jsonify(
        {
            "message": "Participation submitted",
            "participationID": participation.participationID,
        }
    ), 201


@api.route("/participations/<int:pid>", methods=["PUT"])
@token_required
def api_update_participation(user_id, pid):
    data = request.get_json() or {}
    p = Participation.query.get_or_404(pid)

    # basic fields an advisor / system can update
    status = data.get("status")
    if status is not None:
        p.applicationStatus = status
        if status == "Approved":
            p.approvalDate = datetime.utcnow()
        elif status == "Rejected":
            p.approvalDate = datetime.utcnow()
        else:
            p.approvalDate = None

    if "feedback" in data:
        p.advisorFeedback = data.get("feedback")

    if "achievements" in data:
        p.achievements = data.get("achievements")

    db.session.commit()
    return jsonify({"message": "Participation updated"})

@api.route("/students/<int:student_id>/activities", methods=["GET"])
@token_required
def api_student_activity_history(user_id, student_id):
    activity_name = request.args.get('name', type=str)
    category = request.args.get('category', type=str)
    status = request.args.get('status', type=str)

    participations = Participation.query.filter_by(studentID=student_id).all()

    data = []
    for p in participations:
        activity = Activity.query.get(p.activityID)
        
        if activity_name and activity_name.lower() not in activity.activityName.lower():
            continue
        if category and category.lower() not in activity.activityCategory.lower():
            continue
        if status and status.lower() != p.applicationStatus.lower():
            continue

        data.append({
            "participationID": p.participationID,
            "activityID": activity.activityID,
            "activityName": activity.activityName,
            "category": activity.activityCategory,
            "location": activity.activityLocation,
            "dateApplied": p.dateApplied,
            "status": p.applicationStatus
        })

    return jsonify({"history": data}), 200

