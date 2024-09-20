import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
from tqdm import tqdm  # 进度条库，用于显示进度

def read_file(file_path):
    """读取文本文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Failed to read file: {e}")
        return None

def split_text(text, chunk_size=512):
    """将长文本分成多个小块"""
    words = text.split()
    return [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

def generate_summary(text, model, tokenizer, max_length=150, min_length=50):
    """使用预训练的T5模型生成摘要"""
    # 在输入文本前加上任务提示 "summarize: "
    inputs = tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=512, truncation=True)
    # 使用 T5 模型生成摘要
    summary_ids = model.generate(
        inputs, 
        num_beams=4,      # 使用beam search提高摘要质量
        max_length=max_length, 
        min_length=min_length, 
        length_penalty=2.0, 
        early_stopping=True
    )
    # 将生成的ID序列解码为文本
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

def generate_summary_for_chunks(text_chunks, model, tokenizer):
    """为每个小块生成摘要并合并"""
    summaries = []
    for chunk in tqdm(text_chunks, desc="Generating Summary"):
        summary = generate_summary(chunk, model, tokenizer)
        summaries.append(summary)
    return ' '.join(summaries)

def remove_duplicates(summary):
    """去除摘要中的重复句子"""
    sentences = summary.split('. ')
    unique_sentences = list(dict.fromkeys(sentences))  # 去除重复
    return '. '.join(unique_sentences)

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
    try:
        # 加载预训练的T5模型和分词器
        tokenizer = T5Tokenizer.from_pretrained('t5-base')
        model = T5ForConditionalGeneration.from_pretrained('t5-base')

        # 读取文件内容
        text = read_file(file_path)
        if not text:
            return

        # 将文本分块
        text_chunks = split_text(text, chunk_size=512)

        # 为每个小块生成摘要并合并
        summary = generate_summary_for_chunks(text_chunks, model, tokenizer)

        # 去除重复句子
        summary = remove_duplicates(summary)

        # 保存摘要到文件
        save_summary(summary, output_file)

        print("Generated Summary:")
        print(summary)

    except Exception as e:
        print(f"Error occurred during summarization: {e}")

# 示例调用：
if __name__ == "__main__":
    # 使用txt文件的路径，确保路径正确
    input_file = '../../ESG_reports/tesla.txt' 
    output_file = '../../ESG_reports/tesla_summary.txt'
    summarize_txt(input_file, output_file)

