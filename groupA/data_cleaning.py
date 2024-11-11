import pandas as pd
import os
import numpy as np

# 定义要处理的文件夹路径
input_dir = "../labeled_files/apple2"  # CSV 文件夹路径
output_dir = "../processed_files/apple2"  # 处理后的文件保存路径
os.makedirs(output_dir, exist_ok=True)  # 创建输出文件夹如果不存在

# 获取所有 CSV 文件的路径
csv_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.csv')]

def preprocess_dataframe(df):
    """对 DataFrame 进行预处理，使数据更加整洁"""
    # 1. 去除单元格中的换行符和多余空格
    df = df.apply(lambda x: x.replace('\n', '').strip() if isinstance(x, str) else x)
    
    # 2. 删除完全空的行和列
    df.dropna(how='all', inplace=True)  # 删除完全空的行
    df.dropna(axis=1, how='all', inplace=True)  # 删除完全空的列

    # 3. 标准化列名（去掉空格并转换为小写）
    df.columns = df.columns.str.strip().str.lower()

    # 4. 清洗数值数据（去掉逗号并转换为数值）
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].str.replace(',', '', regex=True).str.strip()
            try:
                df[col] = pd.to_numeric(df[col])
            except ValueError:
                pass

    # 5. 替换空值为 NaN
    df.replace(['', 'N/A', 'n/a'], np.nan, inplace=True)

    # 6. 删除重复的行
    df.drop_duplicates(inplace=True)
    
    return df

# 处理每个 CSV 文件
for csv_file in csv_files:
    try:
        # 读取 CSV 文件
        df = pd.read_csv(csv_file)
        
        # 预处理 DataFrame
        df = preprocess_dataframe(df)
        
        # 构造输出文件名并保存处理后的文件
        output_filename = os.path.join(output_dir, os.path.basename(csv_file))
        df.to_csv(output_filename, index=False, encoding='utf-8-sig')
        
        print(f"Successfully processed and saved: {output_filename}")
    except Exception as e:
        print(f"Error processing file {csv_file}: {e}")
