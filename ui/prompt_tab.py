from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QTextEdit, QPushButton, QHBoxLayout

class PromptTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # 定型文リスト
        self.prompt_list = QListWidget()
        self.prompt_list.itemClicked.connect(self.load_prompt)

        # プロンプト入力欄
        self.prompt_editor = QTextEdit()
        self.prompt_editor.setPlaceholderText("ここに定型文を入力...")

        # ボタン
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("➕ 追加")
        self.add_button.clicked.connect(self.add_prompt)

        self.update_button = QPushButton("✏ 更新")
        self.update_button.clicked.connect(self.update_prompt)

        self.delete_button = QPushButton("🗑 削除")
        self.delete_button.clicked.connect(self.delete_prompt)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)

        # レイアウトに追加
        layout.addWidget(QLabel("📝 プロンプト定型文リスト"))
        layout.addWidget(self.prompt_list)
        layout.addWidget(QLabel("✍ 編集"))
        layout.addWidget(self.prompt_editor)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def add_prompt(self):
        text = self.prompt_editor.toPlainText().strip()
        if text:
            self.prompt_list.addItem(text)
            self.prompt_editor.clear()

    def update_prompt(self):
        selected_item = self.prompt_list.currentItem()
        if selected_item:
            selected_item.setText(self.prompt_editor.toPlainText().strip())

    def delete_prompt(self):
        selected_item = self.prompt_list.currentItem()
        if selected_item:
            self.prompt_list.takeItem(self.prompt_list.row(selected_item))

    def load_prompt(self, item):
        self.prompt_editor.setText(item.text())
