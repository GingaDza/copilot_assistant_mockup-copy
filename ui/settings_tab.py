import os
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QLineEdit, QFileDialog, QGroupBox,
                            QFormLayout, QCheckBox)
from PyQt5.QtCore import QSettings

class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = QSettings('GingaDza', 'CopilotAssistant')
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 情報表示エリア
        info_layout = QHBoxLayout()
        self.time_label = QLabel(f"Current UTC: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        self.user_label = QLabel(f"User: GingaDza")
        info_layout.addWidget(self.time_label)
        info_layout.addStretch()
        info_layout.addWidget(self.user_label)
        layout.addLayout(info_layout)

        # プロジェクト設定グループ
        project_group = QGroupBox("プロジェクト設定")
        project_layout = QFormLayout()

        # 開発中のアプリディレクトリ設定
        dir_layout = QHBoxLayout()
        self.app_dir_edit = QLineEdit()
        self.app_dir_edit.setPlaceholderText("開発中のアプリケーションのディレクトリを選択")
        self.app_dir_edit.setReadOnly(True)
        browse_btn = QPushButton("参照...")
        browse_btn.clicked.connect(self.browse_directory)
        dir_layout.addWidget(self.app_dir_edit)
        dir_layout.addWidget(browse_btn)
        project_layout.addRow("アプリケーションディレクトリ:", dir_layout)

        # 実行コマンド設定
        self.run_command_edit = QLineEdit()
        self.run_command_edit.setPlaceholderText("python main.py")
        project_layout.addRow("実行コマンド:", self.run_command_edit)

        # 自動起動設定
        self.auto_start_check = QCheckBox("アプリケーション監視時に自動起動")
        project_layout.addRow("", self.auto_start_check)

        project_group.setLayout(project_layout)
        layout.addWidget(project_group)

        # GitHub設定グループ
        github_group = QGroupBox("GitHub設定")
        github_layout = QFormLayout()
        
        self.repo_url_edit = QLineEdit()
        self.repo_url_edit.setPlaceholderText("https://github.com/username/repo")
        github_layout.addRow("リポジトリURL:", self.repo_url_edit)
        
        self.branch_edit = QLineEdit()
        self.branch_edit.setPlaceholderText("main")
        github_layout.addRow("デフォルトブランチ:", self.branch_edit)

        github_group.setLayout(github_layout)
        layout.addWidget(github_group)

        # 保存/リセットボタン
        button_layout = QHBoxLayout()
        save_btn = QPushButton("設定を保存")
        reset_btn = QPushButton("設定をリセット")
        save_btn.clicked.connect(self.save_settings)
        reset_btn.clicked.connect(self.reset_settings)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(reset_btn)
        layout.addLayout(button_layout)

        # 下部にスペースを追加
        layout.addStretch()

    def browse_directory(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "開発中のアプリケーションディレクトリを選択",
            os.path.expanduser("~"),
            QFileDialog.ShowDirsOnly
        )
        if dir_path:
            self.app_dir_edit.setText(dir_path)
            # main.pyの存在を確認
            if os.path.exists(os.path.join(dir_path, "main.py")):
                self.run_command_edit.setText("python main.py")

    def save_settings(self):
        self.settings.setValue('app_directory', self.app_dir_edit.text())
        self.settings.setValue('run_command', self.run_command_edit.text())
        self.settings.setValue('auto_start', self.auto_start_check.isChecked())
        self.settings.setValue('repo_url', self.repo_url_edit.text())
        self.settings.setValue('default_branch', self.branch_edit.text())
        self.settings.sync()

    def load_settings(self):
        self.app_dir_edit.setText(self.settings.value('app_directory', ''))
        self.run_command_edit.setText(self.settings.value('run_command', 'python main.py'))
        self.auto_start_check.setChecked(self.settings.value('auto_start', False, type=bool))
        self.repo_url_edit.setText(self.settings.value('repo_url', ''))
        self.branch_edit.setText(self.settings.value('default_branch', 'main'))

    def reset_settings(self):
        self.app_dir_edit.clear()
        self.run_command_edit.setText('python main.py')
        self.auto_start_check.setChecked(False)
        self.repo_url_edit.clear()
        self.branch_edit.setText('main')

    def get_app_directory(self):
        """他のタブからアプリケーションディレクトリを取得するためのメソッド"""
        return self.app_dir_edit.text()

    def get_run_command(self):
        """他のタブから実行コマンドを取得するためのメソッド"""
        return self.run_command_edit.text()