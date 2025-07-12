# 🎙️ 现代化语音助手 (Modern Speech-to-Text Assistant)

这是一个基于 PyQt5 的现代化语音转文字桌面插件，采用了受 TDesign 和 QQ 音乐启发的简约设计风格。

![App Screenshot](https://raw.githubusercontent.com/RoyalTeng/recordMytalk/main/screenshot.png)  <!-- 预留截图位置 -->

---

### ✨ 功能特性

- **现代化UI设计**: 采用卡片式布局，视觉风格简约、清晰。
- **双引擎支持**: 
  - **百度语音**: 中文识别效果出色，响应迅速。
  - **Google语音**: 支持全球多种语言，覆盖面广。
- **实时状态反馈**: 清晰的状态栏，实时显示录音、识别中、成功、失败等状态。
- **核心交互功能**:
  - 一键清空文本
  - 一键复制全部内容
  - 窗口置顶，方便在任何应用上使用
  - 空格键快速启动/停止录音
- **轻量级与专注**: 项目文件精简，只保留核心功能，易于维护和二次开发。

---

### 🚀 如何运行

#### 1. 环境准备

确保您的电脑上已安装 Python (建议 3.8 或更高版本)。

#### 2. 安装依赖

在项目根目录下打开终端，运行以下命令来安装所有必需的库：

```bash
pip install -r requirements.txt
```

#### 3. 运行程序

直接运行主程序文件即可启动语音助手：

```bash
python main_ui.py
```

或者，您也可以直接双击项目中的 `run.bat` 文件一键启动。

---

### 📂 项目结构

```
/
├── main_ui.py                 # 主程序UI和逻辑
├── speech_recognizer.py       # Google语音识别模块
├── baidu_speech_simple.py     # 百度语音识别模块
├── requirements.txt           # 项目依赖
├── icons.qrc                  # Qt 图标资源文件
├── icons_rc.py                # 编译后的Python资源
├── FontAwesome.ttf            # 图标字体文件
├── run.bat                    # Windows快速启动脚本
└── README.md                  # 本文档
```

## 系统要求

- Windows 操作系统
- Python 3.7 或更高版本
- 麦克风设备
- 网络连接（用于语音识别）

## 安装依赖

1. 首先确保已安装 Python 3.7+
2. 使用 pip 安装依赖包：

```bash
pip install -r requirements.txt
```

## 运行程序

### 方法1：使用完整安装脚本（推荐）
```bash
# 双击运行 run.bat
# 脚本会自动检查并安装所有依赖
```

### 方法2：使用简化启动器
```bash
# 双击运行 simple_run.bat
# 如果 PyAudio 有问题，会给出安装提示
```

### 方法3：手动运行
```bash
python main.py
```

## 使用说明

1. 启动程序后，会出现一个简洁的窗口
2. 点击「开始语音识别」按钮开始录音
3. 对着麦克风说话，识别结果会显示在文本框中
4. 可以直接编辑文本框中的内容
5. 窗口支持拖拽移动和缩放大小

## 打包为 .exe 文件

使用 PyInstaller 将程序打包为独立的 .exe 文件：

### 1. 安装 PyInstaller

```bash
pip install pyinstaller
```

### 2. 创建打包脚本

创建一个 `build.bat` 文件：

```batch
@echo off
echo 正在打包语音转文字插件...

pyinstaller --onefile --windowed --name "语音转文字插件" --icon=icon.ico main.py

echo 打包完成！
echo 可执行文件位于 dist/ 目录中
pause
```

### 3. 执行打包

```bash
# 基本打包（带控制台）
pyinstaller --onefile main.py

# 无控制台窗口打包
pyinstaller --onefile --windowed main.py

# 自定义打包（推荐）
pyinstaller --onefile --windowed --name "语音转文字插件" main.py
```

### 4. 打包选项说明

- `--onefile`: 打包为单个 .exe 文件
- `--windowed`: 不显示控制台窗口
- `--name`: 自定义输出文件名
- `--icon`: 指定图标文件（可选）
- `--add-data`: 添加额外的数据文件（如需要）

## 项目结构

```
recordMytalk/
├── main.py                 # 主程序入口
├── gui.py                  # GUI 界面模块
├── speech_recognizer.py    # 语音识别模块
├── requirements.txt        # 依赖包列表（不含 PyAudio）
├── README.md              # 说明文档
├── run.bat                # 完整启动脚本
├── simple_run.bat         # 简化启动脚本
├── install_pyaudio.bat    # PyAudio 专用安装脚本
├── build.bat              # 打包脚本
└── dist/                  # 打包输出目录（运行打包后生成）
```

## PyAudio 安装问题解决方案

**⚠️ 重要：PyAudio 在 Windows 上安装可能遇到问题，这是正常现象！**

### 🔧 自动安装 PyAudio

```bash
# 双击运行 install_pyaudio.bat
# 脚本会自动尝试多种安装方法
```

### 🛠️ 手动安装 PyAudio

#### 方法1：使用预编译文件（推荐）
1. 访问：https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
2. 下载对应 Python 版本的 .whl 文件
3. 例如：`PyAudio-0.2.11-cp39-cp39-win_amd64.whl`
4. 运行：`pip install 下载的文件名.whl`

#### 方法2：使用 pipwin
```bash
pip install pipwin
pipwin install pyaudio
```

#### 方法3：使用 Anaconda
```bash
conda install pyaudio
```

## 常见问题

### 1. 程序启动但无法识别语音

如果程序能启动但点击按钮后提示 PyAudio 错误：
- 运行 `install_pyaudio.bat` 安装 PyAudio
- 或者按照上面的手动安装方法操作

### 2. 麦克风权限问题

确保：
- 麦克风设备正常工作
- 系统允许应用访问麦克风
- 在 Windows 设置中启用麦克风权限

### 3. 网络连接问题

本程序使用 Google 语音识别服务，需要：
- 稳定的网络连接
- 能够访问 Google 服务
- 如果网络受限，可以考虑使用离线语音识别方案

### 4. 识别准确度优化

- 在安静环境中使用
- 说话清晰，语速适中
- 麦克风距离嘴巴 15-30cm
- 避免背景噪音

## 技术栈

- **GUI框架**: PyQt5
- **语音识别**: SpeechRecognition
- **音频处理**: PyAudio
- **打包工具**: PyInstaller

## 开发说明

### 模块说明

- `main.py`: 程序入口点，负责启动应用
- `gui.py`: 用户界面实现，包含主窗口和事件处理
- `speech_recognizer.py`: 语音识别核心功能，支持单次和连续识别

### 扩展功能

如需添加更多功能，可以考虑：
- 保存识别结果到文件
- 添加快捷键支持
- 集成离线语音识别（如 Whisper）
- 支持多语言识别
- 添加语音命令功能

## 许可证

本项目采用 MIT 许可证。

## 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。 