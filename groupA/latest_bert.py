import re
import pandas as pd
from transformers import pipeline, AutoModelForTokenClassification, AutoTokenizer
import torch
import hashlib
import json
import os

# 定义关键词和你要提取的信息类别
data_categories = {
    "EnergyConsumption": {"keywords": ["Energy Consumption", "MWh", "GJ"], "unit": "MWh"},
    "GHGEmissions": {"keywords": ["GHG Emissions", "CO2e", "Carbon Emissions"], "unit": "tonnes CO2e"},
    "WaterUsage": {"keywords": ["Water Usage", "million gallons"], "unit": "million gallons"},
    "WasteGenerated": {"keywords": ["Waste Generated", "tonnes"], "unit": "tonnes"},
    "RenewableEnergyUse": {"keywords": ["Renewable Energy Use", "MWh"], "unit": "MWh"},
    "EmployeeCount": {"keywords": ["Employee Count", "Employees", "Number of Employees"], "unit": "employees"}
}

# 初始化 NER 模型
def initialize_ner_model(device):
    print("Initializing NER model...")
    tokenizer = AutoTokenizer.from_pretrained("dbmdz/bert-large-cased-finetuned-conll03-english")
    model = AutoModelForTokenClassification.from_pretrained("dbmdz/bert-large-cased-finetuned-conll03-english").to(device)
    return pipeline("ner", model=model, tokenizer=tokenizer, device=0 if device != "cpu" else -1)

# 只提取表格数据
def extract_table_data(text):
    print("Extracting table data...")
    # 预过滤，只看相关部分
    relevant_sections = re.findall(r'(Table.*?(?=Table|\Z))', text, re.DOTALL | re.IGNORECASE)
    
    table_data = []
    for section in relevant_sections:
        rows = section.strip().split("\n")
        for row in rows:
            # 只处理可能包含数字的行
            if re.search(r'\d', row):  # 只处理包含数字的行
                columns = re.split(r'\s{2,}|\t|,', row)
                if len(columns) > 1:
                    table_data.append(columns)
    
    print(f"Found {len(table_data)} relevant table rows")
    return table_data

# NER 辅助提取信息
def extract_information_from_table(table_data, ner_pipeline):
    print("Extracting information from table data...")
    extracted_data = []
    batch_size = 32  # 批处理多行
    
    # 准备批处理文本
    row_texts = [" ".join(row) for row in table_data]
    
    # 批处理
    total_batches = (len(row_texts) + batch_size - 1) // batch_size
    for i in range(0, len(row_texts), batch_size):
        current_batch = (i // batch_size) + 1
        print(f"Processing batch {current_batch}/{total_batches}")
        
        batch = row_texts[i:i + batch_size]
        ner_results = ner_pipeline(batch)
        
        # 处理每个结果
        for row_idx, entities in enumerate(ner_results):
            row_text = row_texts[i + row_idx]
            for entity in entities:
                entity_text = entity['word']
                for category, details in data_categories.items():
                    for keyword in details["keywords"]:
                        if keyword.lower() in entity_text.lower():
                            year_match = re.search(r'\b(19|20)\d{2}\b', row_text)
                            value_match = re.search(r'([\d,]+\.?\d*)', entity_text)
                            
                            if year_match and value_match:
                                year = int(year_match.group(0))
                                value = float(value_match.group(0).replace(",", ""))
                                if "GJ" in keyword:
                                    value = value / 3.6
                                extracted_data.append({
                                    "Category": category,
                                    "Year": year,
                                    "Value": value,
                                    "Unit": details["unit"] if "GJ" not in keyword else "MWh"
                                })
    
    print(f"Extracted {len(extracted_data)} data points")
    return extracted_data

# 缓存函数
def get_cache_key(text):
    return hashlib.md5(text.encode()).hexdigest()

def load_from_cache(cache_key):
    cache_file = f"cache/{cache_key}.json"
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return json.load(f)
    return None

def save_to_cache(cache_key, data):
    os.makedirs("cache", exist_ok=True)
    cache_file = f"cache/{cache_key}.json"
    with open(cache_file, 'w') as f:
        json.dump(data, f)

# 主函数：执行信息提取
def main():
    print("Starting extraction process...")
    
    # 读入输入文件
    with open("../txt_files/apple.txt", "r", encoding="utf-8") as file:
        clean_text = file.read()
    
    # 尝试从缓存中加载
    cache_key = get_cache_key(clean_text)
    cached_data = load_from_cache(cache_key)
    
    if cached_data:
        print("Loading data from cache...")
        df = pd.DataFrame(cached_data)
    else:
        print("No cached data found, processing text...")
        
        # 检测可用设备
        if torch.cuda.is_available():
            device = torch.device("cuda")
            print("Using CUDA (GPU) for model inference.")
            print(f"GPU Model: {torch.cuda.get_device_name(0)}")
        elif torch.backends.mps.is_available():
            device = torch.device("mps")
            print("Using Apple GPU (MPS) for model inference.")
        else:
            device = torch.device("cpu")
            print("Using CPU for model inference.")

        # 初始化模型一次
        ner_pipeline = initialize_ner_model(device)
        
        # 提取和处理数据
        table_data = extract_table_data(clean_text)
        extracted_data = extract_information_from_table(table_data, ner_pipeline)
        
        # 保存结果到缓存
        print("Saving results to cache...")
        save_to_cache(cache_key, extracted_data)
        
        # 创建 DataFrame
        df = pd.DataFrame(extracted_data)

    # 输出结果
    print("\nExtracted Data Summary:")
    print(df)

    # 保存到 CSV
    output_file = "extracted_data.csv"
    df.to_csv(output_file, index=False)
    print(f"\nData saved to {output_file}")

if __name__ == "__main__":
    main()
