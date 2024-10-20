import pandas as pd
from gmft.auto import CroppedTable, AutoTableDetector, AutoTableFormatter
from gmft.pdf_bindings import PyPDFium2Document
import os

# 初始化表格检测器和格式化工具
detector = AutoTableDetector()
formatter = AutoTableFormatter()

def ingest_pdf(pdf_path):
    """ 从 PDF 文件中提取表格并返回表格列表 """
    doc = PyPDFium2Document(pdf_path)  # 打开 PDF 文档
    tables = []
    pages = []  # 保持对页面对象的引用

    for page in doc:  # 遍历每一页
        pages.append(page)  # 保持对页面对象的引用
        detected_tables = detector.extract(page)
        if detected_tables:
            tables.extend(detected_tables)
    
    return tables, doc, pages  # 返回页的引用

# 提取表格
pdf_path = "../ESG_reports/tesla.pdf"
output_dir = "../labeled_files/tesla_txt"  # 输出文件夹
os.makedirs(output_dir, exist_ok=True)  # 创建输出文件夹（如果不存在）

tables, doc, pages = ingest_pdf(pdf_path)

# 处理每个表格
for i, table in enumerate(tables):
    print(f"\n--- Table {i + 1} ---")
    
    # 确保 CroppedTable 有有效的 page 引用
    if hasattr(table, 'page') and table.page is not None:
        try:
            formatted_table = formatter.format(table)  # 将 CroppedTable 转换为 FormattedTable
            df = formatted_table.df()  # 导出为 Pandas DataFrame
            
            # 将空值替换为 'N/A'，增强表格的可读性
            df.fillna('N/A', inplace=True)

            # 构建分隔线和标题
            title = f"Table {i + 1}"
            separator = "=" * 80

            # 构建表格文本内容
            table_text = f"{separator}\n{title}\n{separator}\n"
            table_text += df.to_string(index=False, col_space=10)  # 调整列宽，增强可读性
            table_text += f"\n{separator}\n"

            # 将表格保存到 TXT 文件
            txt_filename = os.path.join(output_dir, f"table_{i+1}.txt")
            with open(txt_filename, 'w', encoding='utf-8') as f:
                f.write(table_text)
            
            print(f"Table {i + 1} saved to {txt_filename}")
            
        except Exception as e:
            print(f"Error processing table {i + 1}: {e}")
    else:
        print(f"Table {i + 1} has no valid page reference.")

# 在所有表格处理完成后关闭文档
doc.close()
