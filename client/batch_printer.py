import subprocess
from pathlib import Path
from utils import get_resource_path

# ========== 配置常量（要改参数直接改这里就行） ==========
# 支持打印的办公文档后缀
SUPPORTED_DOC_EXTENSIONS = {".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", ".pdf"}
# 支持打印的图片后缀
SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".gif"}
# 合并所有支持打印的文件后缀
ALL_SUPPORTED_EXTENSIONS = set()
ALL_SUPPORTED_EXTENSIONS.update(SUPPORTED_DOC_EXTENSIONS)
ALL_SUPPORTED_EXTENSIONS.update(SUPPORTED_IMAGE_EXTENSIONS)

# LibreOffice 默认安装路径
DEFAULT_LIBREOFFICE_PATH = r"C:\Program Files\LibreOffice\program\soffice.exe"
#DEFAULT_LIBREOFFICE_PATH = get_resource_path("./LibreOffice/program/soffice.exe") 

# 临时存放转换后PDF的文件夹名称
TEMP_PDF_FOLDER_NAME = "_temp_pdf_print"
# ======================================================


class BatchPrinter:
    """批量打印工具：支持办公文档、图片的批量打印，基于LibreOffice实现"""

    def __init__(self, libre_office_path=None):
        """
        初始化打印工具
        :param libre_office_path: 可选，LibreOffice的soffice.exe完整路径
                                   不填的话自动用上面的默认路径
        """
        # 保存LibreOffice程序路径
        if libre_office_path is not None:
            self.libre_office_path = libre_office_path
        else:
            self.libre_office_path = DEFAULT_LIBREOFFICE_PATH
        
        # 临时PDF文件夹的名称
        self.temp_pdf_folder_name = TEMP_PDF_FOLDER_NAME

        #运行信息
        self.runningInfo = """"""

    # -------------------- 内部工具方法（仅类内部自己用，不用管） --------------------
    def _convert_to_pdf(self, src_file, out_dir):
        """
        内部方法：把源文件转换成PDF格式
        :param src_file: 要转换的源文件
        :param out_dir: 转换后PDF存放的文件夹
        :return: 生成的PDF文件
        """
        # 拼接转换用的命令
        cmd = [
            self.libre_office_path,
            "--headless",
            "--convert-to", "pdf",
            "--outdir", str(out_dir),
            str(src_file)
        ]
        # 执行转换命令，不弹出黑窗口
        # subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,stdin=subprocess.DEVNULL)
        subprocess.run(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # 拼接生成的PDF的完整路径
        pdf_name = src_file.stem + ".pdf"
        return out_dir.joinpath(pdf_name)

    def _send_print_task(self, pdf_path):
        """
        内部方法：把PDF提交给打印机
        :param pdf_path: 要打印的PDF文件
        :return: 提交成功返回True，失败返回False
        """
        try:
            cmd = [
                self.libre_office_path,
                "--headless",
                "-p",
                str(pdf_path)
            ]
            # result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,stdin=subprocess.DEVNULL)
            # 发送打印任务的调用
            result = subprocess.run(
                cmd,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # 命令返回码为0代表执行成功
            return result.returncode == 0
        except Exception:
            return False

    def _get_all_printable_files(self, folder_path):
        """
        内部方法：找出文件夹里所有能打印的文件
        :param folder_path: 目标文件夹
        :return: 可打印文件的列表
        """
        file_list = []
        # 遍历文件夹里的所有内容
        all_items = folder_path.iterdir()
        for item in all_items:
            # 只处理文件，跳过子文件夹
            if item.is_file():
                # 获取文件后缀，转成小写，避免大小写导致识别失败
                file_suffix = item.suffix.lower()
                # 判断后缀在支持的列表里，就加入结果
                if file_suffix in ALL_SUPPORTED_EXTENSIONS:
                    file_list.append(item)
        return file_list

    # -------------------- 对外可用方法（你可以直接调用的功能） --------------------
    def get_printable_file_names(self, folder_input):
        """
        获取指定文件夹里，所有待打印文件的文件名列表
        :param folder_input: 目标文件夹的路径字符串
        :return: 文件名组成的列表（对应JS的字符串数组），文件夹不存在返回空列表
        """
        # 把输入的字符串转成路径对象，并获取绝对路径
        root_dir = Path(folder_input).resolve()
        file_name_list = []

        # 先检查文件夹是否存在
        if not root_dir.is_dir():
            return file_name_list

        # 拿到所有可打印的文件
        printable_files = self._get_all_printable_files(root_dir)
        # 把文件名逐个加到结果列表里
        for file in printable_files:
            file_name_list.append(file.name)
        
        return file_name_list

    def batch_print(self, folder_input):
        """
        执行批量打印任务
        :param folder_input: 存放待打印文件的文件夹路径
        """
        # 1. 检查目标文件夹是否存在
        root_dir = Path(folder_input).resolve()
        if not root_dir.is_dir():
            print("❌ 错误：文件夹不存在 -> " + str(root_dir))
            return

        # 2. 检查LibreOffice程序是否存在
        lo_path = Path(self.libre_office_path)
        if not lo_path.exists():
            print("❌ 错误：未找到LibreOffice，请检查路径：" + self.libre_office_path)
            return

        # 3. 创建临时存放PDF的文件夹（已存在也不报错）
        temp_pdf_dir = root_dir.joinpath(self.temp_pdf_folder_name)
        temp_pdf_dir.mkdir(exist_ok=True)

        # 4. 筛选所有可打印的文件
        all_files = self._get_all_printable_files(root_dir)
        total_count = len(all_files)
        success_count = 0
        fail_list = []

        print("===== 开始处理，共扫描到 " + str(total_count) + " 个待打印文件 =====\n")

        # 5. 逐个处理每个文件
        for file in all_files:
            suffix = file.suffix.lower()
            # 判断文件类型
            if suffix in SUPPORTED_IMAGE_EXTENSIONS:
                file_type = "图片"
            else:
                file_type = "文档"
            
            print("正在处理【" + file_type + "】：" + file.name)
            try:
                # PDF文件不用转换，直接用原文件
                if suffix == ".pdf":
                    target_pdf = file
                # 其他格式先转成PDF再打印
                else:
                    target_pdf = self._convert_to_pdf(file, temp_pdf_dir)

                # 检查PDF有没有成功生成
                if not target_pdf.exists():
                    raise Exception("PDF转换失败，未生成文件")

                # 提交打印任务
                send_ok = self._send_print_task(target_pdf)
                if send_ok:
                    success_count = success_count + 1
                    print("✅ " + file.name + " 打印任务已发送至打印机\n")
                else:
                    raise Exception("LibreOffice推送打印任务返回异常")

            except Exception as e:
                # 记录失败的文件和错误原因
                fail_list.append((file.name, str(e)))
                print("❌ " + file.name + " 任务发送失败：" + str(e) + "\n")

        # 6. 打印最终统计报告
        report_lines=[]
        report_lines.append("============== 任务下发完成报告 =============")
        report_lines.append("目标文件夹：" + str(root_dir))
        # report_lines.append("临时PDF存放位置：" + str(temp_pdf_dir))
        report_lines.append("文件总数：" + str(total_count))
        report_lines.append("成功发送打印任务：" + str(success_count))
        report_lines.append("发送失败数量：" + str(len(fail_list)))

        if len(fail_list) > 0:
            report_lines.append("\n【下发失败文件清单】")
            for name, err in fail_list:
                report_lines.append("- " + name + " 原因：" + err)
        else:
            report_lines.append("\n🎉 所有文件打印任务全部成功下发！")
        report_lines.append("========================================")
        report_lines.append("提示：任务已全部送入打印机队列，实际打印由打印机自行处理。")

        self.runningInfo="\n".join(report_lines)
        return self.runningInfo
