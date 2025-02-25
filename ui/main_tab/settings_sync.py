from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import QObject, QTimer
import os
import logging

class SettingsSync(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent = parent
        self._last_app_dir = None
        self._last_run_command = None
        self._setup_timer()

    def _setup_timer(self):
        """同期タイマーの設定"""
        self._sync_timer = QTimer(self)
        self._sync_timer.timeout.connect(self.sync_settings)
        self._sync_timer.start(1000)  # 1秒ごとに同期

    def get_main_window(self):
        """メインウィンドウの取得"""
        try:
            if self._parent and isinstance(self._parent, QWidget):
                return self._parent
            
            app = QApplication.instance()
            if app:
                for widget in app.topLevelWidgets():
                    if widget.objectName() == "MainWindow":
                        return widget
        except Exception as e:
            logging.debug(f"Error getting main window: {str(e)}")
        return None

    def sync_settings(self):
        """設定の同期"""
        if not self._parent:
            return

        try:
            main_window = self.get_main_window()
            if not main_window:
                return

            settings_tab = main_window.findChild(QWidget, "settings_tab")
            if not settings_tab:
                return

            self._sync_app_directory(settings_tab)
            self._sync_run_command(settings_tab)

        except Exception as e:
            logging.error(f"Settings sync error: {str(e)}")

    def _sync_app_directory(self, settings_tab):
        """アプリケーションディレクトリの同期"""
        try:
            new_app_dir = getattr(settings_tab, 'get_app_directory', lambda: None)()
            if new_app_dir and new_app_dir != self._last_app_dir:
                self._last_app_dir = new_app_dir
                if os.path.isdir(new_app_dir):
                    if hasattr(self._parent, 'app_controller'):
                        self._parent.app_controller.set_app_directory(new_app_dir)
                        logging.info(f"App directory updated: {new_app_dir}")
        except Exception as e:
            logging.debug(f"Directory sync error: {str(e)}")

    def _sync_run_command(self, settings_tab):
        """実行コマンドの同期"""
        try:
            new_run_command = getattr(settings_tab, 'get_run_command', lambda: None)()
            if new_run_command and new_run_command != self._last_run_command:
                self._last_run_command = new_run_command
                if hasattr(self._parent, 'app_controller'):
                    self._parent.app_controller.set_run_command(new_run_command)
                    logging.info(f"Run command updated: {new_run_command}")
        except Exception as e:
            logging.debug(f"Command sync error: {str(e)}")

