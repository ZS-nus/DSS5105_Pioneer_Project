import pandas as pd
import os
import numpy as np
import spacy

# 加载 spaCy 的预训练 NER 模型
nlp = spacy.load("en_core_web_sm")

# 定义要处理的文件夹路径
input_dir = "../processed_files/apple2"  # 处理后的 CSV 文件夹路径
output_dir = "../processed_files/apple2/latest_year_data_with_ner"  # 输出文件夹路径
os.makedirs(output_dir, exist_ok=True)  # 创建输出文件夹如果不存在

# 获取所有 CSV 文件的路径
csv_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.csv')]

def extract_latest_year_data(df):
    """提取 DataFrame 中包含 2023、2023/24 或 2022 年的数据"""
    # 查找包含 2023 或 2023/24 的行，允许有其他字符
    latest_year_rows = df[df.apply(lambda row: row.astype(str).str.contains(r'\b2023/24\b|\b2023\b', regex=True).any(), axis=1)]
    if not latest_year_rows.empty:
        return latest_year_rows
    # 如果没有 2023 的数据，查找包含 2022 的行，允许有其他字符
    latest_year_rows = df[df.apply(lambda row: row.astype(str).str.contains(r'\b2022\b', regex=True).any(), axis=1)]
    if not latest_year_rows.empty:
        return latest_year_rows
    return None

def perform_ner_on_dataframe(df):
    """对 DataFrame 中的文本使用 NER 进行实体识别"""
    # 对每个单元格应用 NER
    ner_results = []
    for _, row in df.iterrows():
        row_entities = []
        for cell in row:
            if isinstance(cell, str) and cell.strip():
                doc = nlp(cell)
                entities = [(ent.text, ent.label_) for ent in doc.ents]
                row_entities.append(entities)
            else:
                row_entities.append([])
        ner_results.append(row_entities)
    return ner_results

# 处理每个 CSV 文件
for csv_file in csv_files:
    try:
        # 读取 CSV 文件
        df = pd.read_csv(csv_file)
        
        # 提取最新年份的数据
        latest_year_df = extract_latest_year_data(df)
        
        if latest_year_df is not None and not latest_year_df.empty:
            # 对提取的数据进行 NER
            ner_results = perform_ner_on_dataframe(latest_year_df)
            
            # 将 NER 结果添加到 DataFrame 中作为新列
            latest_year_df['NER_Results'] = ner_results
            
            # 构造输出文件名并保存处理后的文件
            output_filename = os.path.join(output_dir, f"latest_ner_{os.path.basename(csv_file)}")
            latest_year_df.to_csv(output_filename, index=False, encoding='utf-8-sig')
            print(f"Successfully saved latest year data with NER to: {output_filename}")
        else:
            print(f"No valid data found for the latest year in: {csv_file}")
    except Exception as e:
        print(f"Error processing file {csv_file}: {e}")
