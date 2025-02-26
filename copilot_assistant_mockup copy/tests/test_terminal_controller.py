import unittest
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QApplication, QWidget
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.main_tab.terminal_controller import TerminalController

class TestTerminalController(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)

    def setUp(self):
        self.parent = QWidget()
        self.parent.terminal_input = MagicMock()
        self.parent.terminal_output = MagicMock()
        self.parent.app_controller = MagicMock()
        self.terminal_controller = TerminalController(self.parent)

    def test_run_command_with_none_parent(self):
        """親がNoneの場合のテスト"""
        terminal_controller = TerminalController(None)
        terminal_controller.run_command()

    def test_run_command_with_none_terminal_input(self):
        """terminal_inputがNoneの場合のテスト"""
        self.parent.terminal_input = None
        self.terminal_controller.run_command()

    def test_run_command_with_none_terminal_output(self):
        """terminal_outputがNoneの場合のテスト"""
        self.parent.terminal_output = None
        self.parent.terminal_input.toPlainText.return_value = "echo 'test'"
        self.terminal_controller.run_command()

    def test_run_command_with_none_app_controller(self):
        """app_controllerがNoneの場合のテスト"""
        self.parent.app_controller = None
        command = "echo 'test'"
        self.parent.terminal_input.toPlainText.return_value = command
        mock_result = MagicMock()
        mock_result.stdout = "test\n"
        mock_result.stderr = ""

        with patch('subprocess.run', return_value=mock_result):
            self.terminal_controller.run_command()

    def test_session_info(self):
        """セッション情報のテスト"""
        info = self.terminal_controller.get_session_info()
        self.assertIsInstance(info, dict)
        self.assertIn('init_time', info)
        self.assertIn('user', info)
        self.assertIn('current_dir', info)
        self.assertIn('last_command', info)

    def tearDown(self):
        self.parent.deleteLater()

if __name__ == '__main__':
    unittest.main()
