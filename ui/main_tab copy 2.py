import subprocess
import os
import sys
import logging
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QListWidget, 
                            QPushButton, QLabel, QPlainTextEdit, QHBoxLayout,
                            QSplitter, QFrame)
from PyQt5.QtCore import Qt, QProcess, QTimer
from PyQt5.QtGui import QFont

class MainTab(QWidget):
    def __init__(self):
        super().__init__()
        self.process = None
        self.app_process = None
        self.init_ui()
        
        # 時刻更新用タイマー
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)  # 1秒ごとに更新

        # 設定同期用タイマー
        self.sync_timer = QTimer(self)
        self.sync_timer.timeout.connect(self.sync_settings)
        self.sync_timer.start(2000)  # 2秒ごとに設定を同期

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 上部情報エリア
        info_layout = QHBoxLayout()
        self.time_label = QLabel("UTC: 2025-02-25 10:27:22")
        self.user_label = QLabel("User: GingaDza")
        info_layout.addWidget(self.time_label)
        info_layout.addStretch()
        info_layout.addWidget(self.user_label)
        main_layout.addLayout(info_layout)

        # メインスプリッター
        splitter = QSplitter(Qt.Vertical)

        # 上部：プロンプトエリアとCopilot提案
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)

        prompt_label = QLabel("💭 プロンプト入力")
        top_layout.addWidget(prompt_label)

        self.code_editor = QTextEdit()
        self.code_editor.setPlaceholderText("ここにプロンプトを入力してください...\n\n例：\n- アプリケーションの新機能の提案\n- コードレビューの依頼\n- テストケースの生成\n- GitHub Actionsの設定提案")
        top_layout.addWidget(self.code_editor)

        suggestion_label = QLabel("💡 Copilot の提案")
        top_layout.addWidget(suggestion_label)

        self.copilot_suggestions = QListWidget()
        top_layout.addWidget(self.copilot_suggestions)

        button_layout = QHBoxLayout()
        approve_btn = QPushButton("✅ 承認")
        reject_btn = QPushButton("❌ 却下")
        save_template_btn = QPushButton("💾 テンプレート保存")
        button_layout.addWidget(approve_btn)
        button_layout.addWidget(reject_btn)
        button_layout.addWidget(save_template_btn)
        top_layout.addLayout(button_layout)

        # 下部：ターミナルと実行制御
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)

        terminal_label = QLabel("🖥 ターミナル")
        bottom_layout.addWidget(terminal_label)

        self.terminal_output = QPlainTextEdit()
        self.terminal_output.setReadOnly(True)
        font = QFont("Monospace")
        font.setStyleHint(QFont.TypeWriter)
        self.terminal_output.setFont(font)
        bottom_layout.addWidget(self.terminal_output)

        terminal_input_layout = QHBoxLayout()
        self.terminal_input = QPlainTextEdit()
        self.terminal_input.setMaximumHeight(60)
        self.terminal_input.setPlaceholderText("ここにコマンドを入力...")
        run_btn = QPushButton("▶ 実行")
        run_btn.clicked.connect(self.run_command)
        terminal_input_layout.addWidget(self.terminal_input)
        terminal_input_layout.addWidget(run_btn)
        bottom_layout.addLayout(terminal_input_layout)

        # セパレータ
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        bottom_layout.addWidget(separator)

        # アプリケーション制御ボタン
        app_control_label = QLabel("🚀 アプリケーション制御")
        bottom_layout.addWidget(app_control_label)

        app_control_layout = QHBoxLayout()
        self.start_app_btn = QPushButton("▶ アプリ起動")
        self.stop_app_btn = QPushButton("⬛ アプリ停止")
        self.restart_app_btn = QPushButton("🔄 再起動")
        
        self.start_app_btn.clicked.connect(self.start_application)
        self.stop_app_btn.clicked.connect(self.stop_application)
        self.restart_app_btn.clicked.connect(self.restart_application)
        
        app_control_layout.addWidget(self.start_app_btn)
        app_control_layout.addWidget(self.stop_app_btn)
        app_control_layout.addWidget(self.restart_app_btn)
        bottom_layout.addLayout(app_control_layout)

        # スプリッターにウィジェットを追加
        splitter.addWidget(top_widget)
        splitter.addWidget(bottom_widget)

        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        # 初期状態でボタンの状態を設定
        self.update_app_control_buttons()

    def sync_settings(self):
        """設定タブとの同期を実行"""
        try:
            settings_tab = self.parent().parent().findChild(QWidget, "settings_tab")
            if settings_tab:
                # アプリケーションディレクトリの同期
                new_app_dir = settings_tab.get_app_directory()
                current_app_dir = self.get_app_directory()
                
                if new_app_dir and new_app_dir != current_app_dir:
                    self.terminal_output.appendPlainText(f"アプリケーションディレクトリを更新: {new_app_dir}")
                    # ディレクトリの存在確認
                    if not os.path.exists(new_app_dir):
                        self.terminal_output.appendPlainText(f"警告: ディレクトリが存在しません: {new_app_dir}")
                    elif not os.path.isdir(new_app_dir):
                        self.terminal_output.appendPlainText(f"警告: 指定されたパスはディレクトリではありません: {new_app_dir}")
                
                # 実行コマンドの同期
                new_run_command = settings_tab.get_run_command()
                current_run_command = self.get_run_command()
                
                if new_run_command and new_run_command != current_run_command:
                    self.terminal_output.appendPlainText(f"実行コマンドを更新: {new_run_command}")
                    # コマンドの基本的な検証
                    if not any(cmd in new_run_command.split()[0] for cmd in ['python', 'python3', 'py']):
                        self.terminal_output.appendPlainText("警告: Pythonコマンドが見つかりません")
                
                # ボタンの状態を更新
                self.update_app_control_buttons()

        except Exception as e:
            self.terminal_output.appendPlainText(f"設定の同期エラー: {str(e)}")

    def update_app_control_buttons(self):
        """アプリケーション制御ボタンの状態を更新"""
        try:
            app_dir = self.get_app_directory()
            run_command = self.get_run_command()
            app_running = self.app_process is not None and self.app_process.state() == QProcess.Running

            # ボタンの状態を設定
            self.start_app_btn.setEnabled(not app_running and bool(app_dir) and bool(run_command))
            self.stop_app_btn.setEnabled(app_running)
            self.restart_app_btn.setEnabled(app_running)

            # ツールチップを設定
            if not app_dir:
                self.start_app_btn.setToolTip("アプリケーションディレクトリが設定されていません")
            elif not run_command:
                self.start_app_btn.setToolTip("実行コマンドが設定されていません")
            else:
                self.start_app_btn.setToolTip(f"実行: {run_command} (in {app_dir})")

        except Exception as e:
            self.terminal_output.appendPlainText(f"ボタン状態の更新エラー: {str(e)}")

    def update_datetime(self):
        """UTCの現在時刻を更新"""
        current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        self.time_label.setText(f"UTC: {current_time}")

    def get_app_directory(self):
        """設定タブからアプリケーションディレクトリを取得"""
        try:
            settings_tab = self.parent().parent().findChild(QWidget, "settings_tab")
            if settings_tab and hasattr(settings_tab, 'get_app_directory'):
                app_dir = settings_tab.get_app_directory()
                return app_dir if app_dir and os.path.isdir(app_dir) else None
        except Exception as e:
            self.terminal_output.appendPlainText(f"ディレクトリ取得エラー: {str(e)}")
        return None

    def get_run_command(self):
        """設定タブから実行コマンドを取得"""
        try:
            settings_tab = self.parent().parent().findChild(QWidget, "settings_tab")
            if settings_tab and hasattr(settings_tab, 'get_run_command'):
                return settings_tab.get_run_command()
        except Exception as e:
            self.terminal_output.appendPlainText(f"コマンド取得エラー: {str(e)}")
        return None

    def start_application(self):
        """アプリケーションを起動"""
        try:
            app_dir = self.get_app_directory()
            if not app_dir:
                self.terminal_output.appendPlainText(
                    "エラー: アプリケーションディレクトリが設定されていません。\n"
                    "設定タブで正しいディレクトリを設定してください。"
                )
                return

            if not os.path.exists(app_dir):
                self.terminal_output.appendPlainText(f"エラー: ディレクトリが存在しません: {app_dir}")
                return

            command = self.get_run_command()
            if not command:
                self.terminal_output.appendPlainText("エラー: 実行コマンドが設定されていません。")
                return

            if self.app_process is None or self.app_process.state() == QProcess.NotRunning:
                self.terminal_output.appendPlainText(f"アプリケーション起動を試行:\nディレクトリ: {app_dir}\nコマンド: {command}")
                
                self.app_process = QProcess()
                self.app_process.setWorkingDirectory(app_dir)
                
                # プロセス出力の接続
                self.app_process.readyReadStandardOutput.connect(
                    lambda: self.handle_process_output(self.app_process.readAllStandardOutput())
                )
                self.app_process.readyReadStandardError.connect(
                    lambda: self.handle_process_output(self.app_process.readAllStandardError())
                )
                
                # プロセス終了時のハンドラを設定
                self.app_process.finished.connect(self.handle_process_finished)
                
                # コマンドの実行
                program, *args = command.split()
                self.app_process.start(program, args)
                
                # 起動の確認
                if self.app_process.state() == QProcess.Running:
                    self.terminal_output.appendPlainText("アプリケーションが起動しました")
                    self.terminal_output.appendPlainText(f"プロセスID: {self.app_process.processId()}")
                else:
                    self.terminal_output.appendPlainText("アプリケーションの起動に失敗しました")
                
                self.update_app_control_buttons()

        except Exception as e:
            self.terminal_output.appendPlainText(f"起動エラー: {str(e)}\n{sys.exc_info()}")

    def handle_process_finished(self, exit_code, exit_status):
        """プロセス終了時の処理"""
        status_text = "正常終了" if exit_status == QProcess.NormalExit else "異常終了"
        self.terminal_output.appendPlainText(f"アプリケーションが終了しました（{status_text}、終了コード: {exit_code}）")
        self.app_process = None
        self.update_app_control_buttons()

    def stop_application(self):
       """アプリケーションを停止"""
    try:
        if self.app_process and self.app_process.state() == QProcess.Running:
            self.terminal_output.appendPlainText("アプリケーションを停止しています...")
            
            # プロセスIDを取得して表示
            pid = self.app_process.processId()
            self.terminal_output.appendPlainText(f"停止するプロセスID: {pid}")
            
            # OSに応じた停止処理
            if os.name == 'nt':  # Windows
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(pid)], 
                            capture_output=True)
            else:  # Unix系
                subprocess.run(['kill', '-9', str(pid)], 
                            capture_output=True)
            
            self.app_process.terminate()
            if self.app_process.waitForFinished(3000):  # 3秒待機
                self.terminal_output.appendPlainText("アプリケーションを停止しました")
                self.app_process = None
            else:
                self.app_process.kill()  # 強制終了
                self.terminal_output.appendPlainText("アプリケーションを強制終了しました")
                self.app_process = None
            
            self.update_app_control_buttons()
    except Exception as e:
        self.terminal_output.appendPlainText(f"停止エラー: {str(e)}")

    def restart_application(self):
        """アプリケーションを再起動"""
        self.stop_application()
        QTimer.singleShot(1000, self.start_application)

    def handle_process_output(self, data):
        """プロセス出力をターミナルに表示"""
        text = data.data().decode('utf-8', errors='replace')
        self.terminal_output.appendPlainText(text)

    def closeEvent(self, event):
        """ウィンドウが閉じられる時の処理"""
        if self.app_process and self.app_process.state() == QProcess.Running:
            self.stop_application()
        event.accept()