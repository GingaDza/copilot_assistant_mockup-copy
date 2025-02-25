import os
import subprocess
from PyQt5.QtCore import QProcess, QTimer

class AppController:
    def __init__(self, parent):
        self.parent = parent

    def update_app_control_buttons(self):
        """アプリケーション制御ボタンの状態を更新"""
        try:
            app_dir = self.get_app_directory()
            run_command = self.get_run_command()
            app_running = self.parent.app_process is not None and self.parent.app_process.state() == QProcess.Running

            # ボタンの状態を設定
            self.parent.start_app_btn.setEnabled(not app_running and bool(app_dir) and bool(run_command))
            self.parent.stop_app_btn.setEnabled(app_running)
            self.parent.restart_app_btn.setEnabled(app_running)

            # ツールチップを設定
            if not app_dir:
                self.parent.start_app_btn.setToolTip("アプリケーションディレクトリが設定されていません")
            elif not run_command:
                self.parent.start_app_btn.setToolTip("実行コマンドが設定されていません")
            else:
                self.parent.start_app_btn.setToolTip(f"実行: {run_command} (in {app_dir})")

        except Exception as e:
            self.parent.terminal_output.appendPlainText(f"ボタン状態の更新エラー: {str(e)}")

    def get_app_directory(self):
        """設定タブからアプリケーションディレクトリを取得"""
        try:
            settings_tab = self.parent.parent().parent().findChild(QWidget, "settings_tab")
            if settings_tab and hasattr(settings_tab, 'get_app_directory'):
                app_dir = settings_tab.get_app_directory()
                return app_dir if app_dir and os.path.isdir(app_dir) else None
        except Exception as e:
            self.parent.terminal_output.appendPlainText(f"ディレクトリ取得エラー: {str(e)}")
        return None

    def get_run_command(self):
        """設定タブから実行コマンドを取得"""
        try:
            settings_tab = self.parent.parent().parent().findChild(QWidget, "settings_tab")
            if settings_tab and hasattr(settings_tab, 'get_run_command'):
                return settings_tab.get_run_command()
        except Exception as e:
            self.parent.terminal_output.appendPlainText(f"コマンド取得エラー: {str(e)}")
        return None

    def start_application(self):
        """アプリケーションを起動"""
        try:
            app_dir = self.get_app_directory()
            if not app_dir:
                self.parent.terminal_output.appendPlainText(
                    "エラー: アプリケーションディレクトリが設定されていません。\n"
                    "設定タブで正しいディレクトリを設定してください。"
                )
                return

            command = self.get_run_command()
            if not command:
                self.parent.terminal_output.appendPlainText("エラー: 実行コマンドが設定されていません。")
                return

            if self.parent.app_process is None or self.parent.app_process.state() == QProcess.NotRunning:
                self.parent.terminal_output.appendPlainText(
                    f"アプリケーション起動を試行:\n"
                    f"ディレクトリ: {app_dir}\n"
                    f"コマンド: {command}"
                )
                
                self.parent.app_process = QProcess()
                self.parent.app_process.setWorkingDirectory(app_dir)
                
                # プロセス出力の接続
                self.parent.app_process.readyReadStandardOutput.connect(
                    lambda: self.handle_process_output(self.parent.app_process.readAllStandardOutput())
                )
                self.parent.app_process.readyReadStandardError.connect(
                    lambda: self.handle_process_output(self.parent.app_process.readAllStandardError())
                )
                
                # プロセス終了時のハンドラを設定
                self.parent.app_process.finished.connect(self.handle_process_finished)
                
                # コマンドの実行
                program, *args = command.split()
                self.parent.app_process.start(program, args)
                
                # 起動の確認
                if self.parent.app_process.state() == QProcess.Running:
                    self.parent.terminal_output.appendPlainText("アプリケーションが起動しました")
                    self.parent.terminal_output.appendPlainText(f"プロセスID: {self.parent.app_process.processId()}")
                else:
                    self.parent.terminal_output.appendPlainText("アプリケーションの起動に失敗しました")
                
                self.update_app_control_buttons()

        except Exception as e:
            self.parent.terminal_output.appendPlainText(f"起動エラー: {str(e)}")

    def stop_application(self):
        """アプリケーションを停止"""
        try:
            if self.parent.app_process and self.parent.app_process.state() == QProcess.Running:
                self.parent.terminal_output.appendPlainText("アプリケーションを停止しています...")
                
                # プロセスIDを取得して表示
                pid = self.parent.app_process.processId()
                self.parent.terminal_output.appendPlainText(f"停止するプロセスID: {pid}")
                
                # OSに応じた停止処理
                if os.name == 'nt':  # Windows
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(pid)], 
                                capture_output=True)
                else:  # Unix系
                    subprocess.run(['kill', '-9', str(pid)], 
                                capture_output=True)
                
                self.parent.app_process.terminate()
                if self.parent.app_process.waitForFinished(3000):  # 3秒待機
                    self.parent.terminal_output.appendPlainText("アプリケーションを停止しました")
                    self.parent.app_process = None
                else:
                    self.parent.app_process.kill()  # 強制終了
                    self.parent.terminal_output.appendPlainText("アプリケーションを強制終了しました")
                    self.parent.app_process = None
                
                self.update_app_control_buttons()

        except Exception as e:
            self.parent.terminal_output.appendPlainText(f"停止エラー: {str(e)}")

    def restart_application(self):
        """アプリケーションを再起動"""
        self.stop_application()
        QTimer.singleShot(1000, self.start_application)

    def handle_process_output(self, data):
        """プロセス出力をターミナルに表示"""
        text = data.data().decode('utf-8', errors='replace')
        self.parent.terminal_output.appendPlainText(text)

    def handle_process_finished(self, exit_code, exit_status):
        """プロセス終了時の処理"""
        status_text = "正常終了" if exit_status == QProcess.NormalExit else "異常終了"
        self.parent.terminal_output.appendPlainText(
            f"アプリケーションが終了しました（{status_text}、終了コード: {exit_code}）"
        )
        self.parent.app_process = None
        self.update_app_control_buttons()
