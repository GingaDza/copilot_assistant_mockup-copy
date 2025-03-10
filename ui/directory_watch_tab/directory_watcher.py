import os
import logging
from PyQt5.QtCore import QThread, pyqtSignal, QFileSystemWatcher

# ロガーの設定
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DirectoryWatcher(QThread):
    directory_changed = pyqtSignal(str)
    is_running = True
    
    def __init__(self, directory):
        super().__init__()
        self.directory = directory
        self.watcher = QFileSystemWatcher([self.directory])
        self.watcher.directoryChanged.connect(self.on_directory_changed)
        logger.debug(f"DirectoryWatcher initialized with directory: {directory}")
    
    def run(self):
        """スレッドの実行メソッド"""
        logger.debug("DirectoryWatcher thread started")
        # スレッドのメインループ
        self.exec_()
    
    def stop(self):
        """スレッドを安全に停止させる"""
        logger.debug("Stopping DirectoryWatcher thread")
        self.is_running = False
        if self.watcher.directories():
            self.watcher.removePaths(self.watcher.directories())
        self.quit()
        self.wait()  # スレッドが終了するまで待機
        logger.debug("DirectoryWatcher thread stopped")

    def on_directory_changed(self, path):
        logger.debug(f"Directory changed: {path}")
        self.directory_changed.emit(path)

    def update_directory(self, new_directory):
        logger.debug(f"Updating directory watcher from {self.directory} to {new_directory}")
        if self.watcher.directories():
            self.watcher.removePaths(self.watcher.directories())
        self.directory = new_directory
        self.watcher.addPath(new_directory)