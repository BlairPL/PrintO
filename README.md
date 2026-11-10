# PrintO

PrintO 是一个批量打印工具，旨在简化多文件打印流程。项目以 Windows 桌面程序形式发布，依赖 LibreOffice 完成相关文档处理与打印支持。

> 当前仓库发布方式为便携式目录：将 `dist` 目录中的文件复制到任意你希望存放程序的文件夹，即可使用。

## 功能简介

- 批量选择文件并进行打印
- 简化多文件打印操作流程
- 便携式部署，无需传统安装程序
- 随项目提供 LibreOffice 安装包，便于快速配置运行环境

> 具体支持的文件格式与打印能力以实际版本和 LibreOffice 支持范围为准。

## 环境要求

- Windows10 及以上操作系统(只测过win10,其他的windows操作请自行尝试)
- LibreOffice 26.2
- 足够的磁盘空间用于存放程序和待打印文件

## 安装与启动

### 1. 获取项目文件

从 GitHub Releases 下载发行包，或克隆本仓库：

```bash
git clone https://github.com/BlairPL/PrintO/PrintO.git
```

### 2. 复制程序文件

将 `dist` 目录下的所有文件复制到任意你希望存放 PrintO 的文件夹中。

> 注意：请复制 `dist` 目录中的完整内容，不要只复制 `PrintO.exe`，以免缺少运行所需文件。

### 3. 安装 LibreOffice

双击 `LibreOffice 26.2.msi`，按照安装向导完成 LibreOffice 安装。

### 4. 启动 PrintO

进入 `PrintO` 子目录，双击 `PrintO.exe` 即可启动程序。

```text
你的存放目录\PrintO\PrintO.exe
```

## 使用说明

1. 启动`LibreOffice 26.2`和 `PrintO.exe`。
2. 创建一个文件夹，将你想要打印的文件放进去。
3. 根据界面提示选择你所创建的文件夹。
4. 执行批量打印。
5. 打印前建议先使用少量文件测试，确认打印机、纸张和排版设置正确。

## 常见问题

### 双击 PrintO.exe 无法启动？

请检查：

- 是否已安装 LibreOffice 26.2；
- 是否完整复制了 `dist` 目录中的所有文件；
- 程序存放路径是否包含异常字符；
- 是否被安全软件拦截。

### 打印失败或格式异常？

请确认：

- LibreOffice 已正确安装并可正常打开相关文档；
- 打印机驱动和默认打印机设置正常；
- 待打印文件本身可以正常打开和打印；
- 打印前已进行预览或小批量测试。

### 是否需要单独安装 LibreOffice？

需要。请先安装 `dist` 目录中提供的 `LibreOffice 26.2.msi`，或安装兼容版本的 LibreOffice。

## 贡献

欢迎提交 Issue 和 Pull Request。

- 提交问题前，请先搜索是否已有类似 Issue；
- 提交 PR 时，请说明修改内容和测试情况；
- 请尽量保持代码风格一致，并确保不提交无关文件。

## 许可证

本项目采用 MIT License 开源，详情请参阅 [LICENSE](LICENSE)。

## 致谢

- 感谢 [LibreOffice](https://www.libreoffice.org/) 提供文档处理与打印相关能力。
- 感谢所有为本项目提供建议和贡献的开发者。

