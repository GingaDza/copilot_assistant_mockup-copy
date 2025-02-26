import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from ui.main_window import MainWindow

def setup_logging():
    """ログ設定"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """メイン関数"""
    try:
        # ログ設定
        setup_logging()
        
        # アプリケーションの作成
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        
        # メインウィンドウの作成
        main_window = MainWindow()
        main_window.show()
        
        # 終了時のクリーンアップ
        def cleanup():
            if main_window:
                main_window.cleanup()
        
        app.aboutToQuit.connect(cleanup)
        
        # アプリケーションの実行
        return app.exec_()
        
    except Exception as e:
        logging.error(f"Application error: {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
