import sys
import os

# 標準エラー出力をバッファリングせずに即時出力するように設定
sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', buffering=1)

# ログファイルにも出力する場合は以下のようにファイルを開く
class TeeStream:
    def __init__(self, stdout, logfile):
        self.stdout = stdout
        self.logfile = logfile
        
    def write(self, message):
        self.stdout.write(message)
        self.logfile.write(message)
        self.logfile.flush()
        
    def flush(self):
        self.stdout.flush()
        self.logfile.flush()

# ログファイルの設定
log_file = open('debug.log', 'a', encoding='utf-8')
sys.stderr = TeeStream(sys.stderr, log_file)