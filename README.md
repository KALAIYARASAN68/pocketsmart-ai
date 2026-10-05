# PocketSmart AI

PocketSmart AI is a Flask + SQLite + Google Gemini powered budgeting and recommendation web application.

## Your Python version
Your PC has Python 3.7.9. This project is kept compatible with Python 3.7.9 and uses the Gemini REST API through `requests` rather than requiring a newer Google AI SDK.

## Features
- Registration and login
- Home Interior, Party and Jewelry planners
- AI budget allocation and recommendations
- Optional jewelry/outfit image upload
- Recommendation history
- Shopping/search links for Amazon, Flipkart, IKEA, Myntra, Swiggy, Zomato and OYO
- SQLite database
- Flask sessions
- `.env` API-key configuration
- Demo mode if Gemini is not configured
- Responsive frontend

## Folder structure
```text
PocketSmart_AI/
├── app.py
├── requirements.txt
├── .env.example
├── README.md
├── run.bat
├── database/schema.sql
├── backend/
│   ├── __init__.py
│   ├── config.py
│   ├── db.py
│   ├── auth.py
│   ├── gemini_service.py
│   ├── recommendation_service.py
│   └── utils.py
├── frontend/
│   ├── templates/
│   └── static/
├── uploads/
└── instance/
```

## Windows PowerShell setup

### 1. Extract ZIP and enter folder
```powershell
cd C:\path\to\PocketSmart_AI
```

### 2. Check Python
```powershell
py --version
```
Expected: `Python 3.7.9`

### 3. Create virtual environment
```powershell
py -m venv venv
```

Activate:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### 4. Install packages
```powershell
python -m pip install --upgrade "pip<24.1"
pip install -r requirements.txt
```

### 5. Create `.env`
```powershell
Copy-Item .env.example .env
notepad .env
```
Add your Gemini API key:
```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```
The model is configurable. Example:
```env
GEMINI_MODEL=gemini-1.5-flash
```

### 6. Run
```powershell
python app.py
```
Open: `http://127.0.0.1:5000`

## Demo mode
If no API key is configured, the application still works using sample recommendation logic. After the UI/database is tested, configure Gemini for real AI responses.

## Database
SQLite is automatically created at `instance/pocketsmart.db`. No XAMPP/MySQL is required.

## Architecture mapping
Your supplied AWS diagram maps conceptually to this local version as follows:
- Flask = backend/API
- SQLite = local database
- uploads/ = development equivalent of S3
- `.env` = development equivalent of Secrets Manager
- Flask session/auth = local access control
- Python logging = local monitoring equivalent
- Gemini REST API = GenAI engine
- Shopping URL generator = external platform integration layer

This is a student/local implementation. AWS deployment can be added after the local version works.
