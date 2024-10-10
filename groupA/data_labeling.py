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
    print(company_data)
    return company_data

def load_environment_data(environment_file):
    """Load environmental data from CSV and return a list of dictionaries."""
    environment_data = []
    with open(environment_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            environment_data.append(row)
    print(environment_data)
    return environment_data

def label_data(text, company_data, environment_data):
    """Label data in the input text and return labeled data in BIO format and JSON format."""
    labeled_lines = []
    json_data = []

    for line in text:
        tokens = line.split()  # Split the line into tokens
        labeled_tokens = []

        # Extract the company ID and year from the line if applicable
        company_id = None
        report_year = None

        # Check if the line contains a company name and year
        for company_id, company_name in company_data.items():
            if company_name in line:
                # Assuming the year is mentioned in the line, extract it
                match = re.search(r'\b(20\d{2})\b', line)
                if match:
                    report_year = match.group(1)
                break

        # Now label the line based on the environmental data
        for token in tokens:
            # Check for organization names
            if company_id and report_year:
                for env in environment_data:
                    if env['CompanyID'] == company_id and env['ReportYear'] == report_year:
                        # Label the environmental metrics
                        if token == env['EnergyConsumption(MWh)']:
                            labeled_tokens.append(f'B-ENERGY_CONSUMPTION: {token} MWh')
                            json_data.append({"text": token + " MWh", "label": "ENERGY_CONSUMPTION"})
                        elif token == env['GHG Emissions(tonne (Mt) of CO2e)']:
                            labeled_tokens.append(f'B-GHG_EMISSIONS: {token} tonne (Mt) of CO2e')
                            json_data.append({"text": token + " tonne (Mt) of CO2e", "label": "GHG_EMISSIONS"})
                        elif token == env['WaterUsage(tonne (Mt))']:
                            labeled_tokens.append(f'B-WATER_USAGE: {token} tonne (Mt)')
                            json_data.append({"text": token + " tonne (Mt)", "label": "WATER_USAGE"})
                        elif token == env['RenewableEnergyUse (MWh)']:
                            labeled_tokens.append(f'B-RENEWABLE_ENERGY: {token} MWh')
                            json_data.append({"text": token + " MWh", "label": "RENEWABLE_ENERGY"})
                        else:
                            labeled_tokens.append(f'O: {token}')  # Outside any entity
                            json_data.append({"text": token, "label": "O"})  # Outside any entity
                        break
            else:
                # Check for years
                if re.match(r'20\d{2}', token):
                    labeled_tokens.append(f'B-YEAR: {token}')
                    json_data.append({"text": token, "label": "YEAR"})
                else:
                    labeled_tokens.append(f'O: {token}')  # Outside any entity
                    json_data.append({"text": token, "label": "O"})  # Outside any entity

        labeled_lines.append(' '.join(labeled_tokens))

    return labeled_lines, json_data

def save_to_json(output_file, json_data):
    """Save labeled data to a JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)

def label_all_txt_files(input_dir,output_dir ,company_file, environment_file):
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

            # Pass the list of lines to label_data
            labeled_lines, json_data = label_data(text, company_data, environment_data)

            # Write the labeled data to the output file in BIO format
            with open(output_bio_file, 'w', encoding='utf-8') as f:
                f.writelines('\n'.join(labeled_lines))

            # Save the labeled data to a JSON file
            save_to_json(output_json_file, json_data)

            print(f"Labeled data saved to: {output_bio_file}")
            print(f"Labeled data saved to: {output_json_file}")

if __name__ == "__main__":
    input_dir = "../txt_files"  # Adjust this path as needed
    output_dir = "../labeled_files"
    environment_file = "../data_temp/Pioneer DS project - Environment.csv"  # Adjust this path as needed
    company_file = "../data_temp/Pioneer DS project - Company.csv"  # Adjust this path as needed

    label_all_txt_files(input_dir,output_dir ,company_file, environment_file)
    


# if __name__ == "__main__":
#     company_file = "../data_temp/Pioneer DS project - Company.csv"  # Adjust this path as needed
#     environment_file = "../data_temp/Pioneer DS project - Environment.csv"  # Adjust this path as needed
#     input_file = "../md_files/xiaomi.txt"  # Adjust this path as needed
#     output_bio_file = "../md_files/xiaomi_BIO.txt"  # Output file for labeled data in BIO format
#     output_json_file = "../md_files/xiaomi_JSON.json"  # Output file for labeled data in JSON format

#     # Load data from CSV files
#     company_data = load_company_data(company_file)
#     environment_data = load_environment_data(environment_file)

#     # Label the data in the text file
#     labeled_lines, json_data = label_data(input_file, company_data)

#     # Write the labeled data to the output file in BIO format
#     with open(output_bio_file, 'w', encoding='utf-8') as f:
#         f.writelines('\n'.join(labeled_lines))

#     # Save the labeled data to a JSON file
#     save_to_json(output_json_file, json_data)

#     print(f"Labeled data saved to: {output_bio_file}")
#     print(f"Labeled data saved to: {output_json_file}")