from transformers import pipeline

# 使用针对特定领域训练的 NER 模型
ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", device=0)  # 使用 GPU

def process_ner_results(results):
    """处理 NER 输出，拼接子词并生成最终实体"""
    final_entities = []
    current_entity = ""
    current_label = None

    for res in results:
        word = res['word']
        label = res['entity']

        # 如果单词是子词，则去掉 '##' 并拼接
        if word.startswith("##"):
            current_entity += word[2:]
        else:
            # 将前一个实体添加到列表中
            if current_entity:
                final_entities.append((current_entity, current_label))
            current_entity = word
            current_label = label

    # 添加最后一个实体
    if current_entity:
        final_entities.append((current_entity, current_label))

    return final_entities

# 读取输入文件内容
input_file_path = "../ESG_reports/tesla_summary.txt"  # 替换为实际输入文件路径
output_file_path = "../ESG_reports/ner_tesla.txt"  # 输出文件路径

with open(input_file_path, 'r', encoding='utf-8') as file:
    input_text = file.read()

# 获取 NER 结果
ner_results = ner_pipeline(input_text)

# 处理并拼接子词
final_results = process_ner_results(ner_results)

# 打印结果
print(final_results)

# 保存结果到文件
with open(output_file_path, 'w', encoding='utf-8') as f:
    for entity, label in final_results:
        f.write(f"{entity}\t{label}\n")
print(f"NER results successfully saved to {output_file_path}")
