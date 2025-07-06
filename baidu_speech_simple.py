"""
简化的百度语音识别实现
使用SpeechRecognition库内置的百度识别功能
"""
import speech_recognition as sr
import threading
import time
from PyQt5.QtCore import QObject, pyqtSignal

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False


class BaiduSpeechSimple(QObject):
    """简化的百度语音识别器"""
    
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
        
        # 检查PyAudio
        if not PYAUDIO_AVAILABLE:
            self.error_occurred.emit("PyAudio 未安装！请运行 install_pyaudio.bat")
            return
        
        # 初始化麦克风
        self._init_microphone()
        
        # 设置识别器参数
        self._setup_recognizer()
        
        # 标点符号处理
        self.sentence_keywords = ["什么", "怎么", "为什么", "哪里", "谁", "吗", "呢", "如何", "多少"]
    
    def _init_microphone(self):
        """初始化麦克风，并提供设备列表"""
        try:
            mic_list = sr.Microphone.list_microphone_names()
            if not mic_list:
                self.error_occurred.emit("未检测到任何麦克风设备！")
                self.microphone = None
                return

            # 尝试使用默认麦克风
            try:
                self.microphone = sr.Microphone()
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                self.status_changed.emit("默认麦克风已就绪")
                return
            except Exception as e:
                print(f"默认麦克风失败: {e}。尝试其他设备...")

            # 如果默认失败，遍历所有设备
            for i, mic_name in enumerate(mic_list):
                try:
                    self.microphone = sr.Microphone(device_index=i)
                    with self.microphone as source:
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    self.status_changed.emit(f"使用麦克风: {mic_name}")
                    return # 找到一个可用的就退出
                except Exception:
                    continue # 失败了就尝试下一个
            
            # 如果所有设备都失败了
            self.error_occurred.emit("所有麦克风设备均初始化失败。")
            self.microphone = None

        except Exception as e:
            self.error_occurred.emit(f"麦克风初始化过程中发生未知错误: {str(e)}")
            self.microphone = None
    
    def _setup_recognizer(self):
        """设置识别器参数"""
        self.recognizer.energy_threshold = 1000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 1.5
    
    def _recognize_audio(self, audio_data):
        """识别音频"""
        try:
            # 尝试使用百度识别
            try:
                # 如果安装了baidu-aip，尝试使用百度识别
                result = self.recognizer.recognize_baidu(audio_data, language='zh')
                if result and result.strip():
                    return result
            except:
                pass
            
            # 如果百度不可用，回退到Google识别
            result = self.recognizer.recognize_google(audio_data, language='zh-CN')
            if result and result.strip():
                return result
                
        except Exception as e:
            if "Service Unavailable" in str(e):
                raise Exception("网络连接问题，语音识别服务暂时不可用")
            else:
                raise Exception(f"语音识别失败: {str(e)}")
    
    def _add_punctuation(self, text):
        """添加标点符号"""
        if not text:
            return text
        
        text = text.strip()
        
        # 如果已有标点符号，不重复添加
        if text.endswith(('。', '？', '！', '，', '、', '；', '：')):
            return text
        
        # 检查疑问词
        for keyword in self.sentence_keywords:
            if keyword in text:
                return text + "？"
        
        # 根据长度和内容判断
        if len(text) > 15:
            return text + "。"
        elif any(word in text for word in ["但是", "然后", "而且", "另外", "首先", "其次"]):
            return text + "，"
        else:
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
        self.status_changed.emit("开始监听 - 百度语音识别")
    
    def stop_listening(self):
        """停止监听"""
        self.is_listening = False
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=1)
        self.status_changed.emit("停止监听")
    
    def _listen_loop(self):
        """监听循环"""
        consecutive_timeouts = 0
        
        while self.is_listening:
            try:
                # 增加麦克风有效性检查
                if not self.microphone:
                    self.error_occurred.emit("错误: 麦克风未初始化。")
                    self.is_listening = False
                    break

                with self.microphone as source:
                    self.status_changed.emit("请说话...")
                    audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=30)
                
                consecutive_timeouts = 0
                self.status_changed.emit("正在识别（百度）...")
                
                text = self._recognize_audio(audio)
                
                if text:
                    text_with_punctuation = self._add_punctuation(text)
                    self.text_recognized.emit(text_with_punctuation)
                    self.status_changed.emit("请继续说话...")
                
            except sr.WaitTimeoutError:
                consecutive_timeouts += 1
                if consecutive_timeouts >= 1:
                    self.status_changed.emit("长时间无语音，停止监听")
                    self.is_listening = False
                    break
                else:
                    self.status_changed.emit("等待语音输入...")
            except Exception as e:
                self.error_occurred.emit(f"识别错误: {str(e)}")
                time.sleep(2)
    
    def get_engine_info(self):
        """获取引擎信息"""
        return {
            'name': '百度语音识别',
            'description': '使用百度语音识别服务，对中文识别效果好',
            'network_required': True,
            'free_quota': '每天有免费额度',
            'languages': ['中文', '英文'],
            'features': ['实时识别', '高准确率', '快速响应']
        } 