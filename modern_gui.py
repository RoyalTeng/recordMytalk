"""
现代化语音转文字GUI - TDesign风格
基于PyQt5，不依赖WebEngine
"""
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QTextEdit, QPushButton, QLabel, QComboBox,
                             QFrame, QMessageBox, QSizePolicy, QSpacerItem)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QPainter, QPen, QBrush

# 导入语音识别模块
from speech_recognizer import SpeechRecognizer
from baidu_speech_simple import BaiduSpeechSimple
from speech_recognizer_local import LocalSpeechRecognizer


class ModernButton(QPushButton):
    """现代化按钮组件"""
    
    def __init__(self, text="", icon_text="", is_primary=False, is_circular=False):
        super().__init__(text)
        self.icon_text = icon_text
        self.is_primary = is_primary
        self.is_circular = is_circular
        self.is_recording = False
        self.setup_style()
    
    def setup_style(self):
        """设置按钮样式"""
        if self.is_circular:
            # 圆形录音按钮
            self.setFixedSize(80, 80)
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                                stop:0 #00c756, stop:1 #00a84f);
                    border: none;
                    border-radius: 40px;
                    color: white;
                    font-size: 24px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                                stop:0 #00d158, stop:1 #00b851);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                                stop:0 #00b654, stop:1 #009e4d);
                }
            """)
        elif self.is_primary:
            # 主要按钮
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                                stop:0 #00c756, stop:1 #00a84f);
                    border: none;
                    border-radius: 8px;
                    color: white;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                                stop:0 #00d158, stop:1 #00b851);
                }
                QPushButton:disabled {
                    background: #cccccc;
                    color: #888888;
                }
            """)
        else:
            # 次要按钮
            self.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.9);
                    border: 2px solid #e5e7eb;
                    border-radius: 8px;
                    color: #374151;
                    padding: 10px 20px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    border-color: #00c756;
                    color: #00c756;
                    background: rgba(0, 199, 86, 0.05);
                }
                QPushButton:disabled {
                    background: #f3f4f6;
                    color: #9ca3af;
                    border-color: #e5e7eb;
                }
            """)
    
    def set_recording(self, recording):
        """设置录音状态"""
        self.is_recording = recording
        if self.is_circular:
            if recording:
                self.setText("⏹️")
                self.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                                    stop:0 #ff4757, stop:1 #ff3742);
                        border: none;
                        border-radius: 40px;
                        color: white;
                        font-size: 24px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                                    stop:0 #ff5868, stop:1 #ff4853);
                    }
                """)
            else:
                self.setText("🎤")
                self.setup_style()


class StatusLabel(QLabel):
    """状态标签组件"""
    
    def __init__(self, text="准备就绪"):
        super().__init__(text)
        self.setup_style()
    
    def setup_style(self):
        """设置标签样式"""
        self.setStyleSheet("""
            QLabel {
                background: rgba(0, 199, 86, 0.1);
                border: 1px solid rgba(0, 199, 86, 0.3);
                border-radius: 20px;
                padding: 8px 16px;
                color: #00c756;
                font-weight: 600;
                font-size: 13px;
            }
        """)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedHeight(36)
    
    def set_status(self, text, status_type="success"):
        """设置状态"""
        self.setText(text)
        
        if status_type == "success":
            color = "#00c756"
            bg_color = "rgba(0, 199, 86, 0.1)"
            border_color = "rgba(0, 199, 86, 0.3)"
        elif status_type == "warning":
            color = "#f59e0b"
            bg_color = "rgba(245, 158, 11, 0.1)"
            border_color = "rgba(245, 158, 11, 0.3)"
        elif status_type == "error":
            color = "#ef4444"
            bg_color = "rgba(239, 68, 68, 0.1)"
            border_color = "rgba(239, 68, 68, 0.3)"
        else:
            color = "#6b7280"
            bg_color = "rgba(107, 114, 128, 0.1)"
            border_color = "rgba(107, 114, 128, 0.3)"
        
        self.setStyleSheet(f"""
            QLabel {{
                background: {bg_color};
                border: 1px solid {border_color};
                border-radius: 20px;
                padding: 8px 16px;
                color: {color};
                font-weight: 600;
                font-size: 13px;
            }}
        """)


class ModernTextEdit(QTextEdit):
    """现代化文本编辑器"""
    
    def __init__(self):
        super().__init__()
        self.setup_style()
        self.char_count_label = QLabel("0 字符")
        self.setup_char_counter()
    
    def setup_style(self):
        """设置文本编辑器样式"""
        self.setStyleSheet("""
            QTextEdit {
                background: rgba(255, 255, 255, 0.95);
                border: 2px solid rgba(229, 229, 229, 0.6);
                border-radius: 12px;
                padding: 20px;
                font-size: 18px;
                line-height: 1.8;
                color: #1f2937;
                font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
                font-weight: 500;
            }
            QTextEdit:focus {
                border-color: #00c756;
                outline: none;
            }
            QScrollBar:vertical {
                background: rgba(0,0,0,0.1);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0,0,0,0.3);
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(0,0,0,0.5);
            }
        """)
        
        self.setPlaceholderText(
            "语音识别结果将显示在这里...\n\n"
            "您也可以直接在此编辑文本内容。\n\n"
            "支持的功能：\n"
            "• 实时语音转文字\n"
            "• 智能标点符号\n"
            "• 多引擎切换"
        )
    
    def setup_char_counter(self):
        """设置字符计数器"""
        self.textChanged.connect(self.update_char_count)
    
    def update_char_count(self):
        """更新字符计数"""
        text = self.toPlainText()
        char_count = len(text)
        word_count = len(text.split()) if text.strip() else 0
        self.char_count_label.setText(f"{char_count} 字符 • {word_count} 词")


class ModernSpeechGUI(QMainWindow):
    """现代化语音识别GUI"""
    
    def __init__(self):
        super().__init__()
        self.speech_recognizer = None
        self.is_always_on_top = False
        self.current_engine = 'baidu'
        self.is_recording = False
        
        # 可用的语音识别引擎
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
        self.apply_modern_style()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('🎙️ 语音助手 - 现代化界面')
        self.setGeometry(100, 100, 900, 700)
        
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 20, 30, 30)
        
        # 顶部导航栏
        self.create_header(main_layout)
        
        # 中央内容区
        self.create_content_area(main_layout)
        
        # 底部操作栏
        self.create_footer(main_layout)
    
    def create_header(self, parent_layout):
        """创建顶部导航栏"""
        header_frame = QFrame()
        header_frame.setFixedHeight(80)
        header_layout = QHBoxLayout()
        header_frame.setLayout(header_layout)
        
        # Logo和标题
        logo_layout = QHBoxLayout()
        logo_label = QLabel("🎙️")
        logo_label.setStyleSheet("font-size: 32px;")
        title_label = QLabel("语音助手")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #1f2937;
            margin-left: 10px;
        """)
        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(title_label)
        logo_layout.addStretch()
        
        # 状态指示器
        self.status_label = StatusLabel("准备就绪")
        
        # 引擎选择器
        engine_layout = QHBoxLayout()
        engine_label = QLabel("识别引擎:")
        engine_label.setStyleSheet("color: #6b7280; font-size: 14px;")
        
        self.engine_selector = QComboBox()
        for key, engine in self.engines.items():
            self.engine_selector.addItem(engine['name'], key)
        self.engine_selector.setCurrentText(self.engines[self.current_engine]['name'])
        self.engine_selector.currentTextChanged.connect(self.change_engine)
        self.engine_selector.setStyleSheet("""
            QComboBox {
                background: white;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                min-width: 150px;
            }
            QComboBox:hover {
                border-color: #00c756;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
        """)
        
        engine_layout.addWidget(engine_label)
        engine_layout.addWidget(self.engine_selector)
        
        # 置顶按钮
        self.pin_button = ModernButton("📌", is_primary=False)
        self.pin_button.setFixedSize(40, 40)
        self.pin_button.clicked.connect(self.toggle_always_on_top)
        
        header_layout.addLayout(logo_layout)
        header_layout.addWidget(self.status_label)
        header_layout.addLayout(engine_layout)
        header_layout.addWidget(self.pin_button)
        
        parent_layout.addWidget(header_frame)
    
    def create_content_area(self, parent_layout):
        """创建中央内容区"""
        content_frame = QFrame()
        content_layout = QVBoxLayout()
        content_frame.setLayout(content_layout)
        
        # 文本编辑器
        self.text_edit = ModernTextEdit()
        content_layout.addWidget(self.text_edit)
        
        # 字符计数器
        counter_layout = QHBoxLayout()
        counter_layout.addStretch()
        counter_layout.addWidget(self.text_edit.char_count_label)
        self.text_edit.char_count_label.setStyleSheet("""
            color: #9ca3af;
            font-size: 12px;
            padding: 5px 10px;
            background: rgba(255, 255, 255, 0.8);
            border-radius: 15px;
        """)
        content_layout.addLayout(counter_layout)
        
        parent_layout.addWidget(content_frame)
    
    def create_footer(self, parent_layout):
        """创建底部操作栏"""
        footer_frame = QFrame()
        footer_frame.setFixedHeight(120)
        footer_layout = QHBoxLayout()
        footer_frame.setLayout(footer_layout)
        
        # 左侧按钮
        left_layout = QHBoxLayout()
        
        self.clear_button = ModernButton("🗑️ 清空")
        self.clear_button.clicked.connect(self.clear_text)
        
        self.copy_button = ModernButton("📋 复制")
        self.copy_button.clicked.connect(self.copy_text)
        
        left_layout.addWidget(self.clear_button)
        left_layout.addWidget(self.copy_button)
        left_layout.addStretch()
        
        # 中央录音按钮
        self.record_button = ModernButton("🎤", is_circular=True)
        self.record_button.clicked.connect(self.toggle_recording)
        
        # 右侧信息
        right_layout = QHBoxLayout()
        right_layout.addStretch()
        info_label = QLabel("快捷键: 空格键")
        info_label.setStyleSheet("color: #9ca3af; font-size: 12px;")
        right_layout.addWidget(info_label)
        
        footer_layout.addLayout(left_layout)
        footer_layout.addWidget(self.record_button, 0, Qt.AlignCenter)
        footer_layout.addLayout(right_layout)
        
        parent_layout.addWidget(footer_frame)
    
    def apply_modern_style(self):
        """应用现代化样式"""
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                           stop:0 #f5f7fa, stop:1 #c3cfe2);
            }
            QFrame {
                background: rgba(255, 255, 255, 0.7);
                border-radius: 15px;
            }
        """)
    
    def init_speech_recognizer(self):
        """初始化语音识别器"""
        try:
            engine_config = self.engines[self.current_engine]
            self.speech_recognizer = engine_config['class']()
            
            # 检查语音识别器是否正确创建
            if not self.speech_recognizer:
                raise Exception("语音识别器创建失败")
            
            # 连接信号（添加错误处理）
            try:
                self.speech_recognizer.text_recognized.connect(self.on_text_recognized)
                self.speech_recognizer.error_occurred.connect(self.on_error_occurred)
                self.speech_recognizer.status_changed.connect(self.on_status_changed)
            except Exception as signal_error:
                raise Exception(f"信号连接失败: {str(signal_error)}")
            
            self.status_label.set_status(f"{engine_config['name']} 已就绪", "success")
            
        except Exception as e:
            self.status_label.set_status("初始化失败", "error")
            # 不弹出对话框，只在控制台输出
            print(f"语音识别器初始化失败: {str(e)}")
            self.speech_recognizer = None
    
    def change_engine(self, engine_name):
        """切换语音识别引擎"""
        for key, engine in self.engines.items():
            if engine['name'] == engine_name:
                self.current_engine = key
                break
        
        if self.is_recording:
            self.stop_recording()
        
        self.init_speech_recognizer()
    
    def toggle_recording(self):
        """切换录音状态"""
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    def start_recording(self):
        """开始录音"""
        if not self.speech_recognizer:
            self.status_label.set_status("语音识别器未初始化", "error")
            return
        
        try:
            self.speech_recognizer.start_listening()
            self.is_recording = True
            self.record_button.set_recording(True)
            self.status_label.set_status("正在录音...", "warning")
        except Exception as e:
            self.status_label.set_status("启动录音失败", "error")
            print(f"启动录音失败: {str(e)}")
            # 尝试重新初始化
            self.init_speech_recognizer()
    
    def stop_recording(self):
        """停止录音"""
        if self.speech_recognizer:
            self.speech_recognizer.stop_listening()
        
        self.is_recording = False
        self.record_button.set_recording(False)
        self.status_label.set_status("准备就绪", "success")
    
    def clear_text(self):
        """清空文本"""
        self.text_edit.clear()
        self.status_label.set_status("文本已清空", "success")
    
    def copy_text(self):
        """复制文本"""
        text = self.text_edit.toPlainText()
        if text.strip():
            QApplication.clipboard().setText(text)
            self.status_label.set_status("文本已复制", "success")
        else:
            self.status_label.set_status("没有可复制的内容", "warning")
    
    def toggle_always_on_top(self):
        """切换窗口置顶"""
        self.is_always_on_top = not self.is_always_on_top
        
        if self.is_always_on_top:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.pin_button.setText("📌")
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.pin_button.setText("📋")
        
        self.show()
    
    def on_text_recognized(self, text):
        """处理识别到的文本"""
        self.text_edit.append(text)
        cursor = self.text_edit.textCursor()
        cursor.movePosition(cursor.End)
        self.text_edit.setTextCursor(cursor)
    
    def on_error_occurred(self, error_message):
        """处理错误"""
        self.status_label.set_status("识别错误", "error")
        print(f"语音识别错误: {error_message}")
        if self.is_recording:
            self.stop_recording()
    
    def on_status_changed(self, status):
        """处理状态变化"""
        if '正在' in status:
            self.status_label.set_status(status, "warning")
        elif '错误' in status or '失败' in status:
            self.status_label.set_status(status, "error")
        else:
            self.status_label.set_status(status, "success")
    
    def closeEvent(self, event):
        """关闭事件处理"""
        if self.is_recording:
            self.stop_recording()
        event.accept()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("现代化语音助手")
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    window = ModernSpeechGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main() 