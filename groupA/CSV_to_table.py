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
pdf_path = "../ESG_reports/Apple ESG 2024.pdf"
output_dir = "../labeled_files/apple_csv"  # 输出文件夹
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
            
            # 打印表格内容
            print(df)
            
            # 将表格保存到 CSV 文件
            csv_filename = os.path.join(output_dir, f"table_{i+1}.csv")
            df.to_csv(csv_filename, index=False, encoding='utf-8')  # 将 DataFrame 保存为 CSV 文件
            print(f"Table {i + 1} saved to {csv_filename}")
            
        except Exception as e:
            print(f"Error processing table {i + 1}: {e}")
    else:
        print(f"Table {i + 1} has no valid page reference.")

# 在所有表格处理完成后关闭文档
doc.close()
