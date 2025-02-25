import os
import logging
from PyQt5.QtCore import QObject

class AppController(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent = parent
        self._app_directory = os.getcwd()
        self._run_command = "python main.py"
        self._init_time = self._get_current_time()
        logging.info(f"AppController initialized at {self._init_time}")

    def _get_current_time(self):
        """現在時刻を取得"""
        from datetime import datetime
        return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    def get_app_directory(self):
        """アプリケーションディレクトリを取得"""
        try:
            return self._app_directory
        except Exception as e:
            logging.error(f"Error getting app directory: {str(e)}")
            return os.getcwd()

    def set_app_directory(self, directory):
        """アプリケーションディレクトリを設定"""
        try:
            if directory and os.path.isdir(directory):
                self._app_directory = directory
                logging.info(f"App directory updated: {directory}")
                return True
        except Exception as e:
            logging.error(f"Error setting app directory: {str(e)}")
        return False

    def get_run_command(self):
        """実行コマンドを取得"""
        try:
            return self._run_command
        except Exception as e:
            logging.error(f"Error getting run command: {str(e)}")
            return "python main.py"

    def set_run_command(self, command):
        """実行コマンドを設定"""
        try:
            if command and isinstance(command, str):
                self._run_command = command
                logging.info(f"Run command updated: {command}")
                return True
        except Exception as e:
            logging.error(f"Error setting run command: {str(e)}")
        return False

    def get_session_info(self):
        """セッション情報を取得"""
        return {
            'init_time': self._init_time,
            'app_directory': self._app_directory,
            'run_command': self._run_command,
            'user': os.getenv('USER', 'GingaDza')
        }

    def validate_settings(self):
        """設定の検証"""
        is_valid = True
        errors = []

        # ディレクトリの検証
        if not os.path.isdir(self._app_directory):
            is_valid = False
            errors.append(f"Invalid directory: {self._app_directory}")

        # コマンドの検証
        if not isinstance(self._run_command, str) or not self._run_command.strip():
            is_valid = False
            errors.append("Invalid run command")

        if not is_valid:
            logging.warning(f"Settings validation failed: {errors}")
            self.restore_settings()  # 無効な場合は復元

        return is_valid
