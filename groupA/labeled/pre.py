import pandas as pd
import os

def read_csv(file_path):
    """读取CSV文件"""
    return pd.read_csv(file_path)

def preprocess_data(df):
    """对数据进行预处理"""
    # 清洗与数据格式化
    for col in df.columns[2:]:
        df.loc[:, col] = df[col].apply(lambda x: float(str(x).replace(',', '')) if pd.notnull(x) and str(x).replace(',', '').replace('.', '').isdigit() else None)
    return df

def label_data(df):
    """根据实际数据列生成标签"""
    labeled_data = []
    for _, row in df.iterrows():
        # 数据存在的列，生成标签
        company_id = int(row['CompanyID']) if pd.notnull(row['CompanyID']) else 'N/A'
        report_year = int(row['ReportYear']) if pd.notnull(row['ReportYear']) else 'N/A'
        employee_count = row.get('EmployeeCount', 'N/A')
        male_percentage = row.get('Male( %)', 'N/A')
        female_percentage = row.get('Female(', 'N/A')
        
        # 创建标签文本
        labeled_text = (f"Company {company_id} in {report_year} had {employee_count} employees, "
                        f"with {male_percentage}% male and {female_percentage}% female.")
        
        labeled_data.append(labeled_text)
    return labeled_data

def save_labeled_data(labeled_data, output_file):
    """保存标签化的数据到文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in labeled_data:
            f.write(line + '\n')
    print(f"Labeled data successfully saved to {output_file}")

if __name__ == "__main__":
    input_file_path = os.path.abspath('../../data_temp/Pioneer DS project - Social.csv')
    output_file_path = os.path.abspath('../../data_temp/Pioneer_DS_project_new_Social.csv')

    df = read_csv(input_file_path)
    df = preprocess_data(df)
    labeled_data = label_data(df)
    save_labeled_data(labeled_data, output_file_path)
