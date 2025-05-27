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
REM デバッグモードを有効にするには下記の行のコメントアウトを外してください
REM set EAGLE_DEBUG=true
set EAGLE_DEBUG=false

echo Starting server...
python -m uvicorn index:app --reload --host 0.0.0.0 --port 8000
