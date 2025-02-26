import os
import logging
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QListWidget, 
                           QHBoxLayout, QPushButton, QSplitter, QPlainTextEdit, QLineEdit)
from PyQt5.QtCore import QTimer, Qt

from .directory_watcher import DirectoryWatcher
from .operations import DirectoryOperations
from .ui_operations import UIOperations

# ロガーの設定
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DirectoryWatchTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("directory_watch_tab")
        logger.debug("Initializing DirectoryWatchTab")
        
        # UIコンポーネントのセットアップ
        self._setup_ui()
        
        # 各機能モジュールの初期化
        self.dir_ops = DirectoryOperations(self)
        self.ui_ops = UIOperations(self)
        
        # 設定タブからアプリケーションディレクトリを取得
        self.directory = os.getcwd()  # デフォルトとして現在のディレクトリを使用
        self.debug_label.setText(f"デバッグ情報: 初期ディレクトリ = {self.directory}")

        # 監視の設定
        self.watcher_thread = DirectoryWatcher(self.directory)
        self.watcher_thread.directory_changed.connect(self.ui_ops.update_directory_list)
        
        # 初期化
        self.previous_snapshot = {}
        self.ui_ops.update_tree_view(set())

        # 監視タイマーの設定（5秒間隔）
        self.timer = QTimer(self)
        self.timer.setInterval(5000)
        self.timer.timeout.connect(self.check_for_changes)
        self.timer.start()
        
        logger.debug("DirectoryWatchTab initialization complete")

    def _setup_ui(self):
        """UIコンポーネントのセットアップ"""
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        self.setLayout(self.main_layout)

        # 情報エリアの設定
        info_layout = QHBoxLayout()
        self.time_label = QLabel(f"UTC: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        self.user_label = QLabel("User: GingaDza")
        info_layout.addWidget(self.time_label)
        info_layout.addStretch()
        info_layout.addWidget(self.user_label)
        self.main_layout.addLayout(info_layout)

        # デバッグ用ラベル
        self.debug_label = QLabel("デバッグ情報: 初期化中...")
        self.main_layout.addWidget(self.debug_label)

        # メインスプリッター（水平分割）
        self.splitter = QSplitter(Qt.Horizontal)
        
        # 左側：ファイルリスト
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        self.dir_list = QListWidget()
        left_layout.addWidget(QLabel("📁 監視中のファイル"))
        left_layout.addWidget(self.dir_list)
        
        # ボタン
        self.start_watch_button = QPushButton("▶ 監視開始")
        self.stop_watch_button = QPushButton("⏹ 監視停止")
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_watch_button)
        button_layout.addWidget(self.stop_watch_button)
        left_layout.addLayout(button_layout)
        
        # 右側：ツリービュー
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        self.tree_command_input = QLineEdit()
        self.tree_command_input.setPlaceholderText("カスタム tree コマンドを入力...")
        right_layout.addWidget(self.tree_command_input)
        
        self.tree_output = QPlainTextEdit()
        self.tree_output.setReadOnly(True)
        right_layout.addWidget(self.tree_output)
        
        # スプリッターにウィジェットを追加
        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(right_widget)
        
        self.main_layout.addWidget(self.splitter)

    def check_for_changes(self):
        """ディレクトリの変更を確認"""
        try:
            current_snapshot = self.dir_ops.get_directory_snapshot()
            new_files = set(current_snapshot.keys()) - set(self.previous_snapshot.keys())
            
            if new_files:
                logger.debug(f"Detected {len(new_files)} new files")
                self.previous_snapshot = current_snapshot
                self.ui_ops.update_tree_view(new_files)
        except Exception as e:
            logger.error(f"Error checking for changes: {e}")

    def closeEvent(self, event):
        """ウィンドウが閉じられる時のイベント処理"""
        logger.debug("DirectoryWatchTab closeEvent called")
        try:
            if hasattr(self, 'timer'):
                self.timer.stop()
            if hasattr(self, 'watcher_thread'):
                self.watcher_thread.quit()
                self.watcher_thread.wait()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        event.accept()