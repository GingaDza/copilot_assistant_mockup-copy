import os
import subprocess
import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QHBoxLayout, QPushButton, QSplitter, QPlainTextEdit
from PyQt5.QtCore import QThread, pyqtSignal, QFileSystemWatcher, QTimer
from PyQt5.QtGui import QTextCharFormat, QColor, QTextCursor

class DirectoryWatcher(QThread):
    directory_changed = pyqtSignal(str)

    def __init__(self, directory):
        super().__init__()
        self.directory = directory
        self.watcher = QFileSystemWatcher([self.directory])
        self.watcher.directoryChanged.connect(self.on_directory_changed)

    def on_directory_changed(self, path):
        self.directory_changed.emit(path)

class DirectoryWatchTab(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.info_label = QLabel("監視するディレクトリを選択してください")
        self.layout.addWidget(self.info_label)

        self.splitter = QSplitter(self)
        self.layout.addWidget(self.splitter)

        # デバッグメッセージの追加
        print("QSplitter initialized", file=sys.stderr)

        # 左側: 現在の要素
        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout(self.left_widget)

        self.dir_list = QListWidget()
        self.left_layout.addWidget(self.dir_list)

        button_layout = QHBoxLayout()
        self.start_watch_button = QPushButton("監視開始")
        self.stop_watch_button = QPushButton("監視停止")
        button_layout.addWidget(self.start_watch_button)
        button_layout.addWidget(self.stop_watch_button)
        self.left_layout.addLayout(button_layout)

        self.splitter.addWidget(self.left_widget)

        # デバッグメッセージの追加
        print("Left widget added", file=sys.stderr)

        # 右側: ディレクトリツリー
        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout(self.right_widget)

        self.tree_output = QPlainTextEdit()
        self.tree_output.setReadOnly(True)

        self.refresh_button = QPushButton("🔄 更新")
        self.refresh_button.clicked.connect(self.manual_refresh)

        self.right_layout.addWidget(QLabel("📁 ディレクトリツリー"))
        self.right_layout.addWidget(self.tree_output)
        self.right_layout.addWidget(self.refresh_button)

        self.splitter.addWidget(self.right_widget)

        # デバッグメッセージの追加
        print("Right widget added", file=sys.stderr)

        self.directory = os.getcwd()
        self.watcher_thread = DirectoryWatcher(self.directory)
        self.watcher_thread.directory_changed.connect(self.update_directory_list)
        self.watcher_thread.start()

        self.update_directory_list(self.directory)

        self.start_watch_button.clicked.connect(self.start_watching)
        self.stop_watch_button.clicked.connect(self.stop_watching)

        # 初期スナップショットの取得
        self.previous_snapshot = self.get_directory_snapshot()

        # 初期表示
        self.update_tree_view(set())

        # 監視タイマーの設定（5秒間隔）
        self.timer = QTimer(self)
        self.timer.setInterval(5000)
        self.timer.timeout.connect(self.check_for_changes)
        self.timer.start()

        # デバッグメッセージの追加
        print("DirectoryWatchTab initialization complete", file=sys.stderr)

    def get_directory_snapshot(self):
        """ディレクトリの状態を取得"""
        print("Getting directory snapshot", file=sys.stderr)
        snapshot = {}
        for root, dirs, files in os.walk(self.directory):
            for name in files:
                filepath = os.path.join(root, name)
                rel_path = os.path.relpath(filepath, self.directory)
                snapshot[rel_path] = os.path.getmtime(filepath)
        return snapshot

    def check_for_changes(self):
        """変更の検出"""
        print("Checking for changes", file=sys.stderr)
        current_snapshot = self.get_directory_snapshot()
        new_files = set(current_snapshot.keys()) - set(self.previous_snapshot.keys())
        
        if new_files:
            self.previous_snapshot = current_snapshot
            self.update_tree_view(new_files)

    def update_tree_view(self, new_files):
        """ツリー表示の更新"""
        print("Updating tree view", file=sys.stderr)
        try:
            # tree コマンドを実行し、相対パスで出力
            result = subprocess.run(
                ["tree", "-f", "--noreport"],
                capture_output=True,
                text=True,
                cwd=self.directory
            )
            
            if result.returncode != 0:
                print(f"Tree command failed with return code {result.returncode}", file=sys.stderr)
                return

            tree_output = result.stdout
            if not tree_output:
                print("No output from tree command", file=sys.stderr)
                return

            self.tree_output.clear()
            cursor = self.tree_output.textCursor()
            cursor.beginEditBlock()

            for line in tree_output.splitlines():
                format = QTextCharFormat()
                
                # パスの抽出（"├── ./" や "└── ./" などのプレフィックスを除去）
                clean_line = line.replace("├── ./", "").replace("└── ./", "").replace("│   ./", "").strip()
                
                # 新規ファイルの場合はピンク色に設定
                if clean_line in new_files:
                    format.setForeground(QColor(255, 20, 147))  # ディープピンク
                
                cursor.insertText(line + "\n", format)

            cursor.endEditBlock()

        except Exception as e:
            self.tree_output.setPlainText(f"Error: {str(e)}")
            print(f"Error updating tree view: {str(e)}", file=sys.stderr)

    def manual_refresh(self):
        """手動更新"""
        print("Manual refresh", file=sys.stderr)
        self.check_for_changes()

    def update_directory_list(self, path):
        print(f"Updating directory list for path: {path}", file=sys.stderr)
        self.dir_list.clear()
        for root, dirs, files in os.walk(path):
            for name in files:
                self.dir_list.addItem(os.path.join(root, name))

    def start_watching(self):
        self.watcher_thread.start()
        self.info_label.setText(f"監視中: {self.directory}")
        # デバッグメッセージの追加
        print(f"Started watching directory: {self.directory}", file=sys.stderr)

    def stop_watching(self):
        self.watcher_thread.terminate()
        self.info_label.setText("監視停止")
        # デバッグメッセージの追加
        print("Stopped watching directory", file=sys.stderr)