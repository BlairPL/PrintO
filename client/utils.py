# client/utils.py
import os
import sys

SERVER_PORT = 0

def get_abs_path(relative_path: str) -> str:
    """获取资源绝对路径，开发环境以当前脚本目录为基准"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, relative_path)
    return full_path.replace("\\", "/")

def get_resource_path(relative_path: str) -> str:
    # 1. 自动匹配当前环境的基准根目录
    if getattr(sys, 'frozen', False):
        # 打包后运行环境
        if hasattr(sys, '_MEIPASS'):
            # 单文件(--onefile)模式：资源解压到临时_MEIPASS目录
            base_dir = sys._MEIPASS
        else:
            # 目录模式(--onedir)：基准目录为exe所在文件夹
            base_dir = os.path.dirname(sys.executable)
    else:
        # 开发调试环境：基准目录为当前脚本所在目录
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. 拼接基准目录与传入的相对路径，返回规范化的绝对路径
    return os.path.normpath(os.path.join(base_dir, relative_path))