"""
GUI 界面模块
使用 PyQt5 实现极简风格的用户界面
"""
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTextEdit, QMessageBox, QLabel)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from speech_recognizer import SpeechRecognizer



class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.speech_recognizer = SpeechRecognizer()
        self.recognition_thread = None
        self.is_recognizing = False
        self.init_ui()
        self.connect_signals()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("语音转文字插件")
        self.setGeometry(300, 300, 500, 400)
        
        # 默认不置顶
        self.setWindowFlags(Qt.Window)
        
        # 创建中央widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        
        # 创建开始识别按钮
        self.start_button = QPushButton("开始语音识别")
        self.start_button.setFixedHeight(40)
        self.start_button.clicked.connect(self.start_recognition)
        button_layout.addWidget(self.start_button)
        
        # 创建结束识别按钮
        self.stop_button = QPushButton("结束语音识别")
        self.stop_button.setFixedHeight(40)
        self.stop_button.clicked.connect(self.stop_recognition)
        self.stop_button.setEnabled(False)  # 初始状态禁用
        button_layout.addWidget(self.stop_button)
        
        # 创建置顶切换按钮
        self.pin_button = QPushButton("📋")
        self.pin_button.setFixedSize(40, 40)
        self.pin_button.setToolTip("切换窗口置顶")
        self.pin_button.clicked.connect(self.toggle_always_on_top)
        self.pin_button.setStyleSheet("font-size: 16px; border: 1px solid #ccc; border-radius: 3px;")
        self.is_always_on_top = False  # 记录当前置顶状态
        button_layout.addWidget(self.pin_button)
        
        layout.addLayout(button_layout)
        
        # 创建状态标签
        self.status_label = QLabel("正在检测麦克风...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        layout.addWidget(self.status_label)
        
        # 创建文本显示区域
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("点击按钮开始语音识别，识别结果将显示在这里...")
        # 设置字体
        font = QFont()
        font.setPointSize(12)
        self.text_edit.setFont(font)
        layout.addWidget(self.text_edit)
        
        # 设置布局边距
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 居中显示窗口
        self.center_window()
    
    def center_window(self):
        """将窗口居中显示"""
        screen = QApplication.desktop().screenGeometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)
    
    def toggle_always_on_top(self):
        """切换窗口置顶状态"""
        self.is_always_on_top = not self.is_always_on_top
        
        if self.is_always_on_top:
            # 设置窗口置顶
            self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Window)
            self.pin_button.setText("📌")  # 别针图标表示已置顶
            self.pin_button.setToolTip("取消窗口置顶")
            self.pin_button.setStyleSheet("font-size: 16px; border: 1px solid #dc3545; border-radius: 3px; background-color: #f8f9fa;")
        else:
            # 取消窗口置顶
            self.setWindowFlags(Qt.Window)
            self.pin_button.setText("📋")  # 普通图标表示未置顶
            self.pin_button.setToolTip("设置窗口置顶")
            self.pin_button.setStyleSheet("font-size: 16px; border: 1px solid #ccc; border-radius: 3px;")
        
        # 重新显示窗口以应用新的窗口标志
        self.show()
    
    def connect_signals(self):
        """连接信号和槽"""
        self.speech_recognizer.text_recognized.connect(self.on_text_recognized)
        self.speech_recognizer.error_occurred.connect(self.on_error_occurred)
        self.speech_recognizer.status_changed.connect(self.on_status_changed)
    
    def start_recognition(self):
        """开始语音识别"""
        if self.is_recognizing:
            return
        
        self.is_recognizing = True
        self.start_button.setEnabled(False)  # 禁用开始按钮
        self.stop_button.setEnabled(True)   # 启用结束按钮
        
        # 直接启动持续监听模式
        self.speech_recognizer.start_listening()
    
    def stop_recognition(self):
        """停止语音识别"""
        if not self.is_recognizing:
            return
        
        # 重置状态和按钮
        self._reset_ui_state()
        
        # 停止语音识别器
        self.speech_recognizer.stop_listening()
    
    def _reset_ui_state(self):
        """重置UI状态到初始状态"""
        self.is_recognizing = False
        self.start_button.setEnabled(True)   # 启用开始按钮
        self.stop_button.setEnabled(False)  # 禁用结束按钮
        self.status_label.setText("🎤 麦克风已连接")
        self.status_label.setStyleSheet("color: #28a745; font-size: 11px; padding: 5px;")
    
    def on_recognition_finished(self):
        """识别完成后的处理"""
        self._reset_ui_state()
    
    def on_text_recognized(self, text):
        """处理识别到的文本"""
        # 在文本框中添加识别结果
        current_text = self.text_edit.toPlainText()
        if current_text:
            # 如果当前文本不是以标点符号结尾，在新文本前加空格
            if not current_text.endswith(('。', '？', '！', '\n')):
                new_text = current_text + " " + text
            else:
                new_text = current_text + "\n" + text
        else:
            new_text = text
        
        self.text_edit.setPlainText(new_text)
        # 滚动到底部
        self.text_edit.moveCursor(self.text_edit.textCursor().End)
    
    def on_error_occurred(self, error_msg):
        """处理错误"""
        # 更新状态标签显示错误
        if "无法找到可用的麦克风设备" in error_msg:
            self.status_label.setText("❌ 未检测到麦克风")
            self.status_label.setStyleSheet("color: #dc3545; font-size: 11px; padding: 5px;")
        else:
            self.status_label.setText("❌ 语音识别出错")
            self.status_label.setStyleSheet("color: #dc3545; font-size: 11px; padding: 5px;")
        
        # 创建自定义的错误对话框
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Warning)
        
        # 检查是否是麦克风连接问题
        if "无法找到可用的麦克风设备" in error_msg:
            msg_box.setWindowTitle("麦克风连接问题")
            msg_box.setText("检测不到麦克风设备")
            msg_box.setDetailedText(error_msg)
            msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Retry)
            msg_box.setDefaultButton(QMessageBox.Retry)
            
            result = msg_box.exec_()
            if result == QMessageBox.Retry:
                # 用户点击重试，重新初始化语音识别器
                self.status_label.setText("🔄 正在重新检测麦克风...")
                self.status_label.setStyleSheet("color: #007bff; font-size: 11px; padding: 5px;")
                self.speech_recognizer = SpeechRecognizer()
                self.connect_signals()
                return
        else:
            msg_box.setWindowTitle("错误")
            msg_box.setText(error_msg)
            msg_box.exec_()
        
        self.stop_recognition()
    
    def on_status_changed(self, status):
        """处理状态变化"""
        # 更新状态标签
        if "麦克风已连接" in status:
            self.status_label.setText("🎤 麦克风已连接")
            self.status_label.setStyleSheet("color: #28a745; font-size: 11px; padding: 5px;")
        elif "正在监听" in status:
            self.status_label.setText("🔴 正在录音...")
            self.status_label.setStyleSheet("color: #dc3545; font-size: 11px; padding: 5px;")
        elif "监听已停止" in status:
            # 监听停止时，重置所有UI状态
            self._reset_ui_state()
        elif "请说话" in status:
            self.status_label.setText("🎙️ 请对着麦克风说话...")
            self.status_label.setStyleSheet("color: #007bff; font-size: 11px; padding: 5px;")
        elif "正在识别" in status:
            self.status_label.setText("⏳ 正在识别语音...")
            self.status_label.setStyleSheet("color: #ffc107; font-size: 11px; padding: 5px;")
        elif "请继续说话" in status:
            self.status_label.setText("🎙️ 请继续说话...")
            self.status_label.setStyleSheet("color: #007bff; font-size: 11px; padding: 5px;")
        elif "等待语音输入" in status:
            self.status_label.setText("⏸️ 等待语音输入...")
            self.status_label.setStyleSheet("color: #6c757d; font-size: 11px; padding: 5px;")
        elif "长时间无语音" in status:
            # 自动停止时，重置所有UI状态
            self._reset_ui_state()
            self.status_label.setText("⏹️ 长时间无语音，已自动停止")
            self.status_label.setStyleSheet("color: #28a745; font-size: 11px; padding: 5px;")
        else:
            self.status_label.setText(status)
            self.status_label.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        
        # 根据状态更新按钮状态
        if status == "识别完成" or status == "未识别到语音" or status == "录音超时":
            # 这些状态表示识别过程结束，重置UI状态
            self._reset_ui_state()
    
    def closeEvent(self, event):
        """关闭事件处理"""
        # 停止语音识别
        self.speech_recognizer.stop_listening()
        
        # 等待线程结束
        if self.recognition_thread and self.recognition_thread.isRunning():
            self.recognition_thread.quit()
            self.recognition_thread.wait()
        
        event.accept()


def create_application():
    """创建应用程序"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("语音转文字插件")
    app.setApplicationVersion("1.0.0")
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    return app, window 