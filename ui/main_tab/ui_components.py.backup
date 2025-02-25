from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QListWidget, 
                            QPushButton, QLabel, QPlainTextEdit, QHBoxLayout,
                            QSplitter, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class UIComponents:
    def __init__(self, parent):
        self.parent = parent
        self.init_components()

    def init_components(self):
        self.main_widget = QWidget()
        main_layout = QVBoxLayout(self.main_widget)

        # メインスプリッター
        self.splitter = QSplitter(Qt.Vertical)

        # 上部と下部のウィジェットを作成
        top_widget = self.create_top_widget()
        bottom_widget = self.create_bottom_widget()

        # スプリッターに追加
        self.splitter.addWidget(top_widget)
        self.splitter.addWidget(bottom_widget)
        
        # 1:1の比率に設定
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)

        main_layout.addWidget(self.splitter)

    def get_main_widget(self):
        return self.main_widget

    def create_top_widget(self):
        top_widget = QWidget()
        layout = QVBoxLayout(top_widget)

        # プロンプト入力エリア
        prompt_label = QLabel("💭 プロンプト入力")
        layout.addWidget(prompt_label)

        self.parent.code_editor = QTextEdit()
        self.parent.code_editor.setPlaceholderText(
            "ここにプロンプトを入力してください...\n\n"
            "例：\n"
            "- アプリケーションの新機能の提案\n"
            "- コードレビューの依頼\n"
            "- テストケースの生成\n"
            "- GitHub Actionsの設定提案"
        )
        layout.addWidget(self.parent.code_editor)

        # Copilot提案エリア
        suggestion_label = QLabel("💡 Copilot の提案")
        layout.addWidget(suggestion_label)

        self.parent.copilot_suggestions = QListWidget()
        layout.addWidget(self.parent.copilot_suggestions)

        # 操作ボタン
        button_layout = QHBoxLayout()
        approve_btn = QPushButton("✅ 承認")
        reject_btn = QPushButton("❌ 却下")
        save_template_btn = QPushButton("💾 テンプレート保存")
        button_layout.addWidget(approve_btn)
        button_layout.addWidget(reject_btn)
        button_layout.addWidget(save_template_btn)
        layout.addLayout(button_layout)

        return top_widget

    def create_bottom_widget(self):
        bottom_widget = QWidget()
        layout = QVBoxLayout(bottom_widget)

        # ターミナルエリア
        terminal_label = QLabel("🖥 ターミナル")
        layout.addWidget(terminal_label)

        self.parent.terminal_output = QPlainTextEdit()
        self.parent.terminal_output.setReadOnly(True)
        font = QFont("Monospace")
        font.setStyleHint(QFont.TypeWriter)
        self.parent.terminal_output.setFont(font)
        layout.addWidget(self.parent.terminal_output)

        # ターミナル入力エリア
        terminal_input_layout = QHBoxLayout()
        self.parent.terminal_input = QPlainTextEdit()
        self.parent.terminal_input.setMaximumHeight(60)
        self.parent.terminal_input.setPlaceholderText("ここにコマンドを入力...")
        
        run_btn = QPushButton("▶ 実行")
        run_btn.clicked.connect(lambda: self.parent.terminal_controller.run_command())
        
        terminal_input_layout.addWidget(self.parent.terminal_input)
        terminal_input_layout.addWidget(run_btn)
        layout.addLayout(terminal_input_layout)

        # セパレータ
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        # アプリケーション制御エリア
        app_control_label = QLabel("🚀 アプリケーション制御")
        layout.addWidget(app_control_label)

        app_control_layout = QHBoxLayout()
        self.parent.start_app_btn = QPushButton("▶ アプリ起動")
        self.parent.stop_app_btn = QPushButton("⬛ アプリ停止")
        self.parent.restart_app_btn = QPushButton("🔄 再起動")

        self.parent.start_app_btn.clicked.connect(self.parent.app_controller.start_application)
        self.parent.stop_app_btn.clicked.connect(self.parent.app_controller.stop_application)
        self.parent.restart_app_btn.clicked.connect(self.parent.app_controller.restart_application)

        app_control_layout.addWidget(self.parent.start_app_btn)
        app_control_layout.addWidget(self.parent.stop_app_btn)
        app_control_layout.addWidget(self.parent.restart_app_btn)
        layout.addLayout(app_control_layout)

        return bottom_widget
