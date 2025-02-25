import subprocess
import os
import logging
from PyQt5.QtCore import QObject
from datetime import datetime

class TerminalController(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent = parent
        self._current_dir = os.getcwd()
        self._last_command = None
        self._init_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        self._user = os.getenv('USER', 'GingaDza')

    def _safe_get_terminal_text(self):
        """ターミナル入力を安全に取得"""
        try:
            if (self._parent and 
                hasattr(self._parent, 'terminal_input') and 
                self._parent.terminal_input):
                text = self._parent.terminal_input.toPlainText().strip()
                return str(text) if text else ""
        except AttributeError:
            logging.debug("ターミナル入力の取得に失敗")
        return ""

    def _safe_append_output(self, text):
        """ターミナル出力を安全に追加"""
        try:
            if (self._parent and 
                hasattr(self._parent, 'terminal_output') and 
                self._parent.terminal_output):
                self._parent.terminal_output.appendPlainText(str(text))
        except AttributeError:
            logging.debug(f"ターミナル出力の追加に失敗: {text}")

    def get_app_directory(self):
        """アプリケーションディレクトリを安全に取得"""
        try:
            if (self._parent and 
                hasattr(self._parent, 'app_controller') and 
                self._parent.app_controller):
                dir_path = self._parent.app_controller.get_app_directory()
                if dir_path and os.path.isdir(str(dir_path)):
                    return str(dir_path)
        except Exception as e:
            logging.debug(f"ディレクトリ取得エラー: {str(e)}")
        return self._current_dir

    def run_command(self):
        """ターミナルコマンドを実行"""
        if not self._parent:
            return

        command = self._safe_get_terminal_text()
        if not command:
            return

        try:
            self._safe_append_output(f"$ {command}")
            
            # 作業ディレクトリの取得
            app_dir = self.get_app_directory()

            # コマンドが文字列であることを確認
            command = str(command)

            # コマンド実行
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=app_dir
            )
            
            # 出力の処理
            if result.stdout:
                self._safe_append_output(result.stdout.rstrip())
            if result.stderr:
                self._safe_append_output(f"Error: {result.stderr.rstrip()}")
            
            self._last_command = command
            
            # 入力クリア
            try:
                if self._parent.terminal_input:
                    self._parent.terminal_input.clear()
            except AttributeError:
                pass
            
        except Exception as e:
            error_msg = f"コマンド実行エラー: {str(e)}"
            logging.error(error_msg)
            self._safe_append_output(f"Error: {error_msg}")

    def get_session_info(self):
        """セッション情報を取得"""
        return {
            'init_time': self._init_time,
            'user': self._user,
            'current_dir': self._current_dir,
            'last_command': self._last_command
        }
