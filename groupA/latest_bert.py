import re
import pandas as pd
from transformers import pipeline, AutoModelForTokenClassification, AutoTokenizer
import torch

# 定义关键词和你要提取的信息类别
data_categories = {
    "EnergyConsumption": {"keywords": ["Energy Consumption", "MWh", "GJ"], "unit": "MWh"},
    "GHGEmissions": {"keywords": ["GHG Emissions", "CO2e", "Carbon Emissions"], "unit": "tonnes CO2e"},
    "WaterUsage": {"keywords": ["Water Usage", "million gallons"], "unit": "million gallons"},
    "WasteGenerated": {"keywords": ["Waste Generated", "tonnes"], "unit": "tonnes"},
    "RenewableEnergyUse": {"keywords": ["Renewable Energy Use", "MWh"], "unit": "MWh"},
    "EmployeeCount": {"keywords": ["Employee Count", "Employees", "Number of Employees"], "unit": "employees"}
}

# 使用NER模型进行提取，添加设备支持（CUDA 和 Apple GPU）
def run_ner_model(text, device):
    tokenizer = AutoTokenizer.from_pretrained("dbmdz/bert-large-cased-finetuned-conll03-english")
    model = AutoModelForTokenClassification.from_pretrained("dbmdz/bert-large-cased-finetuned-conll03-english").to(device)
    ner = pipeline("ner", model=model, tokenizer=tokenizer, device=0 if device != "cpu" else -1)
    results = ner(text)
    return results

# 只提取表格数据
def extract_table_data(text):
    # 使用正则表达式来定位表格部分，例如表格前后的标识符或者关键词
    table_pattern = r"Table .*?\n((?:.*?\n)+?)\n\n"  # 假设表格被标识为"Table ..."并有换行符
    matches = re.findall(table_pattern, text, re.IGNORECASE | re.DOTALL)
    
    table_data = []
    for match in matches:
        rows = match.strip().split("\n")
        for row in rows:
            # 进一步清理每行，例如按多个空格或逗号拆分
            columns = re.split(r'\s{2,}|\t|,', row)
            if len(columns) > 1:  # 确保是有意义的表格数据
                table_data.append(columns)
    
    return table_data

# NER辅助提取信息
def extract_information_from_table(table_data, device):
    extracted_data = []

    for row in table_data:
        row_text = " ".join(row)
        ner_results = run_ner_model(row_text, device)
        
        # 检查每个单元格是否包含有效实体
        for entity in ner_results:
            entity_text = entity['word']
            for category, details in data_categories.items():
                for keyword in details["keywords"]:
                    if keyword.lower() in entity_text.lower():
                        # 尝试提取数值和年份
                        year_match = re.search(r'\b(19|20)\d{2}\b', row_text)
                        value_match = re.search(r'([\d,]+\.?\d*)', entity_text)
                        
                        if year_match and value_match:
                            year = int(year_match.group(0))
                            value = float(value_match.group(0).replace(",", ""))
                            if "GJ" in keyword:
                                value = value / 3.6  # 如果是GJ，转换为MWh
                            extracted_data.append({
                                "Category": category,
                                "Year": year,
                                "Value": value,
                                "Unit": details["unit"] if "GJ" not in keyword else "MWh"
                            })
    
    return extracted_data

# 主函数：执行信息提取
def main():
    # 假设你已经将PDF转换为txt，并将清理好的文本存储为字符串 clean_text
    with open("../txt_files/apple.txt", "r", encoding="utf-8") as file:
        clean_text = file.read()

    # 自动检测可用设备（CUDA 或 MPS 或 CPU）
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print("Using CUDA (GPU) for model inference.")
        # 打印 GPU 相关信息
        print(f"GPU Model: {torch.cuda.get_device_name(0)}")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
        print("Using Apple GPU (MPS) for model inference.")
        # 打印 Apple GPU 相关信息
        print("Apple GPU (MPS) is being used for model inference.")
    else:
        device = torch.device("cpu")
        print("Using CPU for model inference.")

    # 只提取表格数据
    table_data = extract_table_data(clean_text)

    # 使用NER模型辅助提取表格中的关键信息
    extracted_data = extract_information_from_table(table_data, device)

    # 创建DataFrame保存结构化的数据
    df = pd.DataFrame(extracted_data)

    # 输出提取到的数据信息
    print(df)

    # 保存为csv文件
    df.to_csv("extracted_data.csv", index=False)
    print("提取的数据已保存为 extracted_data.csv")

if __name__ == "__main__":
    main()
