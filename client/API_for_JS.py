import webview
import weakref
import shutil
import os
from batch_printer import BatchPrinter 
from utils import SERVER_PORT

# 全局映射表：存储API实例ID与对应窗口的弱引用，彻底隔离API实例与窗口对象
# 不把window存在API实例上，避免pywebview注入时递归遍历到WinForms原生控件导致栈溢出
_api_window_map = {}


def bind_api_window(api_instance, window):
    """绑定API实例与对应窗口，存入全局映射表"""
    _api_window_map[id(api_instance)] = weakref.ref(window)


class PyApi:
    def __init__(self):
        # 仅存储业务数据，绝对不存储任何窗口相关引用
        self.target_folder_path = ""
        # 初始化打印工具，整个程序共用一个实例就行
        self.printer = BatchPrinter()

        #BatchPrinter运行信息
        self.batchPrinterRunningInfo = """"""

    def _get_window(self):
        """从全局映射表安全获取当前API绑定的窗口实例"""
        win_ref = _api_window_map.get(id(self))
        if not win_ref:
            raise RuntimeError("当前API未绑定窗口")
        win = win_ref()
        if not win:
            raise RuntimeError("窗口已销毁")
        return win

    def select_folder(self) -> str:
        """打开文件夹选择对话框，兼容新旧版pywebview API"""
        window = self._get_window()
        # 优先用新版枚举，旧版回退到常量，消除弃用警告
        try:
            dialog_type = webview.FileDialog.FOLDER
        except AttributeError:
            dialog_type = webview.FOLDER_DIALOG
        
        res = window.create_file_dialog(dialog_type)
        if res:
            self.target_folder_path = res[0]
            return self.target_folder_path
        return ""

    def get_selected_path(self) -> str:
        """获取已选中的文件夹路径"""
        return self.target_folder_path

    def close_current_window(self) -> None:
        """关闭当前所属窗口"""
        window = self._get_window()
        window.close()

    def close_target_window(self, target_win) -> None:
        """关闭指定窗口"""
        target_win.close()

    def open_main_window(self) -> None:
        main_api = PyApi()
        main_window = webview.create_window(
            "PrintO 主界面",
            url=f"http://127.0.0.1:{SERVER_PORT}/html/main.html", # 替换硬编码9090
            js_api=main_api,
            width=950,
            height=620,
            resizable=False,
        )
        # 新窗口与新API绑定，关系存入全局映射表
        bind_api_window(main_api, main_window)
    
    def create_new_window(self, window_name: str, html_url: str,resizable: bool):
        """
        通用创建新窗口方法
        :param window_name: 窗口左上角标题文字
        :param html_url: 页面地址，例如 http://127.0.0.1:9090/html/setting.html
        """
        # 1. 给新窗口创建独立的API实例，每个窗口单独一套api
        new_window_api = PyApi()

        # 2. 创建窗口对象，基础尺寸可以固定，需要改再扩展参数
        new_win = webview.create_window(
            window_name,
            url=html_url,
            js_api=new_window_api,
            width=900,
            height=600,
            resizable=resizable
        )

        # 3. 核心步骤：绑定api和窗口，存入全局弱引用映射表
        bind_api_window(new_window_api, new_win)

    def create_donate_window(self):
        # 1. 给新窗口创建独立的API实例，每个窗口单独一套api
        new_window_api = PyApi()

        # 2. 创建窗口对象，基础尺寸可以固定，需要改再扩展参数
        new_win = webview.create_window(
            '打赏',
            url='https://www.ifdian.net/a/Blair',
            js_api=new_window_api,
            width=900,
            height=600,
            resizable=True
        )
        # 3. 核心步骤：绑定api和窗口，存入全局弱引用映射表
        bind_api_window(new_window_api, new_win)


        

    # 新增：给JS调用，获取待打印文件列表
    def get_print_file_list(self):
        if not self.target_folder_path:
            return []
        return self.printer.get_printable_file_names(self.target_folder_path)

    # 新增：给JS调用，开始批量打印
    def start_batch_print(self):
        if not self.target_folder_path:
            return False
        self.batchPrinterRunningInfo=self.printer.batch_print(self.target_folder_path)
        return True

    def getBatchPrinterRunningInfo(self):
        if not self.batchPrinterRunningInfo:
            return False
        return self.batchPrinterRunningInfo
       
    def delete_temp_pdf_dir(self):
        if not self.target_folder_path:
            return "文件夹不存在"
        # ✅安全拼接路径，自动处理分隔符
        temp_dir = os.path.join(self.target_folder_path, "_temp_pdf_print")
        
        # 先判断文件夹是否存在
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)
            return "删除成功。"
        else:
            return "temp_pdf_dir 文件夹本身不存在，无需删除"
































# 单文件调试用
if __name__ == '__main__':
    import os
    import time
    import threading
    from http.server import HTTPServer, SimpleHTTPRequestHandler

    def test_server():
        web_root = os.path.dirname(os.path.abspath(__file__)) + "/../web"
        class TestHandler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=web_root, **kwargs)
        HTTPServer(("127.0.0.1", 9090), TestHandler).serve_forever()
    
    threading.Thread(target=test_server, daemon=True).start()
    time.sleep(0.3)

    test_api = PyApi()
    win = webview.create_window(
        "欢迎页测试",
        "http://127.0.0.1:9090/html/welcome.html",
        js_api=test_api,
        width=500,
        height=600
    )
    bind_api_window(test_api, win)

    webview.start(debug=True)
