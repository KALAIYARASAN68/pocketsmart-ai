@echo off
if not exist venv (
  echo Virtual environment not found. Run: py -m venv venv
  pause
  exit /b
)
call venv\Scripts\activate
python app.py
pause
