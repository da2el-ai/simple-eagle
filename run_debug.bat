@echo off
IF NOT EXIST "venv" (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate
    echo Installing dependencies...
    pip install -r requirements.txt
) ELSE (
    call venv\Scripts\activate
)

echo Setting debug mode...
set EAGLE_DEBUG=true

echo Starting server in DEBUG mode...
python -m uvicorn index:app --reload --host 0.0.0.0 --port 8000
