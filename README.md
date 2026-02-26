Online Notes Manager
Online Notes Manager is a full-stack web application designed for seamless note-taking. It features a unique "Hybrid" storage system that allows users to start writing as guests and later sync their data to a secure cloud database upon registration.

Key Features

Guest Mode: Create, edit, and delete notes without an account; data is saved in the browser's localStorage.
+1


Auto-Save: Automatic 5-second interval saving to prevent data loss while typing.
+1


Cloud Sync: Automatically migrates all local guest notes to the SQLite database once a user logs in.
+1


Secure Authentication: User registration and login with industry-standard password hashing.
+1


Advanced Management: Pin important notes, categorize them, and set reminders.


Export Options: Download any note as a .txt file for offline use.

Tech Stack

Backend: Python, Flask 


Frontend: HTML5, CSS3, JavaScript (Vanilla) 
+1


Database: SQLite 
+1


Authentication: Flask-Login, Werkzeug Security 
+1

Project Structure

Plaintext
├── app.py              # Main Flask application and API routes
├── init_db.py          # Script to initialize the SQLite database
├── schema.sql          # Database table definitions (Users, Notes)
├── static/
│   ├── css/            # Custom styling
│   └── js/             # Frontend logic (LocalStorage & Fetch API)
└── templates/          # Jinja2 HTML templates (Dashboard, Login, etc.)
Installation & Setup
Clone the repository:

Bash
git clone https://github.com/your-username/online-notes-manager.git
cd online-notes-manager
Install dependencies:

Bash
pip install flask flask-login
Initialize the Database:

Bash
python init_db.py
Run the Application:

Bash
python app.py
The app will be available at http://127.0.0.1:5000.

 Database Design
The project uses a One-to-Many relationship where one user can own multiple notes
