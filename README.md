# DBProject_Group3_StudentActivityTracker

Student Activity Tracker
System is designed to provide a structured, database-based solution. The system will allow advisors to register activities, record student participation, while students can 
view available activities, status of applications and their personal activity history.
The application is built using Flask  with SQLAlchemy ORM and a SQLite database, following proper database normalization until 3NF


Group Members: 
Adam Rizky (24/536885/PA/22777)
Panji Merah Balakosa (24/532826/PA/22541)
Zidni Dziaulhaq (24/536623/PA/22759)


⚙️ Setup Instructions
1️⃣ Prerequisites

Make sure you have the following installed:

Python 3.9+

pip (Python package manager)

Git (optional, for cloning the repository)

2️⃣ Clone the Repository
git clone <repository-url>
cd student-activity-tracker

3️⃣ Create and Activate Virtual Environment
python -m venv venv


Activate:

Windows:

venv\Scripts\activate


macOS / Linux:

source venv/bin/activate

4️⃣ Install Dependencies
pip install -r requirements.txt

5️⃣ Initialize the Database
flask db init
flask db migrate
flask db upgrade


(If migrations are not used, ensure the SQLite database file is created before running the app.)

6️⃣ Run the Application
flask run


The application will be available at:

http://127.0.0.1:5000
