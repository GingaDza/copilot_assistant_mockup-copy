import os
import logging
import subprocess
from PyQt5.QtGui import QTextCharFormat, QColor

logger = logging.getLogger(__name__)

class UIOperations:
    def __init__(self, parent):
        self.parent = parent

    def update_directory_list(self, path):
        """ディレクトリ内の可視ファイルをリストに表示"""
        try:
            self.parent.dir_list.clear()
            for root, dirs, files in os.walk(path):
                # 隠しディレクトリを走査対象から除外
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for name in files:
                    # 隠しファイルを除外
                    if name.startswith('.'):
                        continue
                    
                    self.parent.dir_list.addItem(os.path.join(root, name))
        except Exception as e:
            logger.error(f"Error updating directory list: {e}")

    def update_tree_view(self, new_files):
        """ディレクトリツリーを更新し、可視ファイルのみ表示"""
        try:
            result = subprocess.run(
                ["tree", "-f", "--noreport", "-I", ".*"],
                capture_output=True,
                text=True,
                cwd=self.parent.directory
            )
            
            if result.returncode != 0:
                self.parent.tree_output.setPlainText("Error: tree command failed")
                return

            tree_output = result.stdout
            if not tree_output:
                self.parent.tree_output.setPlainText("No files found")
                return

            self.parent.tree_output.clear()
            cursor = self.parent.tree_output.textCursor()
            cursor.beginEditBlock()

            for line in tree_output.splitlines():
                format = QTextCharFormat()
                clean_line = line.replace("├── ./", "").replace("└── ./", "").replace("│   ./", "").strip()
                
                if clean_line in new_files:
                    format.setForeground(QColor(255, 20, 147))
                
                cursor.insertText(line + "\n", format)

            cursor.endEditBlock()

        except Exception as e:
            self.parent.tree_output.setPlainText(f"Error: {str(e)}")
