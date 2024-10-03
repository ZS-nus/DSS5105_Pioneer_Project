import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# 使用BART模型或T5模型
tokenizer = AutoTokenizer.from_pretrained("fnlp/bart-large-chinese")
model = AutoModelForSeq2SeqLM.from_pretrained("fnlp/bart-large-chinese")

# 检查是否有可用的GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)  # 将模型移动到GPU

# 拆分文本函数
def split_text(text, max_len=512):
    sentences = text.split('。')
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence_length = len(sentence)
        if current_length + sentence_length <= max_len:
            current_chunk.append(sentence)
            current_length += sentence_length
        else:
            chunks.append('。'.join(current_chunk) + '。')
            current_chunk = [sentence]
            current_length = sentence_length
    if current_chunk:
        chunks.append('。'.join(current_chunk) + '。')
    return chunks

# 生成摘要函数
def summarize_chinese_txt_file(file_path, max_length=200):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    # 拆分大文本
    chunks = split_text(text)
    summary_list = []
    
    for i, chunk in enumerate(chunks):
        # 对文本进行tokenize
        inputs = tokenizer.encode(chunk, return_tensors="pt", max_length=512, truncation=True).to(device)  # 将输入移动到GPU
        
        # 生成摘要
        summary_ids = model.generate(inputs, max_length=max_length, min_length=50, length_penalty=1.0, num_beams=2, early_stopping=True)
        
        # 将生成的结果移回CPU，并解码生成摘要
        summary = tokenizer.decode(summary_ids[0].cpu(), skip_special_tokens=True)
        summary_list.append(summary)
        
        # 打印进度
        print(f"Processed chunk {i+1}/{len(chunks)}")
    
    # 合并所有摘要
    return ' '.join(summary_list)

# 使用示例，大文本文件路径
file_path = '../../ESG_reports/seres_car.txt'
summary = summarize_chinese_txt_file(file_path)

print("大文本的摘要:")
print(summary)
