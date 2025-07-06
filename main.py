"""
语音转文字插件主程序
极简风格的 Windows 桌面语音识别应用
"""
import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui import create_application


def main():
    """主函数"""
    try:
        # 创建应用程序
        app, window = create_application()
        
        # 运行应用程序
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"程序启动失败: {str(e)}")
        input("按回车键退出...")
        sys.exit(1)


if __name__ == "__main__":
    main() 