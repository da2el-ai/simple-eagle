#!/bin/bash

# 仮想環境が存在しない場合は作成
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

echo "Setting debug mode..."
# デバッグモードを有効にするには下記の行のコメントアウトを外してください
# export EAGLE_DEBUG=true
export EAGLE_DEBUG=false

echo "Starting server..."
python -m uvicorn index:app --reload --host 0.0.0.0 --port 8000
