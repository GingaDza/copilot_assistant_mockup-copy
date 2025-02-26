import sys
import logging
from datetime import datetime

# ロギングの基本設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('debug.log', mode='a')
    ]
)

def main():
    print("Standard output test", flush=True)
    print("Standard error test", file=sys.stderr, flush=True)
    logging.debug("Debug message test")
    logging.info("Info message test")
    logging.error("Error message test")
    
    # 現在時刻を出力して、スクリプトが実際に実行されていることを確認
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Current time: {current_time}", flush=True)

if __name__ == "__main__":
    main()