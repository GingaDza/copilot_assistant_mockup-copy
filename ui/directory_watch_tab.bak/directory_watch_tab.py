import os
import logging
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QListWidget, 
                            QHBoxLayout, QPushButton, QSplitter, QPlainTextEdit)
from PyQt5.QtCore import QTimer, Qt

from .directory_watcher import DirectoryWatcher
from .directory_operations import DirectoryOperations
from .ui_operations import UIOperations

# ロガーの設定
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levellevel)s - %(message)s')
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
        self.directory = self.dir_ops.get_app_directory()
        logger.debug(f"Initial directory from settings: {self.directory}")
        if not self.directory:
            self.directory = os.getcwd()  # デフォルトとして現在のディレクトリを使用
            logger.debug(f"Using current working directory as fallback: {self.directory}")
        self.debug_label.setText(f"デバッグ情報: 初期ディレクトリ = {self.directory}")

        # 監視の設定
        self.watcher_thread = DirectoryWatcher(self.directory)
        self.watcher_thread.directory_changed.connect(self.ui_ops.update_directory_list)
        self.watcher_thread.start()

        # シグナル接続
        self.start_watch_button.clicked.connect(self.start_watching)
        self.stop_watch_button.clicked.connect(self.stop_watching)

        # 初期化
        self.previous_snapshot = self.dir_ops.get_directory_snapshot()
        self.ui_ops.update_tree_view(set())

        # 監視タイマーの設定（5秒間隔）
        self.timer = QTimer(self)
        self.timer.setInterval(5000)
        self.timer.timeout.connect(self.check_for_changes)
        self.timer.start()

        # 設定の更新を確認するタイマー
        self.settings_timer = QTimer(self)
        self.settings_timer.setInterval(5000)
        self.settings_timer.timeout.connect(self.check_app_directory)
        self.settings_timer.start()
        
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

        # デバッグ用ラベルの追加
        self.debug_label = QLabel("デバッグ情報: 初期化中...")
        self.debug_label.setStyleSheet("color: blue;")
        self.main_layout.addWidget(self.debug_label)

        # 情報ラベルの追加
        self.info_label = QLabel("監視するディレクトリを選択してください")
        self.main_layout.addWidget(self.info_label)

        # メインスプリッターの作成（水平分割）
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.main_splitter)

        # スプリッターがレイアウトの残りのスペースを占めるように設定
        self.main_layout.setStretch(1, 1)

        # 左側のウィジェット
        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout(self.left_widget)
        self.left_layout.setContentsMargins(5, 5, 5, 5)
        self.left_layout.setSpacing(5)

        # ファイルリストの追加
        self.dir_list = QListWidget()
        self.dir_list.setMinimumHeight(400)  # 最小の高さを設定
        self.left_layout.addWidget(self.dir_list)

        # ボタンレイアウトの設定
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.start_watch_button = QPushButton("監視開始")
        self.stop_watch_button = QPushButton("監視停止")
        self.debug_button = QPushButton("デバッグ情報")
        self.debug_button.clicked.connect(self.show_debug_info)

        button_layout.addWidget(self.start_watch_button)
        button_layout.addWidget(self.stop_watch_button)
        button_layout.addWidget(self.debug_button)
        self.left_layout.addLayout(button_layout)

        # 右側のウィジェット
        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout(self.right_widget)
        self.right_layout.setContentsMargins(5, 5, 5, 5)
        self.right_layout.setSpacing(5)

        # ツリービューのラベルとウィジェット
        self.tree_label = QLabel("📁 ディレクトリツリー")
        self.right_layout.addWidget(self.tree_label)

        self.tree_output = QPlainTextEdit()
        self.tree_output.setReadOnly(True)
        self.tree_output.setMinimumHeight(400)  # 最小の高さを設定
        self.right_layout.addWidget(self.tree_output)

        # 更新ボタン
        self.refresh_button = QPushButton("🔄 更新")
        self.refresh_button.clicked.connect(self.manual_refresh)
        self.right_layout.addWidget(self.refresh_button)

        # スプリッターにウィジェットを追加
        self.main_splitter.addWidget(self.left_widget)
        self.main_splitter.addWidget(self.right_widget)

        # スプリッターの初期サイズ比率を設定（1:1）
        self.main_splitter.setStretchFactor(0, 1)
        self.main_splitter.setStretchFactor(1, 1)

    def show_debug_info(self):
        """デバッグ情報を表示する"""
        self.dir_ops.show_debug_info()

    def check_app_directory(self):
        """アプリケーションディレクトリの変更を確認"""
        self.dir_ops.check_app_directory()
        
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

    def manual_refresh(self):
        """手動更新"""
        try:
            self.check_for_changes()
        except Exception as e:
            logger.error(f"Error during manual refresh: {e}")

    def start_watching(self):
        """監視を開始する"""
        try:
            self.watcher_thread.start()
            self.info_label.setText(f"監視中: {self.directory}")
        except Exception as e:
            logger.error(f"Error starting watch: {e}")

    def stop_watching(self):
        """監視を停止する"""
        try:
            if hasattr(self, "watcher_thread") and self.watcher_thread.isRunning():
                self.watcher_thread.quit()
                self.watcher_thread.wait(1000)  # 最大1秒待機
            self.info_label.setText("監視停止")
        except Exception as e:
            logger.error(f"Error stopping watch: {e}")

    def resizeEvent(self, event):
        """ウィンドウのリサイズイベント処理"""
        super().resizeEvent(event)
        # ウィンドウのリサイズ時にスプリッターの比率を維持
        self.main_splitter.setSizes([self.width() // 2, self.width() // 2])

    def closeEvent(self, event):
        """ウィンドウが閉じられる時のイベント処理"""
        logger.debug("DirectoryWatchTab closeEvent called")
        try:
            # タイマーを停止
            if hasattr(self, 'timer') and self.timer.isActive():
                self.timer.stop()
            if hasattr(self, 'settings_timer') and self.settings_timer.isActive():
                self.settings_timer.stop()
                
            # ウォッチャースレッドを停止
            if hasattr(self, 'watcher_thread'):
                self.stop_watching()
                
            logger.debug("DirectoryWatchTab resources cleaned up")
        except Exception as e:
            logger.error(f"Error during DirectoryWatchTab cleanup: {e}")
        event.accept()