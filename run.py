"""
Application runner script / 应用程序启动脚本
应用程序启动脚本。此脚本配置系统路径然后启动Uvicorn服务器。
使用此脚本可确保应用程序的Python路径设置正确，即使Uvicorn的重载器创建新进程时也是如此。

运行应用程序的方法:
python run.py
"""

import sys
import os
import uvicorn

def main():
    """主函数 - 配置环境并启动服务器"""
    # 将'backend'目录添加到Python路径中
    # 这确保了像'from app.core...'这样的绝对导入能正确工作
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend'))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

    # 将当前工作目录更改为'backend'
    # 这对于应用程序内的相对路径通常是必需的（例如，模板或静态文件）
    # 并帮助Uvicorn找到应用程序模块
    os.chdir(backend_dir)

    # 运行Uvicorn服务器
    # 我们将应用程序指定为字符串'main:app'
    # 'reload_dirs'设置为backend目录以监视更改
    uvicorn.run(
        "main:app",                    # FastAPI应用程序实例
        host="0.0.0.0",               # 监听所有接口
        port=8080,                     # 服务器端口
        reload=True,                   # 开发模式自动重载
        reload_dirs=[backend_dir],     # 监视backend目录的文件变化
        log_config=None,               # 我们在应用程序内使用structlog
    )

if __name__ == "__main__":
    main() 