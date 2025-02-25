from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget,
                           QTextEdit, QPlainTextEdit, QPushButton, QHBoxLayout)
from PyQt5.QtCore import QTimer, Qt
from ui.app_controller import AppController
from ui.main_tab.terminal_controller import TerminalController
from ui.main_tab.settings_sync import SettingsSync
import logging

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow")
        self._cleanup_in_progress = False
        self._controllers_initialized = False
        self._init_controllers()
        self._init_ui()
        logging.info("MainWindow initialized successfully")

    def _init_controllers(self):
        """コントローラーの初期化"""
        if self._controllers_initialized:
            return

        try:
            # 中央ウィジェットの作成
            self.central_widget = QWidget()
            self.setCentralWidget(self.central_widget)
            self.main_layout = QVBoxLayout(self.central_widget)

            # コントローラーの初期化
            self.app_controller = AppController(self)
            self.terminal_controller = TerminalController(self)
            self.settings_sync = SettingsSync(self)

            self._controllers_initialized = True
            logging.info("Controllers initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing controllers: {str(e)}")
            raise

    def _init_ui(self):
        """UIの初期化"""
        try:
            self.setWindowTitle("Copilot Assistant")
            self.resize(800, 600)
            
            # タブウィジェットの作成
            self.tab_widget = QTabWidget()
            self.main_layout.addWidget(self.tab_widget)

            # メインタブの作成
            self.main_tab = QWidget()
            self.main_tab_layout = QVBoxLayout(self.main_tab)
            
            # ターミナル出力エリアの作成
            self.terminal_output = QPlainTextEdit()
            self.terminal_output.setReadOnly(True)
            self.terminal_output.setMaximumBlockCount(1000)  # 表示行数の制限
            self.terminal_output.setObjectName("terminal_output")
            self.main_tab_layout.addWidget(self.terminal_output)

            # ターミナル入力エリアの作成
            input_layout = QHBoxLayout()
            self.terminal_input = QTextEdit()
            self.terminal_input.setMaximumHeight(100)
            self.terminal_input.setObjectName("terminal_input")
            input_layout.addWidget(self.terminal_input)

            # 実行ボタンの作成
            self.run_button = QPushButton("実行")
            self.run_button.clicked.connect(self._on_run_clicked)
            self.run_button.setMaximumWidth(100)
            input_layout.addWidget(self.run_button)

            self.main_tab_layout.addLayout(input_layout)

            # 設定タブの作成
            self.settings_tab = QWidget()
            self.settings_tab.setObjectName("settings_tab")
            self.settings_layout = QVBoxLayout(self.settings_tab)

            # タブの追加
            self.tab_widget.addTab(self.main_tab, "ターミナル")
            self.tab_widget.addTab(self.settings_tab, "設定")
            
            # キーボードショートカットの設定
            self.terminal_input.installEventFilter(self)
            
            logging.info("UI initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing UI: {str(e)}")
            raise

    def _on_run_clicked(self):
        """実行ボタンクリック時の処理"""
        try:
            if self.terminal_controller:
                self.terminal_controller.run_command()
        except Exception as e:
            logging.error(f"Error running command: {str(e)}")

    def eventFilter(self, obj, event):
        """イベントフィルター（ショートカットキー処理）"""
        if obj == self.terminal_input and event.type() == event.KeyPress:
            if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
                self._on_run_clicked()
                return True
        return super().eventFilter(obj, event)

    def cleanup(self):
        """クリーンアップ処理"""
        if self._cleanup_in_progress:
            logging.debug("Cleanup already in progress, skipping")
            return

        self._cleanup_in_progress = True
        try:
            if hasattr(self, 'terminal_controller') and self.terminal_controller:
                session_info = self.terminal_controller.get_session_info()
                logging.info(f"Session ending - Info: {session_info}")

                for controller in ['terminal_controller', 'app_controller', 'settings_sync']:
                    if hasattr(self, controller):
                        ctrl = getattr(self, controller)
                        if ctrl:
                            ctrl.deleteLater()
                            setattr(self, controller, None)

                self._controllers_initialized = False
                logging.info("Cleanup completed successfully", extra={'cleanup_id': id(self)})
        except Exception as e:
            logging.error(f"Error during cleanup: {str(e)}")
        finally:
            self._cleanup_in_progress = False

    def closeEvent(self, event):
        """ウィンドウクローズイベントのハンドリング"""
        try:
            self.cleanup()
            event.accept()
        except Exception as e:
            logging.error(f"Error during window close: {str(e)}")
            event.accept()

