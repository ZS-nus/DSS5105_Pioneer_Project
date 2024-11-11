import os
import re
from fuzzywuzzy import fuzz

def check_keywords(content, keywords, similarity_threshold=60):
    content_lower = content.lower()
    for keyword in keywords:
        if len(keyword.split()) > 1:
            # 对于多词短语，使用整体匹配
            if keyword.lower() in content_lower:
                return 1      
            
        else:
            # 对于单个词，使用单词匹配
            for word in re.findall(r'\b\w+\b', content_lower):
                similarity = fuzz.ratio(keyword.lower(), word)
                if similarity >= similarity_threshold:
                    return 1
    return 0

def find_iso_certificates(content):
    # 使用正则表达式匹配 ISO 证书
    iso_pattern = r'ISO\s*\d{4,5}(?::\d{4})?'
    iso_certificates = re.findall(iso_pattern, content)
    return list(set(iso_certificates))

def scan_txt_files():
    txt_folder = '../txt_files'
    keywords = {
        'data_security': [
            'data security', 'information protection', 'data privacy',
            'data breach', 'information security', 'data encryption',
            'data protection', 'secure data', 'data confidentiality', 'data integrity'
        ],
        'cybersecurity': [
            'cybersecurity', 'cyber threat', 'cyber attack', 'cyber risk',
            'cyber defense', 'cyber incident', 'cyber vulnerability', 'cyber resilience',
            'cyber protection', 'network security', 'cyber crime', 'malware',
            'ransomware', 'phishing', 'firewall', 'cyber awareness'
        ],
        'customer_privacy': [
            'customer privacy', 'privacy policy', 'privacy protection', 'privacy rights',
            'personal information', 'data subject rights', 'privacy compliance', 
            'privacy notice', 'privacy impact', 'customer consent', 'privacy breach',
            'privacy risk', 'privacy management', 'data collection', 'data processing',
            'data retention', 'privacy training', 'privacy framework', 'GDPR', 'CCPA'
        ],
        'ethical_corruption': [
            'ethical conduct', 'anti-corruption', 'bribery', 'integrity',
            'ethical standards', 'code of ethics', 'ethical behavior', 'corruption prevention',
            'ethical compliance', 'ethical guidelines', 'ethical practices', 'anti-fraud'
        ],
        'age_gender_diversity': [
            'age', 'gender',
            'age diversity', 'gender diversity', 'generational diversity', 'gender equality',
            'age inclusion', 'gender balance', 'age representation', 'gender representation',
            'multigenerational workforce', 'gender parity', 'age discrimination', 'gender bias'
        ],
        'board_diversity': [
            'board diversity', 'diverse board', 'board composition', 'inclusive governance',
            'diverse leadership', 'board representation', 'diversity in leadership',
            'board inclusivity', 'diverse perspectives in board', 'board member diversity'
        ],
        'risk_management': [
            'risk',
            'risk management', 'risk assessment', 'risk mitigation', 'risk control',
            'enterprise risk management', 'risk identification', 'risk monitoring',
            'risk strategy', 'risk analysis', 'risk reporting', 'risk governance'
        ]
    }
    
    results = {}
    
    for filename in os.listdir(txt_folder):
        if filename.endswith('.txt'):
            file_path = os.path.join(txt_folder, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            file_results = {}
            for category, category_keywords in keywords.items():
                result = check_keywords(content, category_keywords)
                file_results[category] = f"{category.replace('_', ' ')}:{result}"
            
            results[filename] = file_results
            
            iso_certificates = find_iso_certificates(content)
            file_results['iso_certificates'] = iso_certificates

    return results

if __name__ == "__main__":
    scan_results = scan_txt_files()
    for file, categories in scan_results.items():
        print(f"\n{file}:")
        for category, result in categories.items():
            print(f"  {result}")
