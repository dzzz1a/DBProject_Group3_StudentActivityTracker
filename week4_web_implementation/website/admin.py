from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime

from . import db
from .models import Students, Advisor, Activity, Participation

admin = Blueprint("admin", __name__)

# ---------------- ADMIN REQUIRED DECORATOR ---------------- #

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        if getattr(current_user, "role_type", None) != "advisor" or not getattr(current_user, "is_admin", False):
            flash("Not authorized.", "danger")
            return redirect(url_for("views.dashboard"))
        return f(*args, **kwargs)
    return wrapper


# ---------------- ADMIN HOME ---------------- #

@admin.route("/")
@login_required
@admin_required
def index():
    return render_template("admin_home.html")


# ---------------- STUDENTS CRUD ---------------- #

@admin.route("/students")
@login_required
@admin_required
def students_list():
    students = Students.query.all()
    return render_template("admin_students.html", students=students)


@admin.route("/students/add", methods=["GET", "POST"])
@login_required
@admin_required
def students_add():
    if request.method == "POST":
        s = Students(
            studentFirstName=request.form.get("first_name"),
            studentLastName=request.form.get("last_name"),
            studentEmail=request.form.get("email"),
            studentYear=request.form.get("year"),
            studentAddress=request.form.get("address"),
            phoneNumber=request.form.get("phone"),
            studentPassword=request.form.get("password") or "password",
        )
        db.session.add(s)
        db.session.commit()
        flash("Student added.", "success")
        return redirect(url_for("admin.students_list"))
    return render_template("admin_student_form.html")


@admin.route("/students/edit/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def students_edit(id):
    s = Students.query.get_or_404(id)
    if request.method == "POST":
        s.studentFirstName = request.form.get("first_name")
        s.studentLastName = request.form.get("last_name")
        s.studentEmail = request.form.get("email")
        s.studentYear = request.form.get("year")
        s.studentAddress = request.form.get("address")
        s.phoneNumber = request.form.get("phone")
        db.session.commit()
        flash("Student updated.", "success")
        return redirect(url_for("admin.students_list"))
    return render_template("admin_student_form.html", student=s)


@admin.route("/students/delete/<int:id>")
@login_required
@admin_required
def students_delete(id):
    s = Students.query.get_or_404(id)
    db.session.delete(s)
    db.session.commit()
    flash("Student deleted.", "warning")
    return redirect(url_for("admin.students_list"))


# ---------------- ADVISORS MANAGEMENT ---------------- #

@admin.route("/advisors")
@login_required
@admin_required
def advisors_list():
    advisors = Advisor.query.all()
    return render_template("admin_advisors.html", advisors=advisors)


@admin.route("/advisors/update_status/<int:id>", methods=["POST"])
@login_required
@admin_required
def advisors_update_status(id):
    a = Advisor.query.get_or_404(id)
    new_status = request.form.get("status")
    make_admin = request.form.get("make_admin") == "on"

    a.status = new_status
    a.is_admin = make_admin and (new_status == "Approved")

    db.session.commit()
    flash("Advisor updated.", "success")
    return redirect(url_for("admin.advisors_list"))


@admin.route("/advisors/delete/<int:id>")
@login_required
@admin_required
def advisors_delete(id):
    a = Advisor.query.get_or_404(id)
    db.session.delete(a)
    db.session.commit()
    flash("Advisor deleted.", "warning")
    return redirect(url_for("admin.advisors_list"))


# ---------------- ACTIVITIES CRUD ---------------- #

@admin.route("/activities")
@login_required
@admin_required
def activities_list():
    activities = Activity.query.all()
    return render_template("admin_activities.html", activities=activities)


@admin.route("/activities/add", methods=["GET", "POST"])
@login_required
@admin_required
def activities_add():
    if request.method == "POST":
        start_date_str = request.form.get("start_date")
        end_date_str = request.form.get("end_date")

        ac = Activity(
            activityName=request.form.get("name"),
            activityCategory=request.form.get("category"),
            activityLocation=request.form.get("location"),
            activityDetails=request.form.get("details"),
            activityStartDate=datetime.strptime(start_date_str, "%Y-%m-%d").date() if start_date_str else None,
            activityEndDate=datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else None,
            activityFrequency=request.form.get("frequency"),
        )

        db.session.add(ac)
        db.session.commit()
        flash("Activity added.", "success")
        return redirect(url_for("admin.activities_list"))

    return render_template("admin_activity_form.html", activity=None)


@admin.route("/activities/edit/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def activities_edit(id):
    ac = Activity.query.get_or_404(id)

    if request.method == "POST":
        ac.activityName = request.form.get("name")
        ac.activityCategory = request.form.get("category")
        ac.activityLocation = request.form.get("location")
        ac.activityDetails = request.form.get("details")

        start_date_str = request.form.get("start_date")
        end_date_str = request.form.get("end_date")

        if start_date_str:
            ac.activityStartDate = datetime.strptime(start_date_str, "%Y-%m-%d").date()

        if end_date_str:
            ac.activityEndDate = datetime.strptime(end_date_str, "%Y-%m-%d").date()

        ac.activityFrequency = request.form.get("frequency")

        db.session.commit()
        flash("Activity updated.", "success")
        return redirect(url_for("admin.activities_list"))

    return render_template("admin_activity_form.html", activity=ac)


@admin.route("/activities/delete/<int:id>")
@login_required
@admin_required
def activities_delete(id):
    ac = Activity.query.get_or_404(id)
    db.session.delete(ac)
    db.session.commit()
    flash("Activity deleted.", "warning")
    return redirect(url_for("admin.activities_list"))


# ---------------- PARTICIPATION APPROVAL ---------------- #

@admin.route("/participations")
@login_required
@admin_required
def participations_list():
    participations = Participation.query.all()
    return render_template("admin_participations.html", participations=participations)


@admin.route("/participations/update/<int:id>", methods=["POST"])
@login_required
@admin_required
def participations_update(id):
    p = Participation.query.get_or_404(id)
    p.applicationStatus = request.form.get("status")
    p.advisorFeedback = request.form.get("feedback")
    db.session.commit()

    flash("Participation updated.", "success")
    return redirect(url_for("admin.participations_list"))
