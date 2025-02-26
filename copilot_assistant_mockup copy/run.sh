#!/bin/bash

# 環境変数の設定
export PYTHONUNBUFFERED=1
export PYTHONUTF8=1

# ログディレクトリの作成
mkdir -p logs

# タイムスタンプ付きのログファイル名を生成
timestamp=$(date +%Y%m%d_%H%M%S)
log_file="logs/app_${timestamp}.log"

# Pythonの仮想環境がある場合はアクティベート
# source venv/bin/activate  # 必要に応じてコメントを外す

# 必要なパッケージのインストール確認
pip install -r requirements.txt

# アプリケーションの実行
echo "Starting File Management Application..."
echo "Log file: ${log_file}"
python main.py 2>&1 | tee "${log_file}"