import os
import re

def check_keywords(content, keywords):
    for keyword in keywords:
        if re.search(r'\b' + re.escape(keyword) + r'\b', content):
            return 1
    return 0

def scan_esg_reports():
    esg_folder = 'ESG_reports'
    keywords = {
        'data_security': ['customer privacy', 'data breaches', 'security issue', 'cost of data breaches', 'cybersecurity'],
        'ethical': ['corruption', 'corrupt'],
        'diversity_inclusion': ['age', 'gender'],
        'board_diversity': ['board diversity'],
        'risk_management': ['risk management', 'risk management system', 
                            'safety improvement suggestions', 'safety improvement suggestion','risk']
    }
    
    results = {}
    
    for filename in os.listdir(esg_folder):
        if filename.endswith('.md'):
            file_path = os.path.join(esg_folder, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().lower()
            
            file_results = {}
            for category, category_keywords in keywords.items():
                result = check_keywords(content, category_keywords)
                file_results[category] = f"{category.replace('_', ' ')}:{result}"
            
            results[filename] = file_results

    return results

if __name__ == "__main__":
    scan_results = scan_esg_reports()
    for file, categories in scan_results.items():
        print(f"\n{file}:")
        for category, result in categories.items():
            print(f"  {result}")


