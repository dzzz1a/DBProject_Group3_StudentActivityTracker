from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import date
from sqlalchemy import or_  # <--- Added for search logic

from .models import Activity, Participation, Advisor
from . import db

views = Blueprint("views", __name__)


@views.route("/")
def home():
    return render_template("home.html")


# ---------------- STUDENT DASHBOARD ---------------- #

@views.route("/dashboard")
@login_required
def dashboard():
    # Only students
    if getattr(current_user, "role_type", None) != "student":
        if getattr(current_user, "role_type", None) == "advisor":
            if getattr(current_user, "is_admin", False):
                return redirect(url_for("admin.index"))
            return redirect(url_for("advisor.dashboard"))
        return redirect(url_for("auth.login"))

    # FIX: Joined activities = approved participation requests
    joined = (
        Activity.query.join(Participation)
        .filter(
            Participation.studentID == current_user.studentID,
            Participation.applicationStatus == "Approved"
        )
        .all()
    )

    participations = Participation.query.filter_by(
        studentID=current_user.studentID
    ).all()

    return render_template(
        "dashboard.html",
        joined=joined,
        participations=participations
    )



# ---------------- ACTIVITY LIST (STUDENTS) ---------------- #

@views.route("/activities")
@login_required
def activities():
    # Students only; advisors/admins shouldn't use this page
    if getattr(current_user, "role_type", None) != "student":
        if getattr(current_user, "role_type", None) == "advisor":
            if getattr(current_user, "is_admin", False):
                return redirect(url_for("admin.index"))
            return redirect(url_for("advisor.dashboard"))
        return redirect(url_for("auth.login"))

    # --- SEARCH LOGIC START ---
    search_query = request.args.get('q')

    if search_query:
        # Filter by Name OR Category OR Location
        activities = Activity.query.filter(
            or_(
                Activity.activityName.ilike(f'%{search_query}%'),
                Activity.activityCategory.ilike(f'%{search_query}%'),
                Activity.activityLocation.ilike(f'%{search_query}%')
            )
        ).all()
    else:
        activities = Activity.query.all()
    # --- SEARCH LOGIC END ---

    return render_template("activities.html", activities=activities)


# ---------------- PARTICIPATION REQUEST ---------------- #

@views.route("/participate/<int:activity_id>", methods=["GET", "POST"])
@login_required
def participate(activity_id):
    # 1. Role Check: Students only
    if getattr(current_user, "role_type", None) != "student":
        if getattr(current_user, "role_type", None) == "advisor":
            if getattr(current_user, "is_admin", False):
                return redirect(url_for("admin.index"))
            return redirect(url_for("advisor.dashboard"))
        return redirect(url_for("auth.login"))

    # 2. Check if Student is ALREADY applied or accepted
    existing_participation = Participation.query.filter_by(
        studentID=current_user.studentID,
        activityID=activity_id
    ).first()

    if existing_participation:
        if existing_participation.applicationStatus == 'Approved':
            flash("You have already been accepted into this activity.", "info")
            return redirect(url_for('views.dashboard'))
        elif existing_participation.applicationStatus == 'Pending':
            flash("You already have a pending request for this activity. Please wait for approval.", "warning")
            return redirect(url_for('views.dashboard'))
        # If 'Rejected', we allow them to apply again (optional)

    activity = Activity.query.get_or_404(activity_id)
    
    # Show only Approved advisors
    advisors = Advisor.query.filter_by(status="Approved").all()

    if request.method == "POST":
        advisor_id = request.form.get("advisor_id")

        if not advisor_id:
            flash("Please select an advisor.", "warning")
            return redirect(url_for("views.participate", activity_id=activity_id))

        participation = Participation(
            studentID=current_user.studentID,
            activityID=activity_id,
            advisorID=int(advisor_id),
            applicationStatus="Pending",
            dateApplied=date.today(),
        )

        db.session.add(participation)
        db.session.commit()

        flash("Participation request submitted!", "success")
        return redirect(url_for("views.dashboard"))

    return render_template(
        "participate.html",
        activity=activity,
        advisors=advisors
    )


# ---------------- STUDENT PROFILE (VIEW + EDIT) ---------------- #

@views.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    # Students only
    if getattr(current_user, "role_type", None) != "student":
        if getattr(current_user, "role_type", None) == "advisor":
            if getattr(current_user, "is_admin", False):
                return redirect(url_for("admin.index"))
            return redirect(url_for("advisor.dashboard"))
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        current_user.studentFirstName = request.form.get("first_name")
        current_user.studentLastName = request.form.get("last_name")
        current_user.studentEmail = request.form.get("email")
        year = request.form.get("year")
        current_user.studentYear = int(year) if year else None
        current_user.studentAddress = request.form.get("address")
        phone = request.form.get("phone")
        current_user.phoneNumber = int(phone) if phone else None

        new_password = request.form.get("password")
        if new_password:
            current_user.studentPassword = generate_password_hash(
                new_password, method="pbkdf2:sha256", salt_length=16
            )

        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("views.profile"))

    return render_template("profile.html")

#search activity history
@views.route("/activity-history", methods=["GET"])
@login_required
def activity_history():
    # Students only
    if getattr(current_user, "role_type", None) != "student":
        if getattr(current_user, "role_type", None) == "advisor":
            if getattr(current_user, "is_admin", False):
                return redirect(url_for("admin.index"))
            return redirect(url_for("advisor.dashboard"))
        return redirect(url_for("auth.login"))

    # Read search keyword from URL parameter
    search_query = request.args.get("q", "")

    # Join Participation + Activity for filtering
    participations = (
        Participation.query
        .join(Activity)
        .filter(
            Participation.studentID == current_user.studentID,
            Activity.activityName.ilike(f"%{search_query}%")
        )
        .all()
    )

    return render_template(
        "activity_history.html",
        participations=participations,
        search_query=search_query
    )