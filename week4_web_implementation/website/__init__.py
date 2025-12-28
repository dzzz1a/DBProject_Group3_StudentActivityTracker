from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "AkuCintaAris"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///student_activities.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # ----------- REGISTER BLUEPRINTS -----------
    from .views import views
    from .auth import auth
    from .admin import admin
    from .advisor import advisor as advisor_bp

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(admin, url_prefix="/admin")
    app.register_blueprint(advisor_bp, url_prefix="/advisor")

    from .models import Students, Advisor
    from werkzeug.security import generate_password_hash

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # prefix-based loader (fixes ID collision forever)
        if not user_id:
            return None

        if user_id.startswith("s"):
            real_id = int(user_id[1:])
            return Students.query.get(real_id)

        if user_id.startswith("a"):
            real_id = int(user_id[1:])
            return Advisor.query.get(real_id)

        return None

    with app.app_context():
        db.create_all()

        # Create your admin if none exists
        if not Advisor.query.filter_by(is_admin=True).first():
            admin = Advisor(
                advisorName="ATMIN",
                advisorEmail="atmin@anjay.com",
                advisorRole="Admin",
                advisorPassword=generate_password_hash("atmindatang"),
                status="Approved",
                is_admin=True,
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin created: atmin@anjay.com / atmindatang")

    return app
