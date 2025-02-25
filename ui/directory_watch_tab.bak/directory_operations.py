import os
import logging
from PyQt5.QtWidgets import QMessageBox

logger = logging.getLogger(__name__)

class DirectoryOperations:
    def __init__(self, parent):
        self.parent = parent

    def show_debug_info(self):
        """デバッグ情報を表示する"""
        main_window = None
        settings_tab = None
        debug_info = []
        
        # 親ウィジェットの検索
        parent = self.parent.parent()
        debug_info.append(f"Parent type: {type(parent).__name__}")
        
        while parent:
            debug_info.append(f"Checking parent: {type(parent).__name__}")
            if hasattr(parent, 'tabs'):
                main_window = parent
                debug_info.append(f"Found main window with {main_window.tabs.count()} tabs")
                break
            parent = parent.parent()
        
        # 設定タブの検索
        if main_window:
            for i in range(main_window.tabs.count()):
                tab = main_window.tabs.widget(i)
                tab_name = type(tab).__name__
                debug_info.append(f"Tab {i}: {tab_name} (obj_name: {tab.objectName()})")
                
                if tab_name == "SettingsTab" or tab.objectName() == "settings_tab":
                    settings_tab = tab
                    debug_info.append(f"Found settings tab at index {i}")
                    
                    # 設定タブの属性を確認
                    if hasattr(settings_tab, 'get_app_directory'):
                        debug_info.append(f"get_app_directory method exists")
                        dir_value = settings_tab.get_app_directory()
                        debug_info.append(f"get_app_directory returns: {dir_value}")
                    else:
                        debug_info.append("get_app_directory method NOT found")
                        
                    if hasattr(settings_tab, 'app_dir_edit'):
                        debug_info.append(f"app_dir_edit property exists")
                        if hasattr(settings_tab.app_dir_edit, 'text'):
                            dir_text = settings_tab.app_dir_edit.text()
                            debug_info.append(f"app_dir_edit.text returns: {dir_text}")
                    else:
                        debug_info.append("app_dir_edit property NOT found")
        else:
            debug_info.append("Main window NOT found")
        
        # 現在のディレクトリ情報
        debug_info.append(f"Current directory: {self.parent.directory}")
        
        # デバッグ情報をダイアログで表示
        QMessageBox.information(self.parent, "デバッグ情報", "\n".join(debug_info))
    def get_app_directory(self):
        """設定タブからアプリケーションディレクトリを取得"""
        try:
            # mainWindowへの参照を取得
            main_window = None
            parent = self.parent.parent()
            logger.debug(f"Initial parent type: {type(parent).__name__}")
            
            while parent:
                logger.debug(f"Checking parent type: {type(parent).__name__}")
                if hasattr(parent, 'tabs'):
                    main_window = parent
                    logger.debug(f"Found main window with {main_window.tabs.count()} tabs")
                    break
                parent = parent.parent()
            
            if main_window:
                # 設定タブを探す
                for i in range(main_window.tabs.count()):
                    tab = main_window.tabs.widget(i)
                    logger.debug(f"Tab {i} type: {type(tab).__name__}, objectName: {tab.objectName()}")
                    
                    if tab.objectName() == "settings_tab" or type(tab).__name__ == "SettingsTab":
                        logger.debug(f"Found settings tab at index {i}")
                        
                        # get_app_directoryメソッドがある場合はそれを使用
                        if hasattr(tab, 'get_app_directory'):
                            logger.debug("Using get_app_directory method from settings tab")
                            directory = tab.get_app_directory()
                            logger.debug(f"get_app_directory returned: {directory}")
                            if directory and os.path.exists(directory):
                                return directory
                        
                        # app_dir_editウィジェットがある場合はそれを使用
                        elif hasattr(tab, 'app_dir_edit'):
                            logger.debug("Using app_dir_edit from settings tab")
                            if hasattr(tab.app_dir_edit, 'text'):
                                directory = tab.app_dir_edit.text()
                                logger.debug(f"app_dir_edit.text returned: {directory}")
                                if directory and os.path.exists(directory):
                                    return directory
            else:
                logger.debug("Could not find main window")
                
        except Exception as e:
            logger.error(f"Error getting app directory: {e}")
            
        return None

    def check_app_directory(self):
        """アプリケーションディレクトリの変更を確認"""
        try:
            new_directory = self.get_app_directory()
            self.parent.debug_label.setText(f"デバッグ情報: 現在のディレクトリ = {self.parent.directory}, 新しいディレクトリ = {new_directory}")
            logger.debug(f"check_app_directory - current: {self.parent.directory}, new: {new_directory}")
            
            if new_directory and new_directory != self.parent.directory and os.path.exists(new_directory):
                logger.debug(f"Updating directory from {self.parent.directory} to {new_directory}")
                self.parent.directory = new_directory
                self.parent.watcher_thread.update_directory(new_directory)
                self.parent.info_label.setText(f"監視中: {self.parent.directory}")
                self.parent.previous_snapshot = self.get_directory_snapshot()
                self.parent.ui_ops.update_tree_view(set())
                self.parent.ui_ops.update_directory_list(new_directory)
        except Exception as e:
            logger.error(f"Error checking app directory: {e}")

    def get_directory_snapshot(self):
        """ディレクトリ内の可視ファイルのスナップショットを取得"""
        snapshot = {}
        try:
            for root, dirs, files in os.walk(self.parent.directory):
                # 隠しディレクトリを走査対象から除外
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for name in files:
                    # 隠しファイルを除外
                    if name.startswith('.'):
                        continue
                        
                    filepath = os.path.join(root, name)
                    rel_path = os.path.relpath(filepath, self.parent.directory)
                    snapshot[rel_path] = os.path.getmtime(filepath)
        except Exception as e:
            logger.error(f"Error getting directory snapshot: {e}")
        return snapshot
