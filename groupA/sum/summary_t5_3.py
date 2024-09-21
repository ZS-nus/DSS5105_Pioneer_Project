import re
import jionlp as jio
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

def read_file(file_path):
    """读取txt文件内容"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def preprocess_text(text):
    """对文本进行预处理，去除重复和无意义的内容"""
    # 去除重复行
    lines = text.splitlines()
    unique_lines = list(dict.fromkeys(lines))

    # 删除含有无意义的字符
    unique_lines = [line for line in unique_lines if len(line.strip()) > 1]

    # 合并文本并去除多余空格
    processed_text = ' '.join(unique_lines)
    processed_text = re.sub(r'\s+', ' ', processed_text).strip()

    # 进一步去除特殊字符和标记
    processed_text = re.sub(r'[”“’‘]', '', processed_text)  # 去除中文引号
    processed_text = re.sub(r'[^\w\s.,]', '', processed_text)  # 去除非字母、数字和常规标点符号

    return processed_text

def extract_key_sentences(text, max_sentences=5):
    """使用jioNLP抽取重要句子，手动控制句子数量"""
    extracted_summary = jio.summary.extract_summary(text)
    
    # 将抽取出的摘要分割成句子
    sentences = re.split(r'(。|！|\!|\.|？|\?)', extracted_summary)
    
    # 根据max_sentences控制返回的句子数量
    selected_sentences = ''.join(sentences[:2 * max_sentences])  # 保留句子
    return selected_sentences

def generate_summary_with_t5(text, model_name="uer/t5-small-chinese-cluecorpussmall", max_length=200):
    """使用AutoTokenizer和AutoModel生成总结"""
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    # 编码输入文本
    inputs = tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=512, truncation=True)

    # 生成摘要
    summary_ids = model.generate(inputs, max_length=max_length, num_beams=5, early_stopping=True)

    # 解码生成的摘要
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

def save_summary_to_file(summary, output_file):
    """保存生成的摘要到文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"摘要已成功保存到 {output_file}")

def summarize_txt(file_path, output_file):
    """读取txt文件、预处理文本、生成摘要并保存"""
    # 读取输入文本
    input_text = read_file(file_path)

    # 预处理文本
    preprocessed_text = preprocess_text(input_text)

    # 使用jioNLP抽取重要句子
    key_sentences = extract_key_sentences(preprocessed_text, max_sentences=5)

    # 使用T5模型进一步总结抽取出的内容
    generated_summary = generate_summary_with_t5(key_sentences)

    # 保存摘要到文件
    save_summary_to_file(generated_summary, output_file)

if __name__ == "__main__":
    # 输入的txt文件路径
    input_file_path = '../../ESG_reports/seres_car.txt'
    output_file_path = '../../ESG_reports/seres_summary.txt'

    # 调用主函数生成摘要
    summarize_txt(input_file_path, output_file_path)
