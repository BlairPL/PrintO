import sys
import os
# 兼容PyInstaller无控制台模式：标准流重定向到系统空设备，不生成日志
if getattr(sys, 'frozen', False) and not sys.stdout:
    sys.stdout = open(os.devnull, 'w', encoding='utf-8',buffering=1)
    sys.stderr = open(os.devnull, 'w', encoding='utf-8',buffering=1)

import webview
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from API_for_JS import PyApi, bind_api_window
from utils import get_resource_path
import utils

# 打包环境全局日志重定向：彻底解决无控制台模式标准流失效问题
# if getattr(sys, 'frozen', False):
#     # 日志文件放在exe所在目录，单文件模式也能持久化查看
#     exe_dir = os.path.dirname(sys.executable)
#     log_file = os.path.join(exe_dir, "printo_debug.log")
#     # 行缓冲模式实时写入，避免崩溃丢失日志
#     sys.stdout = open(log_file, "w", encoding="utf-8", buffering=1)
#     sys.stderr = open(log_file, "a", encoding="utf-8", buffering=1)
#     print("=== PrintO 启动日志 ===")
#     print(f"运行模式：{'单文件模式' if hasattr(sys, '_MEIPASS') else '目录模式'}")



import ctypes
#修复Windows任务栏图标分组问题
my_app_id = "com.printo.printO.v1.0"
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)


# 先定义变量存真实端口（整数类型）
real_port = 0
server = None



# def run_server():
#     global real_port, server
#     # 如果py文件和web文件夹同级，把 "../web" 改成 "./web"
#     # web_root = get_resource_path("../web")
#     if getattr(sys, 'frozen', False):
#         web_root = get_resource_path("./web")
#     else:
#         web_root = get_resource_path("../web")
#     class StaticHandler(SimpleHTTPRequestHandler):
#         # 禁用默认访问日志，适配无控制台模式
#         def log_message(self, format, *args):
#             pass
#         def __init__(self, *args, **kwargs):
#             super().__init__(*args, directory=web_root, **kwargs)
#     # ✅ 直接让HTTPServer绑定端口0，由系统分配随机可用端口
#     server = HTTPServer(("127.0.0.1", 0), StaticHandler)
#     # ✅ 获取真实分配的端口（int类型）
#     real_port = server.server_address[1]

#     utils.SERVER_PORT = real_port
#     print(f"静态服务已启动，实际端口：{real_port}")
#     server.serve_forever()

# def run_server():
#     global real_port, server
#     try:
#         # --- 你原有的所有业务代码放在这里 ---
#         if getattr(sys, 'frozen', False):
#             web_root = get_resource_path("./web")
#         else:
#             web_root = get_resource_path("../web")

#         class StaticHandler(SimpleHTTPRequestHandler):
#             # 彻底禁用所有HTTP日志，完全规避标准流写入
#             def log_message(self, format, *args):
#                 pass
#             def log_error(self, format, *args):
#                 pass
#             def log_request(self, code='-', size='-'):
#                 pass

#             def __init__(self, *args, **kwargs):
#                 super().__init__(*args, directory=web_root, **kwargs)

#         server = HTTPServer(("127.0.0.1", 0), StaticHandler)
#         real_port = server.server_address[1]
#         print(f"静态服务启动成功，端口：{real_port}，前端根目录：{web_root}")
#         server.serve_forever()
#         # --- 原有代码结束 ---
#     except Exception as e:
#         import traceback
#         print("❌ HTTP服务启动异常：")
#         print(traceback.format_exc())
#         return

def run_server():
    global real_port, server
    try:
        if getattr(sys, 'frozen', False):
            web_root = get_resource_path("./web")
        else:
            web_root = get_resource_path("../web")

        class StaticHandler(SimpleHTTPRequestHandler):
            # 禁用HTTP服务内部日志，必须保留，否则无控制台模式仍会触发流写入错误
            def log_message(self, format, *args):
                pass
            def log_error(self, format, *args):
                pass
            def log_request(self, code='-', size='-'):
                pass

            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=web_root, **kwargs)

        server = HTTPServer(("127.0.0.1", 0), StaticHandler)
        real_port = server.server_address[1]
        server.serve_forever()
    except Exception as e:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, f"服务启动失败：{str(e)}", "程序错误", 0x10)
        return



if __name__ == '__main__':
    # 1. 启动静态文件服务
    threading.Thread(target=run_server, daemon=True).start()
    time.sleep(0.3)
    # 等待服务启动并获取端口
    # while real_port == 0:
    #     time.sleep(0.05)

    # 等待服务启动，最多等5秒，超时直接报错退出
    # wait_times = 0
    # while real_port == 0 and wait_times < 100:
    #     time.sleep(0.05)
    #     wait_times += 1

    # if real_port == 0:
    #     print("❌ 静态服务启动超时，程序退出")
    #     # 弹出系统错误提示，避免静默闪退
    #     ctypes.windll.user32.MessageBoxW(0, "服务启动失败，请查看日志文件", "程序错误", 0x10)
    #     sys.exit(1)

    wait_times = 0
    while real_port == 0 and wait_times < 100:
        time.sleep(0.05)
        wait_times += 1

    if real_port == 0:
        ctypes.windll.user32.MessageBoxW(0, "静态服务启动失败，程序即将退出", "程序错误", 0x10)
        sys.exit(1)


    

    # 2. 创建API实例与欢迎窗口，创建窗口时直接传入API保证注入时机正确
    welcome_api = PyApi()
    welcome_window = webview.create_window(
        'PrintO',
        url=f"http://127.0.0.1:{real_port}/html/welcome.html",
        js_api=welcome_api,
        width=1050,
        height=600,
        resizable=False,
    )
    # 3. 绑定API与窗口（绑定关系存在全局表，API实例本身不存窗口）
    bind_api_window(welcome_api, welcome_window)

    ico_path = get_resource_path("./ico/favicon.ico")
    # print("调试："+ico_path)

    # 4. 启动应用
    # webview.start(icon=ico_path,debug=True)
    webview.start(icon=ico_path)
    # print("后端类型：")
    # print(type(welcome_window.native))
