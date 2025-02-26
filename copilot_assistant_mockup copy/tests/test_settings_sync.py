import unittest
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QApplication, QWidget
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.main_tab.settings_sync import SettingsSync

class TestSettingsSync(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)

    def setUp(self):
        self.parent = QWidget()
        self.parent.terminal_output = MagicMock()
        self.parent.app_controller = MagicMock()
        self.settings_sync = SettingsSync(self.parent)

    def test_sync_settings_with_none_parent(self):
        """親がNoneの場合のテスト"""
        settings_sync = SettingsSync(None)
        # エラーを発生させずに終了することを確認
        settings_sync.sync_settings()

    def test_sync_settings_with_none_main_window(self):
        """メインウィンドウがNoneの場合のテスト"""
        with patch.object(self.settings_sync, 'get_main_window', return_value=None):
            # エラーを発生させずに終了することを確認
            self.settings_sync.sync_settings()

    def test_sync_settings_with_none_settings_tab(self):
        """設定タブがNoneの場合のテスト"""
        main_window = QWidget()
        main_window.setObjectName("MainWindow")
        with patch.object(self.settings_sync, 'get_main_window', return_value=main_window):
            # エラーを発生させずに終了することを確認
            self.settings_sync.sync_settings()

    def test_sync_settings_with_none_app_controller(self):
        """app_controllerがNoneの場合のテスト"""
        self.parent.app_controller = None
        main_window = QWidget()
        main_window.setObjectName("MainWindow")
        settings_tab = QWidget(main_window)
        settings_tab.setObjectName("settings_tab")
        settings_tab.get_app_directory = MagicMock(return_value="/test/dir")
        
        with patch.object(self.settings_sync, 'get_main_window', return_value=main_window):
            # エラーを発生させずに終了することを確認
            self.settings_sync.sync_settings()

    def tearDown(self):
        self.parent.deleteLater()

if __name__ == '__main__':
    unittest.main()
