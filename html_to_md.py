import os
import re
from bs4 import BeautifulSoup
from datetime import datetime

def html_to_md(html_file="index.html", output_dir="memos"):
    """
    將包含多個 memo 的 HTML 檔案轉換為多個 Markdown 檔案。

    Args:
        html_file (str, optional): 包含 memo 的 HTML 檔案路徑。默認為 "index.html"。
        output_dir (str, optional): 保存生成的 Markdown 檔案的目錄。默認為 "memos"。

    功能：
    1. 讀取指定的 HTML 檔案。
    2. 使用 BeautifulSoup 解析 HTML 內容。
    3. 提取每個 memo 的時間和內容。
    4. 將 HTML 格式的內容轉換為 Markdown 格式。
    5. 將 memo 中的 tag 標籤移動到檔案末尾。
    6. 處理檔名，移除特殊字元，並限制長度。
    7. 建立輸出目錄（如果不存在）。
    8. 將每個 memo 保存為單獨的 Markdown 檔案，檔名包含時間資訊，並處理重複檔名。
    9. 記錄成功和失敗的轉換，並打印相關資訊。
    """

    # 確保輸出目錄存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    success_count = 0
    fail_count = 0

    try:
        with open(html_file, "r", encoding="utf-8") as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"\033[33m警告:\033[0m 找不到檔案: {html_file}")
        return

    soup = BeautifulSoup(html_content, "html.parser")
    memos = soup.find_all("div", class_="memo")

    for memo in memos:
        time_str = memo.find("div", class_="time").text.strip()
        content_html = memo.find("div", class_="content")

        try:
            # 將 HTML 轉換為 Markdown，保留換行符
            content_md = html_to_markdown(str(content_html))
            # 提取和移動 tags，必須在生成檔名之前處理
            content_md, tags = extract_tags(content_md)

            # 移除 content_md 前後的空白行
            content_md = content_md.strip()

            # 構造檔名，並進行清理
            filename_base = content_md.splitlines()[0]  # 使用第一行作為檔名
            filename_base = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5\s]', '', filename_base)  # 移除特殊字元
            filename_base = filename_base.strip() #移除首尾空白
            filename_base = filename_base[:20]  # 限制檔名長度
            if not filename_base:  # 如果檔名為空，則使用預設檔名
                filename_base = "untitled"
            timestamp = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S") #將時間字串轉換為 datetime 物件
            # timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")  # 移除這一行
            filename = f"{filename_base}.md" # 檔名中不再包含時間字串
            filepath = os.path.join(output_dir, filename)

            # 處理重複檔名
            counter = 1
            while os.path.exists(filepath):
                filename = f"{filename_base}_{counter}.md" # 重複的檔名加上計數器
                filepath = os.path.join(output_dir, filename)
                counter += 1

            # 將 tags 新增到 Markdown 內容的末尾
            if tags:
                content_md += "\n\n" + " ".join(tags)

            # 寫入 Markdown 檔案
            with open(filepath, "w", encoding="utf-8") as md_file:
                md_file.write(content_md)
            # 修改檔案建立時間
            os.utime(filepath, (timestamp.timestamp(), timestamp.timestamp())) # 使用 os.utime 修改檔案時間

            success_count += 1
        except Exception as e:
            fail_count += 1
            print(f"\033[31m錯誤:\033[0m 處理 memo 時發生錯誤: {e}")
            print(f"  時間: {time_str}")
            print(f"  內容: {content_html}")  # 打印 memo 的完整 HTML 內容，方便除錯

    print("-" * 30)
    print(f"成功轉換: {success_count} 個 memo")
    print(f"轉換失敗: {fail_count} 個 memo")

def html_to_markdown(html):
    """
    將 HTML 轉換為 Markdown，處理換行、段落、粗體、斜體、列表和高亮。

    Args:
        html (str): 要轉換的 HTML 字串。

    Returns:
        str: 轉換後的 Markdown 字串。
    """
    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(html, 'html.parser')

    #   定義一個遞迴函式，用於處理 HTML 元素的轉換
    def process_element(element):
        """
        遞迴處理 HTML 元素，並將其轉換為 Markdown 格式。

        Args:
            element (bs4.element.Tag): 要處理的 HTML 元素。

        Returns:
            str: 轉換後的 Markdown 文字。
        """
        markdown_text = ""

        if element.name == 'p':
            # 段落：轉換為 Markdown 段落，新增換行符
            for child in element.contents:
                markdown_text += process_element(child)
            markdown_text += "\n\n"  # 段落之間新增兩個換行符
        elif element.name == 'br':
            # 換行：轉換為 Markdown 換行符
            markdown_text += "\n"
        elif element.name == 'strong' or element.name == 'b':
            # 粗體：轉換為 Markdown 粗體
            markdown_text += "**"
            for child in element.contents:
                markdown_text += process_element(child)
            markdown_text += "**"
        elif element.name == 'em' or element.name == 'i':
            # 斜體：轉換為 Markdown 斜體
            markdown_text += "*"
            for child in element.contents:
                markdown_text += process_element(child)
            markdown_text += "*"
        elif element.name == 'mark':
            # 高亮：轉換為 Markdown 高亮 (如果支援)
            markdown_text += "=="
            for child in element.contents:
                markdown_text += process_element(child)
            markdown_text += "=="
        elif element.name == 'ul':
            # 無序列表：轉換為 Markdown 無序列表
            for child in element.find_all('li', recursive=False):  # 只處理直接子節點
                markdown_text += "- " + process_element(child).strip() + "\n"
        elif element.name == 'ol':
            # 有序列表：轉換為 Markdown 有序列表
            for i, child in enumerate(element.find_all('li', recursive=False), 1): # 只處理直接子節點
                markdown_text += f"{i}. " + process_element(child).strip() + "\n"
        elif element.name == 'li':
             # 列表項，只獲取子節點內容
            for child in element.contents:
                markdown_text += process_element(child)
        elif isinstance(element, str):
            # 文字節點：直接新增到 Markdown 文字中
            markdown_text += element.replace("\xa0", " ") # 將 nbsp 替換為空格
        else:
            # 其他元素：遞迴處理其子節點
            for child in element.contents:
                markdown_text += process_element(child)

        return markdown_text

    # 處理整個 soup 物件
    return process_element(soup)

def extract_tags(md_content):
    """
    從 Markdown 內容中提取 tag 標籤，並將它們移動到內容的末尾。

    Args:
        md_content (str): 包含 tag 標籤的 Markdown 內容。

    Returns:
        tuple: (處理後的 Markdown 內容, tag 標籤列表)
    """
    tags = re.findall(r'(#[^\s#]+)\s', md_content)  # 查找以 # 開頭，以空格結尾的tag
    cleaned_content = re.sub(r'(#[^\s#]+)\s', '', md_content)  # 移除 tag 標籤，不移除內容中的#
    return cleaned_content, tags

if __name__ == "__main__":
    html_to_md()
