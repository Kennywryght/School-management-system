# School Management System

A comprehensive web application for managing a secondary school in Malawi. Allows administrators to manage classes, subjects, teachers, and students. Teachers can upload results, and students can view their performance and class position.

## Features

### Admin Panel
- Manage Classes, Subjects, and Terms
- Manage Teachers and Students (auto-creates user accounts)
- Assign Teachers to Subjects and Classes
- View all system data

### Teacher Portal
- View teaching assignments
- Upload student results (bulk upload supported)
- Edit uploaded results

### Student Portal
- View personal profile
- View results with grades
- See position in class
- View total marks and average

## Tech Stack

**Backend:**
- FastAPI (Python)
- PostgreSQL
- SQLAlchemy
- JWT Authentication

**Frontend:**
- Svelte
- Axios
- Plain CSS

## Installation

### Backend Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file:
```
DATABASE_URL=postgresql://username:password@localhost:5432/school_management_db
```

4. Create database and run schema (see `schema.sql`)

5. Run backend:
```bash
uvicorn app.main:app --reload --port 8001
```

### Frontend Setup

1. Navigate to frontend:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run frontend:
```bash
npm run dev
```

Access the application at http://localhost:3000

## Default Credentials

Create your first admin user through the `/api/auth/register` endpoint or via Swagger docs at http://localhost:8001/docs

## License

MIT