"""
WebView集成模块
将TDesign React前端集成到PyQt5应用中
"""
import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QUrl
from PyQt5.QtGui import QIcon

# 导入现有的语音识别模块
from speech_recognizer import SpeechRecognizer
from baidu_speech_simple import BaiduSpeechSimple
from speech_recognizer_local import LocalSpeechRecognizer


class SpeechWebAPI(QObject):
    """WebView与Python后端的API桥接类"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.speech_recognizer = None
        self.current_engine = 'baidu'
        self.engines = {
            'baidu': BaiduSpeechSimple,
            'google': SpeechRecognizer,
            'local': LocalSpeechRecognizer
        }
        self.init_speech_recognizer()
    
    def init_speech_recognizer(self):
        """初始化语音识别器"""
        try:
            engine_class = self.engines[self.current_engine]
            self.speech_recognizer = engine_class()
            
            # 连接信号
            self.speech_recognizer.text_recognized.connect(self.on_text_recognized)
            self.speech_recognizer.error_occurred.connect(self.on_error_occurred)
            self.speech_recognizer.status_changed.connect(self.on_status_changed)
            
        except Exception as e:
            print(f"语音识别器初始化失败: {str(e)}")
    
    @pyqtSlot(str)
    def start_listening(self, engine='baidu'):
        """开始语音识别"""
        try:
            if engine != self.current_engine:
                self.change_engine(engine)
            
            if self.speech_recognizer:
                self.speech_recognizer.start_listening()
        except Exception as e:
            self.on_error_occurred(f"启动语音识别失败: {str(e)}")
    
    @pyqtSlot()
    def stop_listening(self):
        """停止语音识别"""
        try:
            if self.speech_recognizer:
                self.speech_recognizer.stop_listening()
        except Exception as e:
            self.on_error_occurred(f"停止语音识别失败: {str(e)}")
    
    @pyqtSlot(str)
    def change_engine(self, engine):
        """切换语音识别引擎"""
        try:
            if engine in self.engines:
                # 停止当前识别
                if self.speech_recognizer and hasattr(self.speech_recognizer, 'is_listening'):
                    if self.speech_recognizer.is_listening:
                        self.speech_recognizer.stop_listening()
                
                # 切换引擎
                self.current_engine = engine
                self.init_speech_recognizer()
                self.on_status_changed(f"已切换到{engine}引擎")
        except Exception as e:
            self.on_error_occurred(f"切换引擎失败: {str(e)}")
    
    @pyqtSlot(bool)
    def toggle_always_on_top(self, enabled):
        """切换窗口置顶"""
        parent = self.parent()
        if parent and hasattr(parent, 'toggle_always_on_top'):
            parent.toggle_always_on_top(enabled)
    
    def on_text_recognized(self, text):
        """处理识别到的文本"""
        # 通过JavaScript调用前端方法
        script = f"window.speechToTextAPI.onTextRecognized({json.dumps(text)});"
        if hasattr(self.parent(), 'web_view'):
            self.parent().web_view.page().runJavaScript(script)
    
    def on_status_changed(self, status):
        """处理状态变化"""
        script = f"window.speechToTextAPI.onStatusChanged({json.dumps(status)});"
        if hasattr(self.parent(), 'web_view'):
            self.parent().web_view.page().runJavaScript(script)
    
    def on_error_occurred(self, error):
        """处理错误"""
        script = f"window.speechToTextAPI.onErrorOccurred({json.dumps(error)});"
        if hasattr(self.parent(), 'web_view'):
            self.parent().web_view.page().runJavaScript(script)


class SpeechWebView(QMainWindow):
    """集成WebView的主窗口"""
    
    def __init__(self):
        super().__init__()
        self.is_always_on_top = False
        self.init_ui()
        self.init_webview()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('🎙️ 语音助手')
        self.setGeometry(100, 100, 800, 600)
        
        # 设置窗口图标
        self.setWindowIcon(QIcon('🎙️'))
        
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # 创建WebView
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
    
    def init_webview(self):
        """初始化WebView"""
        # 创建WebChannel用于Python和JavaScript通信
        self.web_channel = QWebChannel()
        
        # 创建API对象
        self.api = SpeechWebAPI(self)
        
        # 注册API对象到WebChannel
        self.web_channel.registerObject('pywebview', self.api)
        
        # 设置WebChannel到WebView
        self.web_view.page().setWebChannel(self.web_channel)
        
        # 设置Web页面
        self.load_web_page()
    
    def load_web_page(self):
        """加载Web页面"""
        # 方法1：加载本地文件（开发环境）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 如果React应用已构建
        build_dir = os.path.join(current_dir, 'frontend', 'build', 'index.html')
        if os.path.exists(build_dir):
            self.web_view.load(QUrl.fromLocalFile(build_dir))
        else:
            # 方法2：加载开发服务器（如果运行了npm start）
            self.web_view.load(QUrl('http://localhost:3000'))
            
            # 方法3：加载静态HTML（备用方案）
            if not self.web_view.url().isValid():
                self.load_fallback_html()
    
    def load_fallback_html(self):
        """加载备用HTML页面"""
        html_content = """
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="utf-8">
            <title>语音助手</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei';
                    text-align: center;
                    padding: 50px;
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                }
            </style>
        </head>
        <body>
            <h1>🎙️ 语音助手</h1>
            <p>前端页面加载中...</p>
            <p>请确保React应用已构建或开发服务器正在运行。</p>
        </body>
        </html>
        """
        self.web_view.setHtml(html_content)
    
    def toggle_always_on_top(self, enabled):
        """切换窗口置顶"""
        self.is_always_on_top = enabled
        
        if enabled:
            self.setWindowFlags(self.windowFlags() | 
                              self.windowFlags().__class__.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & 
                              ~self.windowFlags().__class__.WindowStaysOnTopHint)
        
        self.show()
    
    def closeEvent(self, event):
        """关闭事件处理"""
        if self.api.speech_recognizer and hasattr(self.api.speech_recognizer, 'is_listening'):
            if self.api.speech_recognizer.is_listening:
                self.api.speech_recognizer.stop_listening()
        event.accept()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("语音助手")
    
    # 创建主窗口
    window = SpeechWebView()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main() 