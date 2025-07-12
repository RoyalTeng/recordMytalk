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
    # 更现代的配色方案 - 基于Material Design 3
    PRIMARY, PRIMARY_HOVER, PRIMARY_PRESSED = "#6750a4", "#7c69b8", "#533b87"
    SECONDARY, SECONDARY_HOVER = "#625b71", "#7c7589"
    BACKGROUND, CARD_BACKGROUND = "#fef7ff", "#ffffff"
    SURFACE_VARIANT = "#f7f2fa"
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_TERTIARY = "#1d1b20", "#49454f", "#79747e"
    BORDER, BORDER_SUBTLE = "#cac4d0", "#e7e0ec"
    SUCCESS, ERROR, WARNING = "#146c2e", "#ba1a1a", "#e65100"
    SUCCESS_BG, ERROR_BG, WARNING_BG = "#e8f5e8", "#ffeaea", "#fff3e0"

class TIcons:
    MICROPHONE, STOP, SETTINGS, PIN = "\uf130", "\uf28d", "\uf013", "\uf08d"
    COPY, CLEAR, SUCCESS, ERROR = "\uf0c5", "\uf1f8", "\uf058", "\uf057"
    CHEVRON_DOWN, CIRCLE = "\uf078", "\uf111"

class TCard(QFrame):
    def __init__(self, elevated=False):
        super().__init__()
        # 更精致的卡片设计
        border_radius = 16 if elevated else 12
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {TColors.CARD_BACKGROUND};
                border-radius: {border_radius}px;
                border: 1px solid {TColors.BORDER_SUBTLE};
            }}
        """)
        shadow = QGraphicsDropShadowEffect(self)
        if elevated:
            shadow.setBlurRadius(32)
            shadow.setColor(QColor(79, 55, 139, 20))  # 使用主色调的阴影
            shadow.setOffset(0, 8)
        else:
            shadow.setBlurRadius(16)
            shadow.setColor(QColor(29, 27, 32, 15))
            shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

class TButton(QPushButton):
    def __init__(self, text, icon=None, button_type="filled"):
        super().__init__(text)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(44)  # 更友好的点击区域
        
        if button_type == "filled":
            style = f"""
                QPushButton {{
                    background-color: {TColors.SURFACE_VARIANT};
                    color: {TColors.TEXT_PRIMARY};
                    border: 1px solid {TColors.BORDER_SUBTLE};
                    border-radius: 12px;
                    padding: 12px 20px;
                    font-size: 14px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {TColors.SECONDARY_HOVER};
                    color: white;
                    border-color: {TColors.SECONDARY};
                }}
                QPushButton:pressed {{
                    background-color: {TColors.SECONDARY};
                }}
            """
        else:  # outline type
            style = f"""
                QPushButton {{
                    background-color: transparent;
                    color: {TColors.SECONDARY};
                    border: 2px solid {TColors.BORDER};
                    border-radius: 12px;
                    padding: 12px 20px;
                    font-size: 14px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {TColors.SURFACE_VARIANT};
                    border-color: {TColors.SECONDARY};
                }}
            """
        
        self.setStyleSheet(style)
        if icon: self.setText(f"{icon}  {text}")

class TIconButton(QPushButton):
    def __init__(self, icon_char):
        super().__init__(icon_char)
        self.setFixedSize(44, 44)  # 更大的点击区域
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TColors.TEXT_SECONDARY};
                border: none;
                font-size: 18px;
                border-radius: 22px;
            }}
            QPushButton:hover {{
                background-color: {TColors.SURFACE_VARIANT};
                color: {TColors.TEXT_PRIMARY};
            }}
            QPushButton:pressed {{
                background-color: {TColors.BORDER};
            }}
            QPushButton:checked {{
                background-color: {TColors.PRIMARY};
                color: white;
            }}
        """)

class TRecordButton(QPushButton):
    def __init__(self):
        super().__init__(TIcons.MICROPHONE)
        self.is_recording = False
        self.setFixedSize(80, 80)  # 更大的按钮作为焦点
        self.setCursor(Qt.PointingHandCursor)
        
        # 动画定时器用于录音状态的脉动效果
        self.pulse_timer = QTimer(self)
        self.pulse_timer.timeout.connect(self._pulse_effect)
        self.pulse_state = 0
        
        self.update_style()

    def set_recording(self, recording):
        self.is_recording = recording
        if recording:
            self.pulse_timer.start(800)  # 每800ms脉动一次
        else:
            self.pulse_timer.stop()
            self.pulse_state = 0
        self.update_style()
    
    def _pulse_effect(self):
        """录音时的脉动效果"""
        self.pulse_state = 1 - self.pulse_state
        self.update_style()
        
    def update_style(self):
        base_style = """
            QPushButton {{
                border: none;
                border-radius: 40px;
                font-size: 32px;
                font-weight: bold;
                transition: all 0.2s ease;
            }}
        """
        
        if self.is_recording:
            self.setText(TIcons.STOP)
            # 脉动效果 - 交替两种阴影大小
            shadow_size = "16px" if self.pulse_state else "8px"
            shadow_opacity = "0.4" if self.pulse_state else "0.2"
            
            hover_style = f"""
                QPushButton:hover {{
                    background-color: #c62828;
                    transform: scale(1.05);
                }}
                QPushButton:pressed {{
                    background-color: #9a0007;
                    transform: scale(0.95);
                }}
            """
            self.setStyleSheet(base_style + f"""
                QPushButton {{
                    background-color: {TColors.ERROR};
                    color: white;
                    box-shadow: 0 6px {shadow_size} rgba(186, 26, 26, {shadow_opacity});
                }}
            """ + hover_style)
        else:
            self.setText(TIcons.MICROPHONE)
            hover_style = f"""
                QPushButton:hover {{
                    background-color: {TColors.PRIMARY_HOVER};
                    transform: scale(1.05);
                    box-shadow: 0 8px 24px rgba(103, 80, 164, 0.4);
                }}
                QPushButton:pressed {{
                    background-color: {TColors.PRIMARY_PRESSED};
                    transform: scale(0.95);
                }}
            """
            self.setStyleSheet(base_style + f"""
                QPushButton {{
                    background-color: {TColors.PRIMARY};
                    color: white;
                    box-shadow: 0 6px 16px rgba(103, 80, 164, 0.3);
                }}
            """ + hover_style)

class TEngineSelector(QWidget):
    """整合的引擎选择器 - 显示状态指示灯和引擎名称"""
    engine_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.current_engine = None
        self.current_status = "info"
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # 状态指示灯
        self.status_dot = QLabel(TIcons.CIRCLE)
        self.status_dot.setFont(QFont("FontAwesome", 8))
        self.status_dot.setStyleSheet(f"color: {TColors.TEXT_TERTIARY};")
        
        # 引擎选择下拉框
        self.combo = QComboBox()
        self.combo.setCursor(Qt.PointingHandCursor)
        self.combo.setMinimumHeight(36)
        self.combo.currentTextChanged.connect(self._on_engine_changed)
        self.combo.setStyleSheet(f"""
            QComboBox {{
                background-color: transparent;
                border: none;
                padding: 8px 12px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                color: {TColors.TEXT_PRIMARY};
            }}
            QComboBox:hover {{
                background-color: {TColors.SURFACE_VARIANT};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: none;
            }}
            QComboBox QAbstractItemView {{
                border: 1px solid {TColors.BORDER};
                background-color: {TColors.CARD_BACKGROUND};
                selection-background-color: {TColors.PRIMARY};
                color: {TColors.TEXT_PRIMARY};
                selection-color: white;
                border-radius: 8px;
                padding: 4px;
            }}
        """)
        
        layout.addWidget(self.status_dot)
        layout.addWidget(self.combo)
        
    def _on_engine_changed(self):
        current_data = self.combo.currentData()
        if current_data:
            self.engine_changed.emit(current_data)
    
    def add_engine(self, key, name):
        self.combo.addItem(name, key)
    
    def set_status(self, status_type):
        """设置状态指示灯颜色"""
        self.current_status = status_type
        colors = {
            "success": TColors.SUCCESS,
            "error": TColors.ERROR,
            "warning": TColors.WARNING,
            "info": TColors.TEXT_TERTIARY
        }
        color = colors.get(status_type, colors["info"])
        self.status_dot.setStyleSheet(f"color: {color};")
        
    def current_data(self):
        return self.combo.currentData()

class TComboBox(QComboBox):
    def __init__(self):
        super().__init__()
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(44)
        self.setStyleSheet(f"""
            QComboBox {{
                background-color: {TColors.SURFACE_VARIANT};
                border: 1px solid {TColors.BORDER_SUBTLE};
                padding: 12px 16px;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 500;
                color: {TColors.TEXT_PRIMARY};
            }}
            QComboBox:hover {{
                border-color: {TColors.BORDER};
                background-color: {TColors.CARD_BACKGROUND};
            }}
            QComboBox:focus {{
                border-color: {TColors.PRIMARY};
                outline: none;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: none;
            }}
            QComboBox QAbstractItemView {{
                border: 1px solid {TColors.BORDER};
                background-color: {TColors.CARD_BACKGROUND};
                selection-background-color: {TColors.PRIMARY};
                color: {TColors.TEXT_PRIMARY};
                selection-color: white;
                border-radius: 8px;
                padding: 4px;
            }}
        """)

class TStatusLabel(QLabel):
    def __init__(self, text="准备就绪"):
        super().__init__()
        self.set_status("info", text)

    def set_status(self, status_type, text):
        colors = {
            "success": (TColors.SUCCESS, TColors.SUCCESS_BG),
            "error": (TColors.ERROR, TColors.ERROR_BG),
            "warning": (TColors.WARNING, TColors.WARNING_BG),
            "info": (TColors.TEXT_SECONDARY, TColors.SURFACE_VARIANT)
        }
        color, bg_color = colors.get(status_type, colors["info"])
        icons = {"success": TIcons.SUCCESS, "error": TIcons.ERROR}
        self.setText(f"{icons.get(status_type, '')} {text}".strip())
        self.setStyleSheet(f"""
            QLabel {{
                color: {color};
                background-color: {bg_color};
                border-radius: 20px;
                padding: 10px 16px;
                font-size: 13px;
                font-weight: 500;
                border: 1px solid {TColors.BORDER_SUBTLE};
            }}
        """)

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
        main_layout = QVBoxLayout(container); main_layout.setContentsMargins(24, 24, 24, 24); main_layout.setSpacing(20)
        main_layout.addWidget(self._create_header_card())
        main_layout.addWidget(self._create_content_card(), 1)
        main_layout.addWidget(self._create_footer_card())

    def _create_header_card(self):
        card = TCard(); layout = QHBoxLayout(card); layout.setContentsMargins(24, 16, 24, 16)
        
        # 左侧：引擎选择器（整合状态和选择）
        self.engine_selector = TEngineSelector()
        self.engine_selector.engine_changed.connect(self.engine_changed_signal.emit)
        
        # 右侧：设置和置顶按钮
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)
        
        self.settings_button = TIconButton(TIcons.SETTINGS)
        self.settings_button.setToolTip("设置")
        
        self.pin_button = TIconButton(TIcons.PIN)
        self.pin_button.setCheckable(True)
        self.pin_button.setToolTip("窗口置顶")
        self.pin_button.clicked.connect(self.toggle_always_on_top)
        
        controls_layout.addWidget(self.settings_button)
        controls_layout.addWidget(self.pin_button)
        
        layout.addWidget(self.engine_selector)
        layout.addStretch()
        layout.addLayout(controls_layout)
        return card

    def _create_content_card(self):
        card = TCard(elevated=True); layout = QVBoxLayout(card); layout.setContentsMargins(20, 20, 20, 15)
        
        # 文本输入区域
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("点击麦克风开始识别")
        self.text_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: transparent;
                border: none;
                font-size: 16px;
                line-height: 1.6;
                color: {TColors.TEXT_PRIMARY};
                selection-background-color: {TColors.PRIMARY};
                selection-color: white;
            }}
            QTextEdit:focus {{
                outline: none;
            }}
        """)
        
        # 底部信息栏（字符计数 + 操作按钮）
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        
        # 字符计数
        self.char_count_label = QLabel("0 字符")
        self.char_count_label.setStyleSheet(f"""
            QLabel {{
                color: {TColors.TEXT_TERTIARY};
                padding: 8px 4px;
                font-size: 12px;
                font-weight: 400;
            }}
        """)
        
        # 操作按钮组
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)
        
        self.clear_button = QPushButton(TIcons.CLEAR)
        self.clear_button.setFixedSize(32, 32)
        self.clear_button.setToolTip("清空")
        self.clear_button.setCursor(Qt.PointingHandCursor)
        self.clear_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TColors.TEXT_TERTIARY};
                border: none;
                border-radius: 16px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {TColors.SURFACE_VARIANT};
                color: {TColors.ERROR};
            }}
        """)
        
        self.copy_button = QPushButton(TIcons.COPY)
        self.copy_button.setFixedSize(32, 32)
        self.copy_button.setToolTip("复制")
        self.copy_button.setCursor(Qt.PointingHandCursor)
        self.copy_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TColors.TEXT_TERTIARY};
                border: none;
                border-radius: 16px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {TColors.SURFACE_VARIANT};
                color: {TColors.PRIMARY};
            }}
        """)
        
        actions_layout.addWidget(self.clear_button)
        actions_layout.addWidget(self.copy_button)
        
        bottom_layout.addWidget(self.char_count_label)
        bottom_layout.addStretch()
        bottom_layout.addLayout(actions_layout)
        
        self.text_edit.textChanged.connect(self.update_char_count)
        self.clear_button.clicked.connect(lambda: self.text_edit.clear())
        self.copy_button.clicked.connect(self.copy_text)
        
        layout.addWidget(self.text_edit)
        layout.addLayout(bottom_layout)
        return card
        
    def _create_footer_card(self):
        """创建底部卡片 - 仅包含录音按钮作为焦点"""
        card = TCard(); layout = QHBoxLayout(card); layout.setContentsMargins(24, 20, 24, 20)
        
        # 中心的录音按钮
        self.record_button = TRecordButton()
        self.record_button.clicked.connect(self.toggle_recording)
        
        layout.addStretch()
        layout.addWidget(self.record_button)
        layout.addStretch()
        return card

    def apply_styles(self):
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {TColors.BACKGROUND};
            }}
        """)
        # 为所有图标按钮设置字体
        icon_buttons = [self.pin_button, self.settings_button, self.clear_button, self.copy_button, self.record_button]
        for btn in icon_buttons: 
            btn.setFont(self.icon_font)

    def toggle_recording(self):
        is_recording = not self.record_button.is_recording
        self.record_button.set_recording(is_recording)
        
        # 更新文本区域提示
        if is_recording:
            self.text_edit.setPlaceholderText("🎤 正在录音，请说话...")
            self.start_recording_signal.emit()
        else:
            self.text_edit.setPlaceholderText("🔄 正在识别中，请稍等...")
            self.stop_recording_signal.emit()

    def toggle_always_on_top(self, checked):
        if checked: self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else: self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()

    def copy_text(self):
        text = self.text_edit.toPlainText()
        if text.strip():
            QApplication.clipboard().setText(text)
            # 简单的视觉反馈 - 短暂改变按钮颜色
            self.copy_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {TColors.SUCCESS_BG};
                    color: {TColors.SUCCESS};
                    border: none;
                    border-radius: 16px;
                    font-size: 14px;
                }}
            """)
            QTimer.singleShot(1000, self._reset_copy_button_style)
    
    def _reset_copy_button_style(self):
        """重置复制按钮样式"""
        self.copy_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TColors.TEXT_TERTIARY};
                border: none;
                border-radius: 16px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {TColors.SURFACE_VARIANT};
                color: {TColors.PRIMARY};
            }}
        """)
        self.copy_button.setFont(self.icon_font)  # 确保字体不丢失

    def update_char_count(self): self.char_count_label.setText(f"{len(self.text_edit.toPlainText())} 字符")
    def keyPressEvent(self, event): (self.toggle_recording() if event.key() == Qt.Key_Space else super().keyPressEvent(event))
    def set_engine_list(self, engines): 
        for key, config in engines.items():
            self.engine_selector.add_engine(key, config['name'])
    
    def on_text_recognized(self, text): 
        self.text_edit.append(text)
        self.text_edit.verticalScrollBar().setValue(self.text_edit.verticalScrollBar().maximum())
    
    def on_status_changed(self, status, status_type="info"): 
        """更新引擎状态指示灯和文本区域提示"""
        self.engine_selector.set_status(status_type)
        
        # 根据状态更新文本区域的提示
        if status_type == "warning" and "录音" in status:
            self.text_edit.setPlaceholderText("🎤 正在聊天，请说话...")
        elif status_type == "info" and "识别" in status:
            self.text_edit.setPlaceholderText("🔄 正在识别中，请稍等...")
        elif status_type == "error":
            self.text_edit.setPlaceholderText("⚠️ 识别失败，请重试")
        elif status_type == "success" and "已就绪" in status:
            self.text_edit.setPlaceholderText("✨ 点击麦克风开始识别")
        else:
            self.text_edit.setPlaceholderText("点击麦克风开始识别")
        
    def on_recording_stopped(self):
        if self.record_button.is_recording: 
            self.record_button.set_recording(False)
            self.text_edit.setPlaceholderText("✨ 点击麦克风开始识别")
            self.on_status_changed("已停止", "info")

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
        
        self.change_engine(self.ui.engine_selector.current_data())
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