# Coupon Management System

## Project Structure

```
coupon-system/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models/
│   │   ├── routes/
│   │   ├── utils/
│   │   └── config.py
│   ├── requirements.txt
│   ├── .env.example
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── utils/
│   │   └── hooks/
│   ├── package.json
│   └── .env.example
├── .gitignore
└── README.md
```

## Setup Instructions

### Backend
1. `cd backend`
2. `python -m venv venv`
3. `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Unix)
4. `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and fill in values
6. `python run.py` to start Flask server

### Frontend
1. `cd frontend`
2. `npm install`
3. Copy `.env.example` to `.env` and fill in values
4. `npm start` to run React app

## Tech Stack
- Backend: Flask, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-Mail, Flask-CORS, python-dotenv, bcrypt, SQLite
- Frontend: React, TailwindCSS, Axios, React Router DOM, React Hook Form, React Hot Toast

---

This is the initial project structure and setup. See future documentation for API and feature details.
