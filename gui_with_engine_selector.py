"""
带有语音识别引擎选择功能的GUI界面
支持选择不同的语音识别服务
"""
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QTextEdit, QPushButton, QLabel, QComboBox,
                             QFrame, QMessageBox, QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

# 导入不同的语音识别器
from speech_recognizer import SpeechRecognizer
from baidu_speech_simple import BaiduSpeechSimple
from speech_recognizer_local import LocalSpeechRecognizer


class EngineGUI(QMainWindow):
    """极简语音转文字GUI"""
    
    def __init__(self):
        super().__init__()
        self.speech_recognizer = None
        self.is_always_on_top = False
        self.current_engine = 'baidu'  # 默认使用百度
        
        # 只保留三个核心语音识别引擎
        self.engines = {
            'baidu': {
                'name': '百度语音识别',
                'class': BaiduSpeechSimple,
                'description': '国内服务，中文识别效果好'
            },
            'google': {
                'name': 'Google语音识别',
                'class': SpeechRecognizer,
                'description': '国际服务，需要稳定网络'
            },
            'local': {
                'name': '本地语音识别',
                'class': LocalSpeechRecognizer,
                'description': '离线识别，无需网络'
            }
        }
        
        self.init_ui()
        self.init_speech_recognizer()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('🎙️ 语音转文字插件')
        self.setGeometry(100, 100, 600, 500)
        
        # 设置窗口图标
        self.setWindowIcon(QIcon('🎙️'))
        
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 创建引擎选择区域
        engine_group = QGroupBox("选择引擎")
        engine_layout = QGridLayout()
        engine_group.setLayout(engine_layout)
        
        # 引擎选择下拉框
        self.engine_selector = QComboBox()
        for key, engine in self.engines.items():
            self.engine_selector.addItem(engine['name'], key)
        self.engine_selector.setCurrentText(self.engines[self.current_engine]['name'])
        self.engine_selector.currentTextChanged.connect(self.change_engine)
        
        # 引擎描述标签
        self.engine_description = QLabel(self.engines[self.current_engine]['description'])
        self.engine_description.setWordWrap(True)
        self.engine_description.setStyleSheet("color: #666; font-size: 11px;")
        
        engine_layout.addWidget(QLabel("选择引擎:"), 0, 0)
        engine_layout.addWidget(self.engine_selector, 0, 1)
        engine_layout.addWidget(self.engine_description, 1, 0, 1, 2)
        
        main_layout.addWidget(engine_group)
        
        # 创建状态显示区域
        status_layout = QHBoxLayout()
        
        # 状态标签
        self.status_label = QLabel("🔌 等待连接...")
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                background-color: #f0f0f0;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        
        # 置顶按钮
        self.pin_button = QPushButton("📋")
        self.pin_button.setFixedSize(40, 40)
        self.pin_button.setToolTip("点击置顶窗口")
        self.pin_button.clicked.connect(self.toggle_always_on_top)
        self.pin_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                border: 2px solid #ddd;
                border-radius: 20px;
                background-color: #f8f8f8;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
            }
        """)
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.pin_button)
        
        main_layout.addLayout(status_layout)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        
        # 开始识别按钮
        self.start_button = QPushButton("🎤 开始语音识别")
        self.start_button.setFixedHeight(50)
        self.start_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.start_button.clicked.connect(self.start_recognition)
        
        # 停止识别按钮
        self.stop_button = QPushButton("⏹️ 结束语音识别")
        self.stop_button.setFixedHeight(50)
        self.stop_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #c1120a;
            }
        """)
        self.stop_button.clicked.connect(self.stop_recognition)
        self.stop_button.setEnabled(False)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        
        main_layout.addLayout(button_layout)
        
        # 创建文本显示区域
        text_group = QGroupBox("识别结果")
        text_layout = QVBoxLayout()
        text_group.setLayout(text_layout)
        
        # 文本编辑框
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("识别到的文字将显示在这里...")
        self.text_edit.setFont(QFont("Microsoft YaHei", 12))
        self.text_edit.setStyleSheet("""
            QTextEdit {
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 10px;
                line-height: 1.5;
            }
        """)
        
        text_layout.addWidget(self.text_edit)
        
        # 文本操作按钮
        text_button_layout = QHBoxLayout()
        
        # 清空按钮
        clear_button = QPushButton("🗑️ 清空文本")
        clear_button.clicked.connect(self.clear_text)
        clear_button.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: #ff9800;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        
        # 复制按钮
        copy_button = QPushButton("📋 复制文本")
        copy_button.clicked.connect(self.copy_text)
        copy_button.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        text_button_layout.addWidget(clear_button)
        text_button_layout.addWidget(copy_button)
        text_button_layout.addStretch()
        
        text_layout.addLayout(text_button_layout)
        
        main_layout.addWidget(text_group)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
    
    def init_speech_recognizer(self):
        """初始化语音识别器"""
        try:
            engine_config = self.engines[self.current_engine]
            
            # 创建语音识别器实例
            self.speech_recognizer = engine_config['class']()
            
            # 连接信号
            self.speech_recognizer.text_recognized.connect(self.on_text_recognized)
            self.speech_recognizer.error_occurred.connect(self.on_error_occurred)
            self.speech_recognizer.status_changed.connect(self.on_status_changed)
            
            self.status_label.setText(f"✅ {engine_config['name']} 已就绪")
            self.status_label.setStyleSheet("""
                QLabel {
                    padding: 8px;
                    background-color: #e8f5e8;
                    border: 1px solid #4CAF50;
                    border-radius: 4px;
                    font-weight: bold;
                    color: #2e7d32;
                }
            """)
            
            # 启用控制按钮
            self.start_button.setEnabled(True)
            
        except Exception as e:
            # 如果当前引擎初始化失败，尝试切换到百度引擎
            if self.current_engine != 'baidu':
                try:
                    self.current_engine = 'baidu'
                    self.engine_selector.setCurrentText(self.engines['baidu']['name'])
                    self.speech_recognizer = BaiduSpeechSimple()
                    
                    # 连接信号
                    self.speech_recognizer.text_recognized.connect(self.on_text_recognized)
                    self.speech_recognizer.error_occurred.connect(self.on_error_occurred)
                    self.speech_recognizer.status_changed.connect(self.on_status_changed)
                    
                    self.status_label.setText("✅ 百度语音识别已就绪")
                    self.start_button.setEnabled(True)
                    return
                except:
                    pass
            
            # 如果所有引擎都失败
            self.speech_recognizer = None
            self.status_label.setText("❌ 初始化失败")
            self.status_label.setStyleSheet("""
                QLabel {
                    padding: 8px;
                    background-color: #ffebee;
                    border: 1px solid #f44336;
                    border-radius: 4px;
                    font-weight: bold;
                    color: #c62828;
                }
            """)
            
            # 禁用控制按钮
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(False)
    
    def change_engine(self, engine_name):
        """切换语音识别引擎"""
        # 找到对应的引擎key
        for key, engine in self.engines.items():
            if engine['name'] == engine_name:
                self.current_engine = key
                break
        
        # 更新描述
        self.engine_description.setText(self.engines[self.current_engine]['description'])
        
        # 如果正在识别，先停止
        if self.speech_recognizer and self.speech_recognizer.is_listening:
            self.stop_recognition()
        
        # 重新初始化语音识别器
        self.init_speech_recognizer()
    
    def start_recognition(self):
        """开始语音识别"""
        if not self.speech_recognizer:
            self.status_label.setText("❌ 语音识别器未初始化")
            return
        
        try:
            self.speech_recognizer.start_listening()
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.engine_selector.setEnabled(False)
        except Exception as e:
            self.status_label.setText(f"❌ 启动失败: {str(e)}")
            print(f"启动语音识别失败: {str(e)}")
    
    def stop_recognition(self):
        """停止语音识别"""
        if self.speech_recognizer:
            self.speech_recognizer.stop_listening()
        self._reset_ui_state()
    
    def _reset_ui_state(self):
        """重置UI状态"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.engine_selector.setEnabled(True)
        self.status_label.setText(f"✅ {self.engines[self.current_engine]['name']} 已就绪")
    
    def on_text_recognized(self, text):
        """处理识别到的文本"""
        self.text_edit.append(text)
        # 自动滚动到底部
        cursor = self.text_edit.textCursor()
        cursor.movePosition(cursor.End)
        self.text_edit.setTextCursor(cursor)
    
    def on_error_occurred(self, error_message):
        """处理错误"""
        QMessageBox.warning(self, "错误", error_message)
        self._reset_ui_state()
    
    def on_status_changed(self, status):
        """处理状态变化"""
        status_icons = {
            '麦克风已就绪': '🎤',
            '麦克风已连接': '🎤',
            '开始监听': '🔴',
            '正在监听': '🔴',
            '请说话': '🗣️',
            '请继续说话': '🗣️',
            '正在识别': '🔄',
            '识别完成': '✅',
            '停止监听': '⏹️',
            '监听已停止': '⏹️'
        }
        
        # 查找匹配的状态图标
        icon = '🔌'
        for key, value in status_icons.items():
            if key in status:
                icon = value
                break
        
        self.status_label.setText(f"{icon} {status}")
        
        # 根据状态设置不同的颜色
        if '错误' in status or '失败' in status:
            self.status_label.setStyleSheet("""
                QLabel {
                    padding: 8px;
                    background-color: #ffebee;
                    border: 1px solid #f44336;
                    border-radius: 4px;
                    font-weight: bold;
                    color: #c62828;
                }
            """)
        elif '正在' in status or '请' in status:
            self.status_label.setStyleSheet("""
                QLabel {
                    padding: 8px;
                    background-color: #fff3e0;
                    border: 1px solid #ff9800;
                    border-radius: 4px;
                    font-weight: bold;
                    color: #f57c00;
                }
            """)
        else:
            self.status_label.setStyleSheet("""
                QLabel {
                    padding: 8px;
                    background-color: #e8f5e8;
                    border: 1px solid #4CAF50;
                    border-radius: 4px;
                    font-weight: bold;
                    color: #2e7d32;
                }
            """)
    
    def toggle_always_on_top(self):
        """切换窗口置顶状态"""
        self.is_always_on_top = not self.is_always_on_top
        
        if self.is_always_on_top:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.pin_button.setText("📌")
            self.pin_button.setToolTip("点击取消置顶")
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.pin_button.setText("📋")
            self.pin_button.setToolTip("点击置顶窗口")
        
        self.show()
    
    def clear_text(self):
        """清空文本"""
        self.text_edit.clear()
    
    def copy_text(self):
        """复制文本到剪贴板"""
        text = self.text_edit.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            QMessageBox.information(self, "提示", "文本已复制到剪贴板")
        else:
            QMessageBox.information(self, "提示", "没有可复制的文本")
    
    def closeEvent(self, event):
        """关闭事件处理"""
        if self.speech_recognizer and self.speech_recognizer.is_listening:
            self.speech_recognizer.stop_listening()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("语音转文字插件")
    
    # 设置应用程序图标
    app.setWindowIcon(QIcon('🎙️'))
    
    window = EngineGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main() 