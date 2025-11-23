from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from functools import wraps
from werkzeug.security import generate_password_hash

from . import db
from .models import Participation, Advisor, Activity, Students


advisor = Blueprint("advisor", __name__)


def advisor_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        if current_user.role_type != "advisor":
            flash("You are not authorized to access the advisor dashboard.", "danger")
            return redirect(url_for("views.dashboard"))
        return f(*args, **kwargs)
    return wrapper


@advisor.route("/dashboard")
@login_required
@advisor_required
def dashboard():
    participations = Participation.query.filter_by(advisorID=current_user.advisorID).all()
    return render_template("advisor_dashboard.html", participations=participations)


@advisor.route("/participation/<int:id>/update", methods=["POST"])
@login_required
@advisor_required
def update_participation(id):
    participation = Participation.query.get_or_404(id)

    if participation.advisorID != current_user.advisorID:
        flash("You cannot update a request not assigned to you.", "danger")
        return redirect(url_for("advisor.dashboard"))

    status = request.form.get("status")
    feedback = request.form.get("feedback")

    participation.applicationStatus = status
    participation.advisorFeedback = feedback

    db.session.commit()

    flash("Participation updated.", "success")
    return redirect(url_for("advisor.dashboard"))


@advisor.route("/participation/<int:id>/delete")
@login_required
@advisor_required
def delete_participation(id):
    p = Participation.query.get_or_404(id)

    if p.advisorID != current_user.advisorID:
        flash("You cannot delete this request.", "danger")
        return redirect(url_for("advisor.dashboard"))

    db.session.delete(p)
    db.session.commit()

    flash("Request deleted.", "warning")
    return redirect(url_for("advisor.dashboard"))


@advisor.route("/profile", methods=["GET", "POST"])
@login_required
@advisor_required
def profile():
    if request.method == "POST":
        current_user.advisorName = request.form.get("name")
        current_user.advisorEmail = request.form.get("email")
        current_user.advisorRole = request.form.get("role")
        current_user.availableSchedule = request.form.get("schedule")

        new_password = request.form.get("password")
        if new_password:
            current_user.advisorPassword = generate_password_hash(
                new_password, method="pbkdf2:sha256", salt_length=16
            )

        db.session.commit()
        flash("Advisor profile updated.", "success")
        return redirect(url_for("advisor.profile"))

    return render_template("advisor_profile.html")
