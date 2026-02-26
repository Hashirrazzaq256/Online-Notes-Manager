# 📝 Online Notes Manager

A full-stack web application for seamless note-taking with a unique **Hybrid Storage System**.

Users can start writing notes as guests (stored in browser localStorage) and later sync them securely to a cloud SQLite database upon registration.

---

## Key Features

### Guest Mode
- Create, edit, and delete notes without an account
- Notes stored locally using `localStorage`

### Auto-Save
- Automatic 5-second interval saving
- Prevents accidental data loss while typing

### Cloud Sync
- Automatically migrates guest notes to SQLite database after login or registration

### Secure Authentication
- User registration & login
- Password hashing using `Werkzeug Security`
- Session management with `Flask-Login`

### Advanced Note Management
- Pin important notes
- Categorize notes
- Set reminders

### Export
- Download any note as a `.txt` file

---

## Tech Stack

**Backend**
- Python
- Flask

**Frontend**
- HTML5
- CSS3
- Vanilla JavaScript

**Database**
- SQLite

**Authentication**
- Flask-Login
- Werkzeug Security

---

## Project Structure

```
online-notes-manager/
│
├── app.py                  # Main Flask application and API routes
├── init_db.py              # Database initialization script
├── schema.sql              # Database schema (Users, Notes)
├── requirements.txt        # Project dependencies
│
├── static/
│   ├── css/
│   │   └── style.css       # Custom styling
│   └── js/
│       └── app.js          # Frontend logic (LocalStorage & Fetch API)
│
└── templates/
    ├── base.html
    ├── dashboard.html
    ├── login.html
    └── register.html
```

---

## ⚙️ Installation & Setup

### Clone Repository

```bash
git clone https://github.com/your-username/online-notes-manager.git
cd online-notes-manager
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install flask flask-login werkzeug
```

### Initialize Database

```bash
python init_db.py
```

###  Run Application

```bash
python app.py
```

App will run at:

```
http://127.0.0.1:5000
```

---

## Database Design

### One-to-Many Relationship

One User → Many Notes

---

### Users Table

| Field         | Type    | Description              |
|--------------|---------|--------------------------|
| id           | Integer | Primary Key              |
| username     | Text    | Unique username          |
| email        | Text    | Unique email             |
| password_hash| Text    | Hashed password          |
| created_at   | Text    | Account creation time    |

---

### Notes Table

| Field        | Type    | Description                        |
|-------------|---------|------------------------------------|
| id          | Integer | Primary Key                        |
| user_id     | Integer | Foreign Key → Users.id             |
| title       | Text    | Note title                         |
| content     | Text    | Note content                       |
| category    | Text    | Note category                      |
| is_pinned   | Integer | 0 = False, 1 = True                |
| reminder_at | Text    | Reminder datetime                  |
| created_at  | Text    | Creation timestamp                 |
| updated_at  | Text    | Last updated timestamp             |

---

## Hybrid Storage Architecture

| Mode        | Storage Type         | Description |
|------------|---------------------|------------|
| Guest Mode | Browser localStorage| Temporary notes without login |
| User Mode  | SQLite Database     | Persistent notes for registered users |
| Migration  | Automatic Sync      | Guest notes migrate on login |

---

## Security Practices

- Password hashing with Werkzeug
- Authenticated route protection
- Foreign key constraints enabled
- Server-side validation
- Secure session handling

---



---



---
