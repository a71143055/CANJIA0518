@echo off
echo CANJIA Web Application Starting...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Run the application
echo.
echo Starting Flask application...
echo Application will be available at http://localhost:5000
echo.
python app.py

pause
