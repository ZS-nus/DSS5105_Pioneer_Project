import jieba
import pandas as pd

# 读取文本文件
with open('../../ESG_reports/seres_car.txt', 'r', encoding='utf-8') as file:
    text = file.read()

# 使用jieba进行分词
keywords = jieba.cut(text)

# 创建关键词计数
word_freq = {}
for word in keywords:
    if word.strip():  # 排除空白字符
        word_freq[word] = word_freq.get(word, 0) + 1

# 按出现频率排序
sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

# 筛选出现次数多的关键词
important_keywords = [word for word, freq in sorted_keywords if len(word) > 1 and freq > 1]  # 筛选词长大于1的词，且出现频率大于1次

# 生成摘要
summary = ' '.join(important_keywords[:50])  # 选取前50个关键词生成摘要

print('摘要：')
print(summary)
