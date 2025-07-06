"""
本地语音识别模块
优先使用本地服务，避免网络依赖
"""
import speech_recognition as sr
import threading
import time
from PyQt5.QtCore import QObject, pyqtSignal

# 尝试导入 PyAudio
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

# 尝试导入 Windows Speech API
try:
    import win32com.client
    WINDOWS_SPEECH_AVAILABLE = True
except ImportError:
    WINDOWS_SPEECH_AVAILABLE = False


class LocalSpeechRecognizer(QObject):
    """本地语音识别器类"""
    
    # 定义信号
    text_recognized = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.is_listening = False
        self.listen_thread = None
        self.use_windows_speech = WINDOWS_SPEECH_AVAILABLE
        
        # 检查可用的识别引擎
        self.available_engines = self._check_available_engines()
        
        # 检查 PyAudio 是否可用
        if not PYAUDIO_AVAILABLE:
            self.error_occurred.emit("PyAudio 未安装！请运行 install_pyaudio.bat 安装 PyAudio")
            return
        
        # 初始化麦克风
        self._init_microphone()
        
        # 设置识别器参数
        self._setup_recognizer()
        
        # 标点符号处理
        self.sentence_keywords = ["什么", "怎么", "为什么", "哪里", "谁", "吗", "呢"]
    
    def _check_available_engines(self):
        """检查可用的语音识别引擎"""
        engines = []
        
        if WINDOWS_SPEECH_AVAILABLE:
            engines.append({
                'name': 'windows',
                'display_name': 'Windows语音识别',
                'priority': 1,
                'description': '使用Windows内置语音识别'
            })
        
        # 检查是否可以使用Sphinx离线识别
        try:
            # 尝试创建一个测试识别器
            test_recognizer = sr.Recognizer()
            engines.append({
                'name': 'sphinx',
                'display_name': '离线语音识别',
                'priority': 2,
                'description': 'PocketSphinx离线识别'
            })
        except:
            pass
        
        # 网络识别作为备用
        engines.append({
            'name': 'google',
            'display_name': 'Google语音识别',
            'priority': 3,
            'description': '需要网络连接'
        })
        
        return sorted(engines, key=lambda x: x['priority'])
    
    def _init_microphone(self):
        """初始化麦克风"""
        try:
            self.microphone = sr.Microphone()
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self.status_changed.emit("麦克风已就绪")
        except Exception as e:
            self.error_occurred.emit(f"麦克风初始化失败: {str(e)}")
    
    def _setup_recognizer(self):
        """设置识别器参数"""
        self.recognizer.energy_threshold = 1000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 1.5
    
    def _recognize_windows(self, audio):
        """使用Windows语音识别"""
        if not WINDOWS_SPEECH_AVAILABLE:
            raise Exception("Windows语音识别不可用")
        
        try:
            # 创建Windows语音识别对象
            speech_engine = win32com.client.Dispatch("SAPI.SpVoice")
            recognizer = win32com.client.Dispatch("SAPI.SpSharedRecognizer")
            
            # 这里需要实现具体的Windows语音识别逻辑
            # 由于Windows语音识别API较复杂，这里提供一个简化版本
            raise Exception("Windows语音识别功能正在开发中")
            
        except Exception as e:
            raise Exception(f"Windows语音识别失败: {str(e)}")
    
    def _recognize_sphinx(self, audio):
        """使用Sphinx离线识别"""
        try:
            return self.recognizer.recognize_sphinx(audio, language='zh-CN')
        except Exception as e:
            raise Exception(f"离线识别失败: {str(e)}")
    
    def _recognize_google(self, audio):
        """使用Google识别（备用）"""
        try:
            return self.recognizer.recognize_google(audio, language='zh-CN')
        except Exception as e:
            raise Exception(f"Google识别失败: {str(e)}")
    
    def _recognize_with_fallback(self, audio):
        """使用备用识别引擎"""
        errors = []
        
        for engine in self.available_engines:
            try:
                if engine['name'] == 'windows':
                    result = self._recognize_windows(audio)
                elif engine['name'] == 'sphinx':
                    result = self._recognize_sphinx(audio)
                elif engine['name'] == 'google':
                    result = self._recognize_google(audio)
                else:
                    continue
                
                if result and result.strip():
                    return result
                    
            except Exception as e:
                errors.append(f"{engine['display_name']}: {str(e)}")
                continue
        
        # 所有引擎都失败
        error_msg = "所有识别引擎都失败了:\n" + "\n".join(errors)
        raise Exception(error_msg)
    
    def _add_punctuation(self, text):
        """添加标点符号"""
        if not text:
            return text
        
        text = text.strip()
        
        # 如果已有标点符号，不重复添加
        if text.endswith(('。', '？', '！', '，')):
            return text
        
        # 检查疑问词
        for keyword in self.sentence_keywords:
            if keyword in text:
                return text + "？"
        
        # 默认添加句号
        return text + "。"
    
    def start_listening(self):
        """开始监听"""
        if not self.microphone:
            self.error_occurred.emit("麦克风未初始化")
            return
        
        if self.is_listening:
            return
        
        self.is_listening = True
        self.listen_thread = threading.Thread(target=self._listen_loop)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        self.status_changed.emit("开始监听...")
    
    def stop_listening(self):
        """停止监听"""
        self.is_listening = False
        if self.listen_thread:
            self.listen_thread.join(timeout=1)
        self.status_changed.emit("停止监听")
    
    def _listen_loop(self):
        """监听循环"""
        while self.is_listening:
            try:
                with self.microphone as source:
                    self.status_changed.emit("请说话...")
                    audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=30)
                
                self.status_changed.emit("正在识别...")
                text = self._recognize_with_fallback(audio)
                
                if text:
                    text_with_punctuation = self._add_punctuation(text)
                    self.text_recognized.emit(text_with_punctuation)
                    self.status_changed.emit("请继续说话...")
                
            except sr.WaitTimeoutError:
                self.status_changed.emit("超时，停止监听")
                self.is_listening = False
                break
            except Exception as e:
                self.error_occurred.emit(f"识别错误: {str(e)}")
                time.sleep(2)
    
    def get_engine_status(self):
        """获取识别引擎状态"""
        status = "可用的识别引擎:\n\n"
        
        if not self.available_engines:
            status += "• 没有可用的识别引擎\n"
        else:
            for i, engine in enumerate(self.available_engines, 1):
                status += f"{i}. {engine['display_name']}\n"
                status += f"   {engine['description']}\n\n"
        
        return status 