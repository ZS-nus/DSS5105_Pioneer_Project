import csv
import re
import json
import os

def load_company_data(company_file):
    """Load company data from CSV and return a dictionary mapping CompanyID to CompanyName."""
    company_data = {}
    with open(company_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            company_data[row['CompanyID']] = row['CompanyName']
    return company_data

def load_environment_data(environment_file):
    """Load environmental data from CSV and return a list of dictionaries."""
    environment_data = []
    with open(environment_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            environment_data.append(row)
    return environment_data

def match_numeric_value(token, value):
    """Attempt to match a token to a numeric value, allowing for some flexibility in format."""
    try:
        return float(token) == float(value)
    except ValueError:
        return False

def label_data(text, company_data, environment_data):
    """Label data in the input text and return labeled data in BIO format and JSON format."""
    labeled_lines = []
    json_data = []

    # Define keywords for specific environmental metrics
    metrics_keywords = {
        "ENERGY_CONSUMPTION": "MWh",
        "GHG_EMISSIONS": "tonne",
        "WATER_USAGE": "tonne",
        "RENEWABLE_ENERGY": "MWh"
    }

    for line in text:
        tokens = line.split()
        labeled_tokens = []

        # Extract the company ID and year from the line if applicable
        company_id = None
        report_year = None

        # Check if the line contains a company name and year
        for cid, cname in company_data.items():
            if cname in line:
                match = re.search(r'\b(20\d{2})\b', line)
                if match:
                    report_year = match.group(1)
                company_id = cid
                break

        # Now label the line based on the environmental data
        for token in tokens:
            labeled = False

            # Check for environmental metrics if company and year are identified
            if company_id and report_year:
                for env in environment_data:
                    if env['CompanyID'] == company_id and env['ReportYear'] == report_year:
                        for metric, unit in metrics_keywords.items():
                            if unit in token and match_numeric_value(token.replace(unit, ''), env.get(metric, '')):
                                labeled_tokens.append(f'B-{metric}: {token}')
                                json_data.append({"text": token, "label": metric})
                                labeled = True
                                break
                        if labeled:
                            break

            # Year recognition
            if not labeled and re.match(r'20\d{2}', token):
                labeled_tokens.append(f'B-YEAR: {token}')
                json_data.append({"text": token, "label": "YEAR"})
                labeled = True

            # Outside any entity
            if not labeled:
                labeled_tokens.append(token)

        labeled_lines.append(' '.join(labeled_tokens))

    return labeled_lines, json_data

def save_to_json(output_file, json_data):
    """Save labeled data to a JSON file, only including entities (non-O labels)."""
    filtered_data = [item for item in json_data if item["label"] != "O"]
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=4)

def label_all_txt_files(input_dir, output_dir, company_file, environment_file):
    """Label all .txt files in the specified directory."""
    company_data = load_company_data(company_file)
    environment_data = load_environment_data(environment_file)

    for filename in os.listdir(input_dir):
        if filename.endswith('.txt'):
            input_file = os.path.join(input_dir, filename)
            output_bio_file = os.path.join(output_dir, f"{filename[:-4]}_BIO.txt")
            output_json_file = os.path.join(output_dir, f"{filename[:-4]}_labels.json")

            with open(input_file, 'r', encoding='utf-8') as f:
                text = f.readlines()

            labeled_lines, json_data = label_data(text, company_data, environment_data)

            with open(output_bio_file, 'w', encoding='utf-8') as f:
                f.writelines('\n'.join(labeled_lines))

            save_to_json(output_json_file, json_data)

            print(f"Labeled data saved to: {output_bio_file}")
            print(f"Labeled data saved to: {output_json_file}")

if __name__ == "__main__":
    input_dir = "../txt_files"  # Adjust this path as needed
    output_dir = "../labeled_files"
    environment_file = "../data_temp/Pioneer DS project - Environment.csv"  # Adjust this path as needed
    company_file = "../data_temp/Pioneer DS project - Company.csv"  # Adjust this path as needed

    label_all_txt_files(input_dir, output_dir, company_file, environment_file)
