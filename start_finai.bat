@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo FinAI is not installed correctly. Run: python -m venv .venv && .venv\Scripts\pip install -r requirements.txt
  pause
  exit /b 1
)
.venv\Scripts\python.exe -m streamlit run app.py
pause
