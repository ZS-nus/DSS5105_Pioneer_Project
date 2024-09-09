import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import os

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        text += pytesseract.image_to_string(image)
    return text

# 使用函数提取文本
pdf_path = "../ESG_reports/Apple_ESG_2024.pdf"
text = extract_text_from_pdf(pdf_path)

def save_as_markdown(text, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text)

output_md = "output.md"
save_as_markdown(text, output_md)

