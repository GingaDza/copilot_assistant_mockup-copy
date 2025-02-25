import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTreeView, QFileSystemModel, QTextEdit, QSplitter
from PyQt5.QtCore import QDir

class FilesTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # ファイルツリー（QTreeView）
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(QDir.currentPath())  # 現在のディレクトリをルートに設定

        self.file_tree = QTreeView()
        self.file_tree.setModel(self.file_model)
        self.file_tree.setRootIndex(self.file_model.index(QDir.currentPath()))
        self.file_tree.doubleClicked.connect(self.open_file)

        # ファイルエディタ（QTextEdit）
        self.file_editor = QTextEdit()
        self.file_editor.setReadOnly(False)  # 編集可能にする場合は False

        # スプリッターで左右に配置（ツリー + エディタ）
        splitter = QSplitter()
        splitter.addWidget(self.file_tree)
        splitter.addWidget(self.file_editor)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        # レイアウトに追加
        layout.addWidget(QLabel("📂 プロジェクトのファイル"))
        layout.addWidget(splitter)

        self.setLayout(layout)

    def open_file(self, index):
        """ ユーザーがツリーでファイルを選択すると、内容をエディタで表示する """
        file_path = self.file_model.filePath(index)
        
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.file_editor.setText(content)
            except Exception as e:
                self.file_editor.setText(f"エラー: {str(e)}")
