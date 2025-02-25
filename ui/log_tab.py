from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel

class LogTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.log_view = QTextEdit()

        layout.addWidget(QLabel("📊 ログ"))
        layout.addWidget(self.log_view)

        self.setLayout(layout)
