# flomo-to-markdown
Flomo to Markdown Converter

将 Flomo 笔记导出为 Markdown (`.md`) 文件，可以直接放入 Obsidian 仓库中。

## 功能说明

1. **笔记标题**：Flomo 没有标题概念，默认取笔记第一行作为 Markdown 文件名。
2. **标签处理**：Flomo 默认将标签放在笔记最前面，为避免影响文件名，脚本会把标签挪到文档的最后一行。
3. **特殊字符处理**：
    - 文件名中的特殊字符会被删除，以避免创建文件失败。
    - 不影响文档内容，但如果你经常使用特殊字符（如 `3/11 - 3/20` 作为笔记首行），文件名可能会有些奇怪。
4. **笔记中的内部引用链接无法转换**。
5. **稳定性**：
    - 该脚本仅作简单转换，若遇到较多错误，请考虑其他方法。

## 使用说明

1. 在 Flomo 网页版，进入 **账号详情 → 数据同步 → 导出所有数据（as HTML）**。
2. 下载后解压缩，找到 `.html` 文件，并将其 **重命名为 index.html**。
3. 将 `html_to_md.py` 放到相同目录下。
4. 打开终端（Terminal），运行以下命令：
    ```
    python html_to_md.py
    ```
5. 处理完成后，所有 `.md` 笔记将存放在 `memos` 文件夹内。
