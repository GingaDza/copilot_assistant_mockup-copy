import subprocess
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QListWidget, QPushButton, QLabel, QPlainTextEdit, QHBoxLayout

class MainTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # コードエディタ
        self.code_editor = QTextEdit()
        self.copilot_suggestions = QListWidget()
        approve_btn = QPushButton("✅ 承認")
        reject_btn = QPushButton("❌ 却下")

        # ターミナル部分
        self.terminal_output = QPlainTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_input = QPlainTextEdit()
        self.terminal_input.setPlaceholderText("ここにコマンドを入力...")
        run_btn = QPushButton("▶ 実行")
        run_btn.clicked.connect(self.run_command)

        # レイアウト配置
        layout.addWidget(QLabel("💻 コードエディタ"))
        layout.addWidget(self.code_editor)
        layout.addWidget(QLabel("💡 Copilot の提案"))
        layout.addWidget(self.copilot_suggestions)
        layout.addWidget(approve_btn)
        layout.addWidget(reject_btn)

        layout.addWidget(QLabel("🖥 ターミナル"))
        layout.addWidget(self.terminal_output)
        
        terminal_layout = QHBoxLayout()
        terminal_layout.addWidget(self.terminal_input)
        terminal_layout.addWidget(run_btn)
        layout.addLayout(terminal_layout)

        self.setLayout(layout)

    def run_command(self):
        command = self.terminal_input.toPlainText().strip()
        if command:
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output = result.stdout if result.stdout else result.stderr
                self.terminal_output.appendPlainText(f"$ {command}\n{output}\n")
            except Exception as e:
                self.terminal_output.appendPlainText(f"エラー: {str(e)}\n")
