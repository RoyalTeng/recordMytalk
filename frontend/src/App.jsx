import React from 'react';
import { ConfigProvider } from 'tdesign-react';
import SpeechApp from './components/SpeechApp';
import './App.css';

// TDesign配置
const tdConfig = {
  // 全局主题配置
  theme: {
    // 主色调设置为QQ音乐绿
    primary: '#00c756',
  },
  // 组件默认属性配置
  components: {
    Button: {
      // 按钮默认配置
    },
    Input: {
      // 输入框默认配置
    }
  }
};

function App() {
  return (
    <ConfigProvider>
      <div className="app-container">
        <SpeechApp />
      </div>
    </ConfigProvider>
  );
}

export default App; 