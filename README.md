# Notes App — Flask Backend API

## Description

A RESTful backend API for a personal notes application built with Flask, SQLAlchemy, and Marshmallow.
Users can sign up, log in, and manage their own private notes. All notes are protected — users can only
access and modify their own data. Includes session-based authentication and pagination.

---

## Tech Stack

- Python 3.8+
- Flask 2.2.2
- Flask-SQLAlchemy 3.0.3
- Flask-Migrate 3.1.0
- Flask-Bcrypt (password hashing)
- Marshmallow 3.20.1 (validation & serialization)

---

## Installation

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd <repo-name>
```

### 2. Install dependencies
```bash
pipenv install
pipenv shell
```

### 3. Navigate to the server directory
```bash
cd server
```

### 4. Initialize and migrate the database
```bash
flask db init
flask db migrate -m "initial migration"
flask db upgrade head
```

### 5. Seed the database with sample data
```bash
python seed.py
```

---

## Running the App

```bash
flask run --port 5555
```

or

```bash
python app.py
```

The API will be available at: `http://localhost:5555`

---

## API Endpoints

### Auth

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/signup` | Create a new user account | No |
| POST | `/login` | Log in with username & password | No |
| DELETE | `/logout` | Log out and clear session | No |
| GET | `/check_session` | Check if user is logged in | No |

**Signup / Login body:**
```json
{ "username": "alice", "password": "password123" }
```

---

### Notes

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/notes` | Get all notes for logged-in user (paginated) | Yes |
| GET | `/notes/<id>` | Get a single note by ID | Yes |
| POST | `/notes` | Create a new note | Yes |
| PATCH | `/notes/<id>` | Update a note | Yes |
| DELETE | `/notes/<id>` | Delete a note | Yes |

**Pagination:** `GET /notes?page=1&per_page=5`

**Create / Update note body:**
```json
{ "title": "My Note", "content": "Note content here." }
```

---

## Notes on Security

- Passwords are hashed with bcrypt — never stored as plain text.
- Sessions are signed with a secret key — cannot be tampered with.
- Users can only view, edit, or delete their **own** notes.
- Accessing another user's note returns a `403 Forbidden`.

---

## Project Structure

```
server/
  app.py       
  models.py     
  schemas.py    
  seed.py       
  instance/
    app.db      
  migrations/   
README.md
Pipfile
```