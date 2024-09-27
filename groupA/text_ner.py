import torch
from transformers import BertTokenizer, BertForTokenClassification
from transformers import pipeline

# 加载预训练的BERT模型和分词器，用于命名实体识别
tokenizer = BertTokenizer.from_pretrained('dbmdz/bert-large-cased-finetuned-conll03-english')
model = BertForTokenClassification.from_pretrained('dbmdz/bert-large-cased-finetuned-conll03-english')

# NER任务管道
ner_pipeline = pipeline('ner', model=model, tokenizer=tokenizer)

def read_file(file_path):
    """读取文本文件"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def save_ner_results(ner_results, output_file):
    """保存NER结果到文件"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for result in ner_results:
                f.write(f"{result['word']}: {result['entity']}\n")
        print(f"NER results successfully saved to {output_file}")
    except Exception as e:
        print(f"Failed to save NER results: {e}")

def merge_tokens(ner_results):
    """将分词结果合并为完整的实体"""
    entities = []
    current_entity = ""
    current_label = None

    for result in ner_results:
        word = result['word']
        label = result['entity']

        # 如果是子词，拼接到当前实体
        if word.startswith("##"):
            current_entity += word[2:]  # 去掉##并拼接
        else:
            # 如果有正在处理的实体，先存储它
            if current_entity:
                entities.append((current_entity, current_label))
            # 开始新的实体
            current_entity = word
            current_label = label

    # 最后一个实体添加进结果
    if current_entity:
        entities.append((current_entity, current_label))

    return entities

def perform_ner(file_path):
    """对文本文件执行命名实体识别"""
    # 读取文件内容
    text = read_file(file_path)

    # 执行NER识别
    ner_results = ner_pipeline(text)

    # 输出NER识别结果（原始结果）
    for entity in ner_results:
        print(f"{entity['word']}: {entity['entity']}")

    # 合并分词结果
    merged_entities = merge_tokens(ner_results)

    # 保存合并后的结果到文件
    output_file = '../ESG_reports/ner_tesla.txt'  # 使用txt文件来保存结果
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for entity, label in merged_entities:
                f.write(f"{entity}: {label}\n")
        print(f"NER results successfully saved to {output_file}")
    except Exception as e:
        print(f"Failed to save NER results: {e}")

    # 打印合并后的实体
    print(merged_entities)


# 示例调用：
if __name__ == "__main__":
    # 使用实际的文件路径
    file_path = '../ESG_reports/tesla.txt'  # 将文件路径更改为txt文件
    perform_ner(file_path)
