from . import db
from flask_login import UserMixin

# ---------------- STUDENT MODEL ---------------- #

class Students(db.Model, UserMixin):
    __tablename__ = "students"

    studentID = db.Column(db.Integer, primary_key=True)
    studentFirstName = db.Column(db.String(15))
    studentLastName = db.Column(db.String(15))
    studentYear = db.Column(db.Integer)
    studentEmail = db.Column(db.String(25))
    studentPassword = db.Column(db.String(15))
    studentAddress = db.Column(db.String(255))
    phoneNumber = db.Column(db.Integer)

    @property
    def id(self):
        return f"s{self.studentID}"

    @property
    def role_type(self):
        return "student"


# ---------------- ADVISOR MODEL ---------------- #

class Advisor(db.Model, UserMixin):
    __tablename__ = "advisor"

    advisorID = db.Column(db.Integer, primary_key=True)
    advisorName = db.Column(db.String(20))
    advisorEmail = db.Column(db.String(25))
    advisorRole = db.Column(db.String(15))
    advisorPassword = db.Column(db.String(15))
    availableSchedule = db.Column(db.Text)

    # Added for functionality (NOT in SQL, but necessary)
    status = db.Column(db.String(20), default="Pending")
    is_admin = db.Column(db.Boolean, default=False)

    @property
    def id(self):
        return f"a{self.advisorID}"

    @property
    def role_type(self):
        return "advisor"


# ---------------- ACTIVITY MODEL ---------------- #

class Activity(db.Model):
    __tablename__ = "activity"

    activityID = db.Column(db.Integer, primary_key=True)
    activityName = db.Column(db.String(30))
    activityCategory = db.Column(db.String(20))
    activityLocation = db.Column(db.String(50))
    activityDetails = db.Column(db.Text)
    activityStartDate = db.Column(db.Date)
    activityEndDate = db.Column(db.Date)
    activityFrequency = db.Column(db.String(20))

    advisorID = db.Column(db.Integer, db.ForeignKey("advisor.advisorID"))
    advisor = db.relationship("Advisor")


# ---------------- PARTICIPATION MODEL ---------------- #

class Participation(db.Model):
    __tablename__ = "participation"

    participationID = db.Column(db.Integer, primary_key=True)
    dateApplied = db.Column(db.Date)
    applicationStatus = db.Column(db.String(20))
    approvalDate = db.Column(db.Date)
    advisorFeedback = db.Column(db.Text)
    achievements = db.Column(db.Text)

    studentID = db.Column(db.Integer, db.ForeignKey("students.studentID"))
    activityID = db.Column(db.Integer, db.ForeignKey("activity.activityID"))
    advisorID = db.Column(db.Integer, db.ForeignKey("advisor.advisorID"))

    student = db.relationship("Students")
    activity = db.relationship("Activity")
    advisor = db.relationship("Advisor")
