#!/bin/bash

echo "Starting tests at $(date -u '+%Y-%m-%d %H:%M:%S') UTC"
echo "User: $USER"

# カレントディレクトリをPythonパスに追加
export PYTHONPATH="${PYTHONPATH:+${PYTHONPATH}:}$(pwd)"

echo "Running Settings Sync tests..."
python3 -m unittest tests.test_settings_sync -v

echo "Running Terminal Controller tests..."
python3 -m unittest tests.test_terminal_controller -v

echo "Tests completed at $(date -u '+%Y-%m-%d %H:%M:%S') UTC"
