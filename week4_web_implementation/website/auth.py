from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required

from .models import Students, Advisor
from . import db

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # 1) Try advisor login first
        advisor = Advisor.query.filter_by(advisorEmail=email).first()
        if advisor:
            if advisor.status != "Approved":
                flash(
                    "Your advisor account is not approved yet. Please contact admin.",
                    "warning",
                )
                return render_template("login.html")

            if not advisor.advisorPassword or not check_password_hash(
                advisor.advisorPassword, password
            ):
                flash("Invalid email or password", "danger")
                return render_template("login.html")

            login_user(advisor, remember=True)

            if advisor.is_admin:
                return redirect(url_for("admin.index"))
            else:
                return redirect(url_for("advisor.dashboard"))

        # 2) Try student login
        student = Students.query.filter_by(studentEmail=email).first()
        if student and check_password_hash(student.studentPassword, password):
            login_user(student, remember=True)
            return redirect(url_for("views.dashboard"))

        flash("Invalid email or password", "danger")

    return render_template("login.html")


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first = request.form.get("first_name")
        last = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")

        existing_student = Students.query.filter_by(
            studentEmail=email
        ).first()
        existing_advisor = Advisor.query.filter_by(
            advisorEmail=email
        ).first()
        if existing_student or existing_advisor:
            flash("Email already registered.", "warning")
        else:
            new_user = Students(
                studentFirstName=first,
                studentLastName=last,
                studentEmail=email,
                studentPassword=generate_password_hash(
                    password, method="pbkdf2:sha256", salt_length=16
                ),
            )
            db.session.add(new_user)
            db.session.commit()
            flash("Account created, please login", "success")
            return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth.route("/register_advisor", methods=["GET", "POST"])
def register_advisor():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")

        existing_student = Students.query.filter_by(
            studentEmail=email
        ).first()
        existing_advisor = Advisor.query.filter_by(
            advisorEmail=email
        ).first()
        if existing_student or existing_advisor:
            flash("Email already registered.", "warning")
            return redirect(url_for("auth.register_advisor"))

        advisor = Advisor(
            advisorName=name,
            advisorEmail=email,
            advisorRole=role,
            advisorPassword=generate_password_hash(password),
            status="Pending",  # admin must approve
            is_admin=False,
        )

        db.session.add(advisor)
        db.session.commit()

        flash(
            "Advisor account registered. Waiting for admin approval.",
            "success",
        )
        return redirect(url_for("auth.login"))

    return render_template("register_advisor.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home"))
