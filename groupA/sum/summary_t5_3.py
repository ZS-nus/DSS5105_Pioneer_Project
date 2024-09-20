import re
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

def read_file(file_path):
    """读取txt文件内容"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def preprocess_text(text):
    """对文本进行预处理，去除重复和无意义的内容"""
    # 1. 去除重复行
    lines = text.splitlines()
    unique_lines = list(dict.fromkeys(lines))  # 保留唯一行

    # 2. 去除特定关键词的重复
    processed_text = ' '.join(unique_lines)
    processed_text = re.sub(r'(数据来源)+', '', processed_text)  # 去除"数据来源"的重复
    processed_text = re.sub(r'(层)+', '', processed_text)  # 去除"层"的重复
    processed_text = re.sub(r'(件)+', '', processed_text)  # 去除"件"的重复
    processed_text = re.sub(r'(优势)+', '', processed_text)  # 去除"优势"的重复
    processed_text = re.sub(r'(<extra_id_\d>)+', '', processed_text)  # 去除无用的标记

    # 3. 去除多余的空格和无意义字符
    processed_text = re.sub(r'\s+', ' ', processed_text).strip()  # 去除多余的空格

    return processed_text

def generate_summary(text, model_name="uer/t5-small-chinese-cluecorpussmall", max_length=150, num_beams=4):
    """使用预训练的中文T5模型生成摘要"""
    # 使用 AutoTokenizer 和 AutoModelForSeq2SeqLM 自动加载分词器和模型
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    # 编码输入文本
    inputs = tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=512, truncation=True)

    # 生成摘要
    summary_ids = model.generate(
        inputs, 
        max_length=max_length, 
        num_beams=num_beams, 
        length_penalty=2.0, 
        early_stopping=True
    )

    # 解码生成的摘要
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

def save_summary_to_file(summary, output_file):
    """保存生成的摘要到文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"Summary successfully saved to {output_file}")

def summarize_txt(file_path, output_file):
    """读取txt文件、预处理文本、生成摘要并保存"""
    # 读取输入文本
    input_text = read_file(file_path)

    # 预处理文本
    preprocessed_text = preprocess_text(input_text)

    # 使用中文T5模型生成摘要
    generated_summary = generate_summary(preprocessed_text, model_name="uer/t5-small-chinese-cluecorpussmall", max_length=200, num_beams=5)

    # 保存摘要到文件
    save_summary_to_file(generated_summary, output_file)

if __name__ == "__main__":
    # 输入的txt文件路径
    input_file_path = '../../ESG_reports/seres_car.txt'
    output_file_path = '../../ESG_reports/seres_summary.txt'

    # 调用主函数生成摘要
    summarize_txt(input_file_path, output_file_path)
