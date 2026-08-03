# TrekManager 🏔️

A comprehensive Trekking Management Application built with Flask.

## Tech Stack
- **Backend:** Flask, Flask-SQLAlchemy, Flask-Login
- **Frontend:** Jinja2, HTML, CSS, Bootstrap 5
- **Database:** SQLite

## Setup

1. Create virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Seed the database:
   ```bash
   python seed.py
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Open browser: `http://localhost:5000`

## Default Admin Credentials
- **Username:** admin
- **Password:** admin123

## Roles
- **Admin** — Manages treks, staff, and users
- **Trek Staff** — Guides assigned treks
- **User (Trekker)** — Books and participates in treks
