"""
主UI实现文件 - TDesign & QQ音乐风格 (最终版)
作者: Gemini (UI Engineer)
日期: 2025-07-06
"""
import os
import sys
import traceback
os.environ["QT_DEBUG_PLUGINS"] = "1"

def excepthook(type, value, tb):
    traceback.print_exception(type, value, tb)
    input("程序异常退出，按回车键关闭...")

sys.excepthook = excepthook

from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QTextEdit, QPushButton, QLabel, QComboBox,
                             QFrame, QSpacerItem, QSizePolicy, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QColor, QFontDatabase

# 导入编译后的资源文件
try:
    # 用绝对路径加载 icons_rc.py
    import importlib.util
    icons_rc_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons_rc.py')
    spec = importlib.util.spec_from_file_location('icons_rc', icons_rc_path)
    icons_rc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(icons_rc)
except Exception as e:
    print(f"CRITICAL: icons_rc.py not found or failed to load: {e}")
    sys.exit(1)

# 导入后端逻辑
from speech_recognizer import SpeechRecognizer
from baidu_speech_simple import BaiduSpeechSimple

class TColors:
    PRIMARY, PRIMARY_HOVER, PRIMARY_PRESSED = "#0052d9", "#366ef4", "#003fab"
    BACKGROUND, CARD_BACKGROUND = "#f3f4f7", "#ffffff"
    TEXT_PRIMARY, TEXT_SECONDARY = "#000000", "#86909c"
    BORDER, SUCCESS, ERROR, WARNING = "#e0e3e6", "#00a870", "#d54941", "#e6a23c"

class TIcons:
    MICROPHONE, STOP, SETTINGS, PIN = "\uf130", "\uf28d", "\uf013", "\uf08d"
    COPY, CLEAR, SUCCESS, ERROR = "\uf0c5", "\uf1f8", "\uf058", "\uf057"

class TCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: {TColors.CARD_BACKGROUND}; border-radius: 12px;")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20); shadow.setColor(QColor(0, 0, 0, 25)); shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

class TButton(QPushButton):
    def __init__(self, text, icon=None):
        super().__init__(text)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"QPushButton {{ background-color: #f0f2f5; color: {TColors.TEXT_PRIMARY}; border: none; border-radius: 8px; padding: 10px 18px; font-size: 14px; }} QPushButton:hover {{ background-color: #e4e6e9; }}")
        if icon: self.setText(f"{icon}  {text}")

class TIconButton(QPushButton):
    def __init__(self, icon_char):
        super().__init__(icon_char)
        self.setFixedSize(38, 38)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"QPushButton {{ background-color: transparent; color: {TColors.TEXT_SECONDARY}; border: none; font-size: 18px; border-radius: 19px; }} QPushButton:hover {{ background-color: #f0f2f5; }}")

class TRecordButton(QPushButton):
    def __init__(self):
        super().__init__(TIcons.MICROPHONE)
        self.is_recording = False
        self.setFixedSize(64, 64)
        self.setCursor(Qt.PointingHandCursor)
        self.update_style()

    def set_recording(self, recording):
        self.is_recording = recording
        self.update_style()
        
    def update_style(self):
        if self.is_recording:
            self.setText(TIcons.STOP)
            self.setStyleSheet(f"QPushButton {{ background-color: {TColors.ERROR}; color: white; border: none; border-radius: 32px; font-size: 26px; }} QPushButton:hover {{ background-color: #e15f58; }}")
        else:
            self.setText(TIcons.MICROPHONE)
            self.setStyleSheet(f"QPushButton {{ background-color: {TColors.PRIMARY}; color: white; border: none; border-radius: 32px; font-size: 26px; }} QPushButton:hover {{ background-color: {TColors.PRIMARY_HOVER}; }}")

class TComboBox(QComboBox):
    def __init__(self):
        super().__init__()
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"QComboBox {{ background-color: #f0f2f5; border: none; padding: 10px 14px; border-radius: 8px; font-size: 14px; }} QComboBox:hover {{ background-color: #e4e6e9; }} QComboBox::drop-down {{ border: none; }} QComboBox QAbstractItemView {{ border: 1px solid {TColors.BORDER}; background-color: {TColors.CARD_BACKGROUND}; selection-background-color: {TColors.PRIMARY}; color: {TColors.TEXT_PRIMARY}; selection-color: white;}}")

class TStatusLabel(QLabel):
    def __init__(self, text="准备就绪"):
        super().__init__()
        self.set_status("info", text)

    def set_status(self, status_type, text):
        colors = {"success": (TColors.SUCCESS, "#e8f8f3"), "error": (TColors.ERROR, "#fbebee"), "warning": (TColors.WARNING, "#fdf6ec"), "info": (TColors.TEXT_SECONDARY, "#f0f2f5")}
        color, bg_color = colors.get(status_type, colors["info"])
        icons = {"success": TIcons.SUCCESS, "error": TIcons.ERROR}
        self.setText(f"{icons.get(status_type, '')} {text}".strip())
        self.setStyleSheet(f"color: {color}; background-color: {bg_color}; border-radius: 17px; padding: 8px 14px; font-size: 13px; font-weight: 500;")

class SpeechAppUI(QMainWindow):
    """主应用UI"""
    start_recording_signal = pyqtSignal()
    stop_recording_signal = pyqtSignal()
    engine_changed_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        print("[DEBUG] Initializing UI...")
        self.setWindowTitle("语音助手")
        self.setGeometry(100, 100, 580, 720)
        self.setMinimumSize(500, 640)
        
        # 加载字体
        font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'FontAwesome.ttf')
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            print(f"[DEBUG] CRITICAL: FontAwesome.ttf could not be loaded from {font_path}!")
            self.icon_font = QFont("Arial", 15) # Fallback font
        else:
            print(f"[DEBUG] FontAwesome font loaded with ID: {font_id}")
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            if not font_families:
                 print("[DEBUG] WARNING: No font families found in the font file. Using fallback.")
                 self.icon_font = QFont("Arial", 15) # Fallback font
            else:
                 font_name = font_families[0]
                 self.icon_font = QFont(font_name, 15)
                 print(f"[DEBUG] Using font family: '{font_name}'")

        self.is_always_on_top = False
        
        self.init_ui()
        self.apply_styles()
        print("[DEBUG] UI Initialized successfully.")

    def init_ui(self):
        container = QWidget(); self.setCentralWidget(container)
        main_layout = QVBoxLayout(container); main_layout.setContentsMargins(20, 20, 20, 20); main_layout.setSpacing(18)
        main_layout.addWidget(self._create_header_card())
        main_layout.addWidget(self._create_content_card(), 1)
        main_layout.addWidget(self._create_footer_card())

    def _create_header_card(self):
        card = TCard(); layout = QHBoxLayout(card); layout.setContentsMargins(20, 15, 20, 15)
        title = QLabel("语音助手"); title.setStyleSheet(f"font-size: 20px; font-weight: 600; color: {TColors.TEXT_PRIMARY};")
        self.status_label = TStatusLabel("准备就绪")
        self.engine_selector = TComboBox()
        self.engine_selector.currentTextChanged.connect(lambda: self.engine_changed_signal.emit(self.engine_selector.currentData()))
        self.pin_button = TIconButton(TIcons.PIN); self.pin_button.setCheckable(True); self.pin_button.clicked.connect(self.toggle_always_on_top)
        layout.addWidget(title); layout.addStretch(); layout.addWidget(self.status_label); layout.addWidget(self.engine_selector); layout.addWidget(self.pin_button)
        return card

    def _create_content_card(self):
        card = TCard(); layout = QVBoxLayout(card); layout.setContentsMargins(15, 15, 15, 15)
        self.text_edit = QTextEdit(); self.text_edit.setPlaceholderText("点击下方的麦克风按钮开始语音识别...")
        self.text_edit.setStyleSheet(f"background-color: transparent; border: none; font-size: 16px; color: {TColors.TEXT_PRIMARY};")
        self.char_count_label = QLabel("0 字符"); self.char_count_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.char_count_label.setStyleSheet(f"color: {TColors.TEXT_SECONDARY}; padding: 5px;")
        self.text_edit.textChanged.connect(self.update_char_count)
        layout.addWidget(self.text_edit); layout.addWidget(self.char_count_label)
        return card
        
    def _create_footer_card(self):
        card = TCard(); layout = QHBoxLayout(card); layout.setContentsMargins(15, 10, 15, 10)
        self.clear_button = TButton("清空", TIcons.CLEAR); self.copy_button = TButton("复制", TIcons.COPY); self.record_button = TRecordButton()
        self.clear_button.clicked.connect(lambda: self.text_edit.clear()); self.copy_button.clicked.connect(self.copy_text); self.record_button.clicked.connect(self.toggle_recording)
        layout.addWidget(self.clear_button); layout.addWidget(self.copy_button); layout.addStretch(); layout.addWidget(self.record_button); layout.addStretch()
        placeholder = QWidget(); placeholder.setFixedWidth(self.clear_button.sizeHint().width() + self.copy_button.sizeHint().width())
        layout.addWidget(placeholder)
        return card

    def apply_styles(self):
        self.setStyleSheet(f"background-color: {TColors.BACKGROUND};")
        for btn in [self.pin_button, self.clear_button, self.copy_button, self.record_button, self.status_label]: btn.setFont(self.icon_font)

    def toggle_recording(self):
        is_recording = not self.record_button.is_recording
        self.record_button.set_recording(is_recording)
        if is_recording: self.start_recording_signal.emit()
        else: self.stop_recording_signal.emit()

    def toggle_always_on_top(self, checked):
        if checked: self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else: self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()

    def copy_text(self):
        QApplication.clipboard().setText(self.text_edit.toPlainText())
        self.status_label.set_status("success", "已复制！")
        QTimer.singleShot(2000, lambda: self.status_label.set_status("info", "准备就绪"))

    def update_char_count(self): self.char_count_label.setText(f"{len(self.text_edit.toPlainText())} 字符")
    def keyPressEvent(self, event): (self.toggle_recording() if event.key() == Qt.Key_Space else super().keyPressEvent(event))
    def set_engine_list(self, engines): [self.engine_selector.addItem(config['name'], key) for key, config in engines.items()]
    def on_text_recognized(self, text): self.text_edit.append(text); self.text_edit.verticalScrollBar().setValue(self.text_edit.verticalScrollBar().maximum())
    def on_status_changed(self, status, status_type="info"): self.status_label.set_status(status_type, status)
    def on_recording_stopped(self):
        if self.record_button.is_recording: self.record_button.set_recording(False); self.on_status_changed("已停止", "info")

class MainController:
    """主控制器，连接UI和后端逻辑"""
    def __init__(self, app):
        self.app = app
        print("[DEBUG] Creating MainController...")
        self.ui = SpeechAppUI()
        self.speech_recognizer = None
        self.is_recording = False
        
        self.engines = {
            'baidu': {'name': '百度语音', 'class': BaiduSpeechSimple},
            'google': {'name': 'Google语音', 'class': SpeechRecognizer},
        }
        
        self.ui.set_engine_list(self.engines)
        
        self._connect_signals()
        
        self.change_engine(self.ui.engine_selector.currentData())
        print("[DEBUG] MainController initialized.")

    def _connect_signals(self):
        self.ui.start_recording_signal.connect(self.start_listening)
        self.ui.stop_recording_signal.connect(self.stop_listening)
        self.ui.engine_changed_signal.connect(self.change_engine)
    
    def _connect_recognizer_signals(self):
        if self.speech_recognizer:
            self.speech_recognizer.text_recognized.connect(self.ui.on_text_recognized)
            self.speech_recognizer.status_changed.connect(self.ui.on_status_changed)
            self.speech_recognizer.error_occurred.connect(self.handle_recognition_error)

    def handle_recognition_error(self, error_message):
        """只在程序仍在录音状态时处理错误"""
        if self.is_recording:
            self.ui.on_status_changed(error_message, "error")
    
    def change_engine(self, engine_key):
        if self.is_recording: self.stop_listening()
        if engine_config := self.engines.get(engine_key):
            try: self.speech_recognizer = engine_config['class'](); self._connect_recognizer_signals(); self.ui.on_status_changed(f"{engine_config['name']} 已就绪", "success")
            except Exception as e: self.ui.on_status_changed(f"引擎加载失败: {e}", "error")

    def start_listening(self):
        if self.speech_recognizer and not self.is_recording: self.is_recording = True; self.ui.on_status_changed("正在录音...", "warning"); self.speech_recognizer.start_listening()
            
    def stop_listening(self):
        if self.speech_recognizer and self.is_recording: self.is_recording = False; self.speech_recognizer.stop_listening(); self.ui.on_recording_stopped()

    def show(self):
        self.ui.show()
        print("[DEBUG] UI window should be visible now.")

if __name__ == '__main__':
    print("[DEBUG] Application starting...")
    app = QApplication(sys.argv)
    print("[DEBUG] QApplication instance created.")
    controller = MainController(app)
    print("[DEBUG] MainController instance created.")
    controller.show()
    print("[DEBUG] Entering application main loop...")
    sys.exit(app.exec_()) 