"""
语音识别模块
使用 SpeechRecognition 库实现语音转文字功能
支持多种识别引擎：百度、Google、离线识别
"""
import speech_recognition as sr
import threading
import time
from PyQt5.QtCore import QObject, pyqtSignal

# 尝试导入 PyAudio，如果失败则设置标志
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False


class SpeechRecognizer(QObject):
    """语音识别器类"""
    
    # 定义信号
    text_recognized = pyqtSignal(str)  # 识别到文本时发出信号
    error_occurred = pyqtSignal(str)   # 发生错误时发出信号
    status_changed = pyqtSignal(str)   # 状态变化时发出信号
    
    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.is_listening = False
        self.listen_thread = None
        
        # 识别引擎配置（按优先级排序）
        self.recognition_engines = [
            {
                'name': 'Baidu',
                'method': self._recognize_baidu,
                'description': '百度语音识别'
            },
            {
                'name': 'Google',
                'method': self._recognize_google,
                'description': 'Google语音识别'
            },
            {
                'name': 'Sphinx',
                'method': self._recognize_sphinx,
                'description': '离线语音识别'
            }
        ]
        
        # 检查 PyAudio 是否可用
        if not PYAUDIO_AVAILABLE:
            self.error_occurred.emit("PyAudio 未安装！请运行 install_pyaudio.bat 安装 PyAudio")
            return
        
        try:
            # 尝试使用默认麦克风，如果失败则尝试其他设备
            try:
                self.microphone = sr.Microphone()
            except Exception as e1:
                # 如果默认麦克风失败，尝试使用 Realtek 麦克风 (设备 23)
                try:
                    self.microphone = sr.Microphone(device_index=23)
                except Exception as e2:
                    # 如果还是失败，尝试 Microsoft Sound Mapper (设备 0)
                    try:
                        self.microphone = sr.Microphone(device_index=0)
                    except Exception as e3:
                        # 所有麦克风设备都失败，给出详细提示
                        self._handle_microphone_error(e1, e2, e3)
                        return
            
            # 调整识别器参数
            self.recognizer.energy_threshold = 1000  # 噪声阈值
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 1.5  # 静音时间阈值，增加到1.5秒
            
            # 标点符号处理参数
            self.last_text_time = 0
            self.previous_text = ""
            self.sentence_keywords = ["什么", "怎么", "为什么", "哪里", "谁", "吗", "呢"]  # 疑问词
            
            # 初始化麦克风
            self._initialize_microphone()
        except Exception as e:
            self.error_occurred.emit(f"麦克风初始化失败: {str(e)}")
            return
    
    def _recognize_baidu(self, audio):
        """百度语音识别"""
        try:
            # 使用百度API进行识别
            # 注意：这里需要百度的API密钥，可以免费申请
            # 暂时使用演示版本，实际使用需要注册百度智能云
            return self.recognizer.recognize_baidu(audio, language='zh')
        except Exception as e:
            raise Exception(f"百度识别失败: {str(e)}")
    
    def _recognize_google(self, audio):
        """Google语音识别"""
        try:
            return self.recognizer.recognize_google(audio, language='zh-CN')
        except Exception as e:
            raise Exception(f"Google识别失败: {str(e)}")
    
    def _recognize_sphinx(self, audio):
        """离线语音识别"""
        try:
            # 使用离线识别，但对中文支持不够好
            return self.recognizer.recognize_sphinx(audio, language='zh-CN')
        except Exception as e:
            raise Exception(f"离线识别失败: {str(e)}")
    
    def _recognize_audio(self, audio):
        """
        尝试使用多种识别引擎识别语音
        """
        last_error = None
        
        for engine in self.recognition_engines:
            try:
                result = engine['method'](audio)
                if result and result.strip():
                    return result
            except Exception as e:
                last_error = e
                continue
        
        # 所有引擎都失败了
        if last_error:
            raise last_error
        else:
            raise Exception("所有识别引擎都无法识别语音")
    
    def _handle_microphone_error(self, e1, e2, e3):
        """处理麦克风设备错误"""
        error_msg = "无法找到可用的麦克风设备！\n\n"
        
        # 检查错误类型，给出具体建议
        if "No Default Input Device Available" in str(e1):
            error_msg += "请检查以下设置：\n\n"
            error_msg += "1. 确保麦克风已正确连接到电脑\n"
            error_msg += "2. 检查系统声音设置：\n"
            error_msg += "   - 右键点击任务栏音量图标\n"
            error_msg += "   - 选择'声音设置'\n"
            error_msg += "   - 确保输入设备已启用\n\n"
            error_msg += "3. 如果使用蓝牙耳机：\n"
            error_msg += "   - 确保蓝牙已连接\n"
            error_msg += "   - 重新连接蓝牙设备\n\n"
            error_msg += "4. 重启程序或重新插拔麦克风"
        else:
            error_msg += f"详细错误信息：\n"
            error_msg += f"• 默认设备: {str(e1)}\n"
            error_msg += f"• 内置麦克风: {str(e2)}\n"
            error_msg += f"• 系统映射器: {str(e3)}"
        
        self.error_occurred.emit(error_msg)

    def _initialize_microphone(self):
        """初始化麦克风"""
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self.status_changed.emit("麦克风已连接，可以开始语音识别")
        except Exception as e:
            self.error_occurred.emit(f"麦克风初始化失败: {str(e)}")
    
    def _add_punctuation(self, text, pause_duration=0):
        """
        根据语音内容和停顿时间添加标点符号
        """
        if not text:
            return text
        
        # 去除首尾空格
        text = text.strip()
        
        # 如果文本已经以标点符号结尾，不再添加
        if text.endswith(('。', '？', '！', '，', '、', '；', '：')):
            return text
        
        # 检查是否包含疑问词，如果是则添加问号
        for keyword in self.sentence_keywords:
            if keyword in text:
                return text + "？"
        
        # 根据停顿时间添加标点符号
        if pause_duration > 2.0:  # 长停顿，添加句号
            return text + "。"
        elif pause_duration > 1.0:  # 中等停顿，添加逗号
            return text + "，"
        else:
            # 根据语音内容判断
            if any(word in text for word in ["但是", "然后", "而且", "另外", "首先", "其次", "最后"]):
                return text + "，"
            elif len(text) > 10:  # 长句子，添加句号
                return text + "。"
            else:
                return text + "，"
    
    def check_microphone_status(self):
        """检查麦克风状态"""
        if not PYAUDIO_AVAILABLE:
            return False, "PyAudio 未安装"
        if self.microphone is None:
            return False, "麦克风设备未初始化"
        
        # 尝试测试麦克风是否真的可用
        try:
            with self.microphone as source:
                # 简单测试，不实际录音
                pass
            return True, "麦克风正常"
        except Exception as e:
            return False, f"麦克风连接异常: {str(e)}"

    def start_listening(self):
        """开始监听语音"""
        # 检查麦克风状态
        is_ok, status_msg = self.check_microphone_status()
        if not is_ok:
            if "麦克风设备未初始化" in status_msg:
                self.error_occurred.emit("无法找到可用的麦克风设备！\n\n请检查麦克风是否正确连接到电脑。")
            else:
                self.error_occurred.emit(f"无法启动语音识别: {status_msg}")
            return
            
        if self.is_listening:
            return
        
        self.is_listening = True
        self.listen_thread = threading.Thread(target=self._listen_continuously)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        self.status_changed.emit("正在监听...")
    
    def stop_listening(self):
        """停止监听语音"""
        self.is_listening = False
        if self.listen_thread:
            self.listen_thread.join(timeout=1)
        self.status_changed.emit("监听已停止")
    
    def _listen_continuously(self):
        """持续监听语音的主循环"""
        self.status_changed.emit("请说话...")
        consecutive_timeouts = 0  # 连续超时计数
        
        while self.is_listening:
            try:
                start_time = time.time()
                
                with self.microphone as source:
                    # 监听音频：等待10秒检测声音，允许30秒长语音
                    audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=30)
                
                end_time = time.time()
                pause_duration = end_time - start_time
                
                # 重置超时计数（有声音输入）
                consecutive_timeouts = 0
                
                # 识别语音
                try:
                    self.status_changed.emit("正在识别...")
                    text = self._recognize_audio(audio)
                    
                    if text:
                        # 添加标点符号
                        text_with_punctuation = self._add_punctuation(text, pause_duration)
                        self.text_recognized.emit(text_with_punctuation)
                        self.last_text_time = end_time
                        self.previous_text = text_with_punctuation
                        self.status_changed.emit("请继续说话...")
                        
                except sr.UnknownValueError:
                    # 没有识别到清晰的语音，但继续监听
                    self.status_changed.emit("请继续说话...")
                    continue
                except Exception as e:
                    # 改进错误处理
                    if "Service Unavailable" in str(e) or "百度识别失败" in str(e):
                        self.error_occurred.emit("网络连接问题，语音识别服务暂时不可用。\n\n建议：\n1. 检查网络连接\n2. 稍后再试\n3. 或尝试使用离线识别")
                    else:
                        self.error_occurred.emit(f"语音识别错误: {str(e)}")
                    time.sleep(2)  # 等待2秒后重试
                    
            except sr.WaitTimeoutError:
                # 10秒内没有检测到声音
                consecutive_timeouts += 1
                if consecutive_timeouts >= 1:  # 第一次10秒超时就停止
                    self.status_changed.emit("长时间无语音，自动停止监听")
                    self.is_listening = False
                    break
                else:
                    self.status_changed.emit("等待语音输入...")
                    continue
            except Exception as e:
                self.error_occurred.emit(f"监听错误: {str(e)}")
                time.sleep(1)
    
    def recognize_once(self):
        """单次语音识别"""
        # 检查麦克风状态
        is_ok, status_msg = self.check_microphone_status()
        if not is_ok:
            if "麦克风设备未初始化" in status_msg:
                self.error_occurred.emit("无法找到可用的麦克风设备！\n\n请检查麦克风是否正确连接到电脑。")
            else:
                self.error_occurred.emit(f"无法启动语音识别: {status_msg}")
            return
            
        try:
            start_time = time.time()
            
            with self.microphone as source:
                self.status_changed.emit("请说话...")
                # 监听音频，最长10秒
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=10)
            
            end_time = time.time()
            pause_duration = end_time - start_time
            
            self.status_changed.emit("正在识别...")
            
            # 识别语音
            text = self._recognize_audio(audio)
            
            if text:
                # 添加标点符号
                text_with_punctuation = self._add_punctuation(text, pause_duration)
                self.text_recognized.emit(text_with_punctuation)
                self.status_changed.emit("识别完成")
            else:
                self.status_changed.emit("未识别到语音")
                
        except sr.UnknownValueError:
            self.status_changed.emit("未识别到清晰的语音")
        except Exception as e:
            # 改进错误处理
            if "Service Unavailable" in str(e) or "百度识别失败" in str(e):
                self.error_occurred.emit("网络连接问题，语音识别服务暂时不可用。\n\n建议：\n1. 检查网络连接\n2. 稍后再试\n3. 或尝试使用离线识别")
            else:
                self.error_occurred.emit(f"语音识别错误: {str(e)}")
        except sr.WaitTimeoutError:
            self.status_changed.emit("录音超时")
        except Exception as e:
            self.error_occurred.emit(f"识别错误: {str(e)}") 