import markdown
import re
from bs4 import BeautifulSoup
from transformers import BertTokenizer, BertForSequenceClassification
import torch

# 加载预训练的BERT模型和分词器
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)  # 二分类任务

# ESG标签映射
label_map = {
    'environment': ['energy consumption', 'GHG', 'water consumption', 'waste generation'],
    'social': ['data security', 'customer privacy', 'diversity and inclusion', 'occupational health and safety', 'labour practices'],
    'governance': ['ethical behaviour', 'certifications', 'board diversity', 'risk management policies']
}

# 分值体系映射 (根据提供的图表进行映射)
score_map = {
    'energy consumption': {'type': 'binary', 'weight': 0.08},   # 二元分类
    'GHG': {'type': 'binary', 'weight': 0.04},                  # 二元分类
    'water consumption': {'type': 'binary', 'weight': 0.04},    # 二元分类
    'waste generation': {'type': 'binary', 'weight': 0.04},     # 二元分类
    
    'data security': {'type': 'binary', 'weight': 0.3},         # 二元分类
    'customer privacy': {'type': 'score', 'weight': 0.15},      # 评分制 (0-10)
    'diversity and inclusion': {'type': 'binary', 'weight': 0.05}, # 二元分类
    'occupational health and safety': {'type': 'score', 'weight': 0.05}, # 评分制 (0-10)
    'labour practices': {'type': 'score', 'weight': 0.05},      # 评分制 (0-10)
    
    'ethical behaviour': {'type': 'binary', 'weight': 0.04},    # 二元分类
    'certifications': {'type': 'score', 'weight': 0.04},        # 评分制 (1-10)
    'board diversity': {'type': 'binary', 'weight': 0.04},      # 二元分类
    'risk management policies': {'type': 'binary', 'weight': 0.08}, # 二元分类
}


def markdown_to_text(markdown_string):
    """Convert a markdown string to plaintext"""
    html = markdown.markdown(markdown_string)
    soup = BeautifulSoup(html, features="html.parser")
    text = soup.get_text()
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def read_markdown_file(file_path):
    """Read a Markdown file and return its content"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def process_markdown_file(file_path):
    """Process a single Markdown file"""
    markdown_content = read_markdown_file(file_path)
    plain_text = markdown_to_text(markdown_content)
    return plain_text


def save_text_to_file(text, output_file):
    """Save the processed text to a file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text)

import os

def process_and_classify_esg(file_path):
    """Process the markdown file, convert it to text, and classify ESG terms using BERT"""
    plain_text = process_markdown_file(file_path)

    # 检查当前工作目录
    print(f"Current working directory: {os.getcwd()}")

    # 保存生成的纯文本到文件
    output_file = 'processed_text.txt'
    save_text_to_file(plain_text, output_file)
    print(f"Processed text has been saved to {output_file}")

    results = {}
    for category, labels in label_map.items():
        results[category] = {}
        for label in labels:
            if label in score_map:  # 检查是否存在映射
                label_type = score_map[label]['type']
                results[category][label] = classify_esg(plain_text, label_type)
            else:
                print(f"Warning: No score map found for {label}")
                results[category][label] = 'No score available'

    for category, labels in results.items():
        print(f"{category.capitalize()}:")
        for label, score in labels.items():
            print(f"  {label}: {score}")

    return results



def classify_esg(text, label_type):
    """Classify text into ESG categories using BERT"""
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)

    with torch.no_grad():
        outputs = model(**inputs)
    
    logits = outputs.logits

    if label_type == 'binary':
        # 二元分类: 返回两个logits值 (对应于0和1)
        predicted_label = torch.argmax(logits, dim=1).item()
        return predicted_label  # 返回0或1，表示是否符合类别
    elif label_type == 'score':
        # 评分制: 将logits的第一个维度取sigmoid并映射为0到10的评分
        score = torch.sigmoid(logits).mean().item() * 10  # 取平均值并映射到0-10分制
        return score


def process_and_classify_esg(file_path):
    """Process the markdown file, convert it to text, and classify ESG terms using BERT"""
    plain_text = process_markdown_file(file_path)

    results = {}
    for category, labels in label_map.items():
        results[category] = {}
        for label in labels:
            if label in score_map:  # 检查是否存在映射
                label_type = score_map[label]['type']
                results[category][label] = classify_esg(plain_text, label_type)
            else:
                print(f"Warning: No score map found for {label}")
                results[category][label] = 'No score available'

    for category, labels in results.items():
        print(f"{category.capitalize()}:")
        for label, score in labels.items():
            print(f"  {label}: {score}")

    return results


# Example usage
if __name__ == "__main__":
    # 使用实际的文件路径
    file_path = '../ESG_reports/Apple.md'
    process_and_classify_esg(file_path)
