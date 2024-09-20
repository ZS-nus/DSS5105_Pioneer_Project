import markdown
from bs4 import BeautifulSoup
import re

def markdown_to_text(markdown_string):
    """将Markdown字符串转换为纯文本"""
    # 将Markdown转换为HTML
    html = markdown.markdown(markdown_string)
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html, "html.parser")
    # 获取纯文本
    text = soup.get_text()
    # 去除多余的空白字符
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# 读取Markdown文件
with open('../ESG_reports/seres_car.md', 'r', encoding='utf-8') as file:
    markdown_content = file.read()

# 转换为纯文本
plain_text = markdown_to_text(markdown_content)

# 将纯文本保存为TXT文件
with open('../ESG_reports/seres_car.txt', 'w', encoding='utf-8') as text_file:
    text_file.write(plain_text)
