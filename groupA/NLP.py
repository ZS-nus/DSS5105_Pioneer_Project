# pip install markdown
# pip install regex
# pip install transformers
# pip install datasets
# pip install torch
# pip install sentencepiece

import markdown
import re
from bs4 import BeautifulSoup
from transformers import AutoTokenizer
from datasets import Dataset, Features, Sequence, Value, ClassLabel
from transformers import AutoModelForTokenClassification
from transformers import TrainingArguments, Trainer, DataCollatorForTokenClassification
import os


# ... 其他函数保持不变 ...

# 定义标签列表
# label_list = ['O', 'B-Environmental', 'I-Environmental', 'B-Social', 'I-Social', 'B-Governance', 'I-Governance']
# label2id = {label: i for i, label in enumerate(label_list)}
# id2label = {i: label for i, label in enumerate(label_list)}

def read_markdown_file(file_path):
    """Read a Markdown file and return its content"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def process_markdown_files(directory):
    """Process all Markdown files in the specified directory"""
    texts = []
    for filename in os.listdir(directory):
        if filename.endswith('.md'):
            file_path = os.path.join(directory, filename)
            markdown_content = read_markdown_file(file_path)
            plain_text = markdown_to_text(markdown_content)
            texts.append(plain_text)
    return texts

# 示例数据
texts = [
    markdown_to_text("# Company Report\nThe company reduced its carbon footprint."),
    markdown_to_text("# Sustainability\nNew policies for social welfare were introduced."),
]

# 示例标签
labels_list = [
    {31: 'B-Environmental', 37: 'I-Environmental'},  # 'carbon footprint'
    {35: 'B-Social', 41: 'I-Social'},  # 'social welfare'
]

# 初始化tokenizer
tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')

# 标记化并对齐标签
tokenized_dataset = tokenize_and_align_labels(texts, labels_list)

# 打印tokenized_dataset以检查内容
print("Tokenized dataset (first few items):")
for key, value in tokenized_dataset.items():
    print(f"{key}: {value[:2]}")  # 只打印前两个项目

# 定义特征
features = Features({
    'input_ids': Sequence(Value('int32')),
    'attention_mask': Sequence(Value('int8')),
    'labels': Sequence(ClassLabel(num_classes=len(label_list), names=label_list))
})

# 创建数据集
dataset = Dataset.from_dict(tokenized_dataset, features=features)

print(dataset)

# 加载预训练模型
model = AutoModelForTokenClassification.from_pretrained(
    "bert-base-uncased", 
    num_labels=len(label_list),
    id2label=id2label,
    label2id=label2id
)

# 设置训练参数
training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=3,
    weight_decay=0.01,
)

# 初始化Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    eval_dataset=dataset,
    tokenizer=tokenizer,
    data_collator=DataCollatorForTokenClassification(tokenizer),
)

# 训练模型
trainer.train()

# 保存模型
trainer.save_model("./esg_ner_model")

def extract_esg_data(markdown_text):
    text = markdown_to_text(markdown_text)
    inputs = tokenizer(
        text,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=128,
    )
    outputs = model(**inputs)
    predictions = outputs.logits.argmax(-1).squeeze().tolist()
    tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'].squeeze())

    esg_data = []
    for token, pred in zip(tokens, predictions):
        label = id2label[pred]
        esg_data.append((token, label))
    return esg_data

# 使用示例
esg_report_dir = 'ESG_report'  # 请确保这是正确的路径
processed_texts = process_markdown_files(esg_report_dir)

# 打印处理后的文本数量
print(f"处理了 {len(processed_texts)} 个 Markdown 文件")

# 如果需要，可以打印每个处理后的文本的一部分
for i, text in enumerate(processed_texts):
    print(f"文件 {i+1} 的前100个字符: {text[:100]}...")
    


# 主程序
if __name__ == "__main__":
    # 在这里定义文件路径或目录
    file_path = 'ESG_report/tesla.md'  # 单个文件的例子
    # file_path = 'ESG_report'  # 整个目录的例子

    # 处理 Markdown 文件
    processed_texts = process_markdown_files(file_path)

    print(f"处理了 {len(processed_texts)} 个 Markdown 文件")

    # ... [后续代码保持不变] ...


