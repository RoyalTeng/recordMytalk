import React, { useState, useRef, useEffect } from 'react';
import {
  Layout,
  Header,
  Content,
  Footer,
  Button,
  Input,
  Space,
  Dropdown,
  Message,
  Dialog,
  Card,
  Tag,
  Tooltip
} from 'tdesign-react';
import {
  MicrophoneIcon,
  StopCircleIcon,
  PlayCircleIcon,
  SettingIcon,
  ClearIcon,
  CopyIcon,
  PinIcon,
  SoundIcon
} from 'tdesign-icons-react';
import './SpeechApp.css';

const { TextArea } = Input;

const SpeechApp = () => {
  // 状态管理
  const [isRecording, setIsRecording] = useState(false);
  const [text, setText] = useState('');
  const [status, setStatus] = useState('准备就绪');
  const [engine, setEngine] = useState('baidu');
  const [isPinned, setIsPinned] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  
  const textAreaRef = useRef(null);

  // 语音识别引擎选项
  const engineOptions = [
    { label: '百度语音识别', value: 'baidu' },
    { label: 'Google语音识别', value: 'google' },
    { label: '本地语音识别', value: 'local' }
  ];

  // 状态颜色映射
  const getStatusColor = (status) => {
    if (status.includes('正在')) return 'warning';
    if (status.includes('准备') || status.includes('就绪')) return 'success';
    if (status.includes('错误') || status.includes('失败')) return 'danger';
    return 'default';
  };

  // 开始/停止录音
  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const startRecording = () => {
    setIsRecording(true);
    setStatus('正在录音...');
    
    // 🔗 这里是与Python后端的接口挂钩点
    // 调用Python的语音识别功能
    if (window.pywebview) {
      // 如果是WebView环境
      window.pywebview.api.start_listening(engine);
    } else if (window.electronAPI) {
      // 如果是Electron环境
      window.electronAPI.startRecording(engine);
    } else {
      // 开发环境模拟
      console.log('开始语音识别，引擎:', engine);
      simulateRecording();
    }
  };

  const stopRecording = () => {
    setIsRecording(false);
    setStatus('处理中...');
    
    // 🔗 这里是与Python后端的接口挂钩点
    if (window.pywebview) {
      window.pywebview.api.stop_listening();
    } else if (window.electronAPI) {
      window.electronAPI.stopRecording();
    } else {
      // 开发环境模拟
      console.log('停止语音识别');
      setTimeout(() => setStatus('准备就绪'), 1000);
    }
  };

  // 开发环境模拟录音
  const simulateRecording = () => {
    setTimeout(() => {
      const mockText = '这是一段模拟的语音识别结果。';
      setText(prev => prev + mockText);
      setStatus('识别完成');
      setTimeout(() => {
        setIsRecording(false);
        setStatus('准备就绪');
      }, 1000);
    }, 3000);
  };

  // 清空文本
  const clearText = () => {
    Dialog.confirm({
      header: '确认清空',
      body: '确定要清空所有文本内容吗？',
      onConfirm: () => {
        setText('');
        Message.success('文本已清空');
      }
    });
  };

  // 复制文本
  const copyText = () => {
    if (!text.trim()) {
      Message.warning('没有可复制的内容');
      return;
    }
    
    navigator.clipboard.writeText(text).then(() => {
      Message.success('文本已复制到剪贴板');
    }).catch(() => {
      Message.error('复制失败，请手动复制');
    });
  };

  // 切换置顶
  const togglePin = () => {
    setIsPinned(!isPinned);
    
    // 🔗 这里是与Python后端的接口挂钩点
    if (window.pywebview) {
      window.pywebview.api.toggle_always_on_top(!isPinned);
    } else if (window.electronAPI) {
      window.electronAPI.togglePin(!isPinned);
    }
    
    Message.info(isPinned ? '已取消置顶' : '窗口已置顶');
  };

  // 切换引擎
  const handleEngineChange = (value) => {
    setEngine(value);
    setStatus(`已切换到${engineOptions.find(e => e.value === value)?.label}`);
    
    // 🔗 这里是与Python后端的接口挂钩点
    if (window.pywebview) {
      window.pywebview.api.change_engine(value);
    } else if (window.electronAPI) {
      window.electronAPI.changeEngine(value);
    }
    
    setTimeout(() => setStatus('准备就绪'), 2000);
  };

  // 设置下拉菜单
  const settingsDropdown = (
    <div className="settings-dropdown">
      <div className="dropdown-item" onClick={() => setShowSettings(true)}>
        <SettingIcon />
        <span>设置</span>
      </div>
      <div className="dropdown-item">
        <SoundIcon />
        <span>音频设置</span>
      </div>
    </div>
  );

  // 监听来自Python的消息
  useEffect(() => {
    const handlePythonMessage = (event) => {
      const { type, data } = event.detail;
      
      switch (type) {
        case 'text_recognized':
          setText(prev => prev + data);
          break;
        case 'status_changed':
          setStatus(data);
          break;
        case 'error_occurred':
          setStatus('识别错误');
          setIsRecording(false);
          Message.error(data);
          break;
        default:
          break;
      }
    };

    // 监听自定义事件
    window.addEventListener('pythonMessage', handlePythonMessage);
    
    return () => {
      window.removeEventListener('pythonMessage', handlePythonMessage);
    };
  }, []);

  return (
    <Layout className="speech-app">
      {/* 顶部导航栏 */}
      <Header className="app-header">
        <div className="header-left">
          <div className="app-logo">
            <MicrophoneIcon size="24px" />
            <span className="app-title">语音助手</span>
          </div>
        </div>
        
        <div className="header-center">
          <Tag 
            theme={getStatusColor(status)} 
            variant="light"
            className="status-tag"
          >
            {status}
          </Tag>
        </div>
        
        <div className="header-right">
          <Space size="small">
            <Dropdown 
              trigger="click"
              content={
                <div className="engine-dropdown">
                  {engineOptions.map(option => (
                    <div 
                      key={option.value}
                      className={`dropdown-item ${engine === option.value ? 'active' : ''}`}
                      onClick={() => handleEngineChange(option.value)}
                    >
                      {option.label}
                    </div>
                  ))}
                </div>
              }
            >
              <Button variant="text" size="small">
                {engineOptions.find(e => e.value === engine)?.label}
              </Button>
            </Dropdown>
            
            <Tooltip content={isPinned ? "取消置顶" : "窗口置顶"}>
              <Button 
                variant="text" 
                size="small"
                theme={isPinned ? "primary" : "default"}
                onClick={togglePin}
              >
                <PinIcon />
              </Button>
            </Tooltip>
            
            <Dropdown trigger="click" content={settingsDropdown}>
              <Button variant="text" size="small">
                <SettingIcon />
              </Button>
            </Dropdown>
          </Space>
        </div>
      </Header>

      {/* 中央内容区 */}
      <Content className="app-content">
        <Card className="text-card" bordered={false}>
          <div className="text-area-container">
            <TextArea
              ref={textAreaRef}
              value={text}
              onChange={setText}
              placeholder="语音识别结果将显示在这里...&#10;&#10;您也可以直接在此编辑文本内容。"
              autosize={{ minRows: 8, maxRows: 20 }}
              className="main-textarea"
            />
            
            {text && (
              <div className="text-stats">
                <span>{text.length} 字符</span>
                <span>{text.split(/\s+/).filter(word => word.length > 0).length} 词</span>
              </div>
            )}
          </div>
        </Card>
      </Content>

      {/* 底部操作栏 */}
      <Footer className="app-footer">
        <div className="footer-content">
          <div className="footer-left">
            <Space>
              <Button 
                variant="outline" 
                size="medium"
                onClick={clearText}
                disabled={!text}
              >
                <ClearIcon />
                清空
              </Button>
              
              <Button 
                variant="outline" 
                size="medium"
                onClick={copyText}
                disabled={!text}
              >
                <CopyIcon />
                复制
              </Button>
            </Space>
          </div>
          
          <div className="footer-center">
            <Button
              theme="primary"
              size="large"
              shape="circle"
              onClick={toggleRecording}
              className={`record-btn ${isRecording ? 'recording' : ''}`}
              disabled={status.includes('处理')}
            >
              {isRecording ? (
                <StopCircleIcon size="32px" />
              ) : (
                <MicrophoneIcon size="32px" />
              )}
            </Button>
          </div>
          
          <div className="footer-right">
            <Space>
              <Button variant="text" size="small">
                快捷键: Space
              </Button>
            </Space>
          </div>
        </div>
      </Footer>
      
      {/* 设置对话框 */}
      <Dialog
        header="设置"
        visible={showSettings}
        onClose={() => setShowSettings(false)}
        footer={
          <Button onClick={() => setShowSettings(false)}>
            关闭
          </Button>
        }
      >
        <div className="settings-content">
          <p>更多设置功能开发中...</p>
        </div>
      </Dialog>
    </Layout>
  );
};

export default SpeechApp; 