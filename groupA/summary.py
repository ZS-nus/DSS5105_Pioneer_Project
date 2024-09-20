import torch
from transformers import BartTokenizer, BartForConditionalGeneration

def read_file(file_path):
    """读取txt文件"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def generate_summary(text, model, tokenizer, max_length=300, min_length=100):
    """使用预训练的BART模型生成摘要"""
    inputs = tokenizer([text], max_length=1024, return_tensors='pt', truncation=True)
    summary_ids = model.generate(
        inputs['input_ids'],
        num_beams=6,  # 提升beam search的宽度以得到更多候选摘要
        max_length=max_length,  # 增加摘要的最大长度
        min_length=min_length,  # 增加摘要的最小长度
        length_penalty=2.0,  # 长度惩罚，平衡摘要的简短和信息完整性
        early_stopping=True
    )
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

def save_summary(summary, output_file):
    """将生成的摘要保存到文件"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Summary successfully saved to {output_file}")
    except Exception as e:
        print(f"Failed to save summary: {e}")

def summarize_txt(file_path, output_file):
    """读取txt文件、生成摘要并保存"""
    # 加载预训练的BART模型和分词器
    tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
    model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')

    # 读取文件并生成摘要
    text = read_file(file_path)
    summary = generate_summary(text, model, tokenizer)

    # 保存摘要到文件
    save_summary(summary, output_file)

    # 打印摘要到控制台
    print("Generated Summary:")
    print(summary)


# 示例调用
if __name__ == "__main__":
    # 使用txt文件路径
    input_file = '../ESG_reports/tesla.txt'
    output_file = '../ESG_reports/tesla_summary.txt'
    summarize_txt(input_file, output_file)
