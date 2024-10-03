import pandas as pd
import re
import os

def read_csv(file_path):
    """读取CSV文件"""
    return pd.read_csv(file_path)

def preprocess_data(df):
    """对数据进行预处理"""
    # 去除逗号，转换为浮点数，并处理无效值
    for col in df.columns[2:]:
        df.loc[:, col] = df[col].apply(lambda x: float(str(x).replace(',', '')) if str(x).replace(',', '').replace('.', '').isdigit() else None)

    return df

def label_data(df):
    """将数据标签化"""
    labeled_data = []
    for _, row in df.iterrows():
        labeled_text = f"Company {row['CompanyID']} in {row['ReportYear']} had energy consumption of {row.get('EnergyConsumption(MWh)', 'N/A')} MWh, GHG emissions of {row.get('GHG Emissions(tonne (Mt) of CO2e)', 'N/A')} tonnes, water usage of {row.get('WaterUsage(tonne (Mt))', 'N/A')} tonnes, waste generated of {row.get('WasteGenerated (tonne)', 'N/A')} tonnes, and renewable energy use of {row.get('RenewableEnergyUse (MWh)', 'N/A')} MWh."
        labeled_data.append(labeled_text)
    return labeled_data

def save_labeled_data(labeled_data, output_file):
    """保存标签化的数据到文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in labeled_data:
            f.write(line + '\n')
    print(f"Labeled data successfully saved to {output_file}")

if __name__ == "__main__":
    # 输入的CSV文件路径
    input_file_path = os.path.abspath('../../data_temp/Pioneer DS project - Environment.csv')
    output_file_path = os.path.abspath('../../data_temp/Pioneer_DS_project_new_Environment2.csv')

    # 读取CSV文件
    df = read_csv(input_file_path)

    # 预处理数据
    df = preprocess_data(df)

    # 标签化数据
    labeled_data = label_data(df)

    # 保存标签化的数据到文件
    save_labeled_data(labeled_data, output_file_path)