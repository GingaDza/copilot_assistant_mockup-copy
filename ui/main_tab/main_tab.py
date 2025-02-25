import subprocess
import os
import sys
import logging
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QListWidget, 
                            QPushButton, QLabel, QPlainTextEdit, QHBoxLayout,
                            QSplitter, QFrame)
from PyQt5.QtCore import Qt, QProcess, QTimer
from PyQt5.QtGui import QFont

from .ui_components import UIComponents
from .app_controller import AppController
from .settings_sync import SettingsSync
from .terminal_controller import TerminalController

class MainTab(QWidget):
    def __init__(self):
        super().__init__()
        self.process = None
        self.app_process = None
        
        # コントローラーの初期化（UIの前に行う）
        self.app_controller = AppController(self)
        self.terminal_controller = TerminalController(self)
        self.settings_sync = SettingsSync(self)
        
        # UI初期化
        self.ui = UIComponents(self)
        self.init_ui()
        
        # 時刻更新用タイマー
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)  # 1秒ごとに更新

        # 設定同期用タイマー
        self.sync_timer = QTimer(self)
        self.sync_timer.timeout.connect(self.settings_sync.sync_settings)
        self.sync_timer.start(2000)  # 2秒ごとに設定を同期

        # 初期状態の設定
        self.update_datetime()
        self.app_controller.update_app_control_buttons()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 上部情報エリア
        info_layout = QHBoxLayout()
        self.time_label = QLabel("UTC: 2025-02-25 11:00:52")
        self.user_label = QLabel("User: GingaDza")
        info_layout.addWidget(self.time_label)
        info_layout.addStretch()
        info_layout.addWidget(self.user_label)
        main_layout.addLayout(info_layout)

        # メインスプリッター
        splitter = QSplitter(Qt.Vertical)

        # UIコンポーネントをレイアウトに追加
        main_layout.addWidget(self.ui.get_main_widget())
        self.setLayout(main_layout)

    def update_datetime(self):
        """UTCの現在時刻を更新"""
        current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        self.time_label.setText(f"UTC: {current_time}")

    def closeEvent(self, event):
        """ウィンドウが閉じられる時の処理"""
        if self.app_process and self.app_process.state() == QProcess.Running:
            self.app_controller.stop_application()
        event.accept()
