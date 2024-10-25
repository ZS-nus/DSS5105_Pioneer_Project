import re
import pandas as pd
from io import StringIO
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_to_standard_unit(value, unit):
    conversions = {
        'kwh': 0.001,  # kWh to MWh
        'gwh': 1000,   # GWh to MWh
        'mt': 1,       # Metric tonnes to tonnes
        'kg': 0.001,   # kg to tonnes
        'ml': 0.000001,# milliliters to tonnes (assuming water density)
        'm3': 1,       # cubic meters to tonnes (assuming water density)
        'million gallons': 3785.41  # million gallons to tonnes
    }
    return value * conversions.get(unit.lower(), 1)

def extract_tables(text):
    table_pattern = r'Table \d+.*?\n={10,}\n(.*?)\n={10,}'
    tables = re.findall(table_pattern, text, re.DOTALL)
    return tables

def table_to_dataframe(table_text):
    lines = table_text.strip().split('\n')
    data = []
    headers = []
    for line in lines:
        row = re.split(r'\s{2,}', line.strip())
        if not headers:
            headers = row
        else:
            if len(row) < len(headers):
                row.extend([''] * (len(headers) - len(row)))
            elif len(row) > len(headers):
                headers.extend([''] * (len(row) - len(headers)))
            data.append(row)
    
    df = pd.DataFrame(data, columns=headers)
    return df

def is_relevant_table(df):
    metrics = {
        'EnergyConsumption': ['energy', 'electricity', 'power', 'consumption'],
        'GHGEmissions': ['ghg', 'emissions', 'co2', 'carbon', 'greenhouse'],
        'WaterUsage': ['water', 'h2o', 'aqua'],
        'WasteGenerated': ['waste', 'trash', 'garbage', 'refuse'],
        'RenewableEnergyUse': ['renewable', 'clean energy', 'green energy', 'solar', 'wind']
    }
    
    # Check if any column name contains a year between 2000 and 2030
    has_year = any('20' in str(col) and str(col).replace('20', '').isdigit() for col in df.columns)
    
    # Check if any of the relevant keywords are in the DataFrame
    has_keywords = any(keyword in df.values.astype(str).sum().lower() for keywords in metrics.values() for keyword in keywords)
    
    return has_year and has_keywords

def extract_latest_year_data(df):
    metrics = {
        'EnergyConsumption': ['energy', 'electricity', 'power', 'consumption'],
        'GHGEmissions': ['ghg', 'emissions', 'co2', 'carbon', 'greenhouse'],
        'WaterUsage': ['water', 'h2o', 'aqua'],
        'WasteGenerated': ['waste', 'trash', 'garbage', 'refuse'],
        'RenewableEnergyUse': ['renewable', 'clean energy', 'green energy', 'solar', 'wind']
    }

    extracted_data = {}
    year_columns = [col for col in df.columns if '20' in str(col) and str(col).replace('20', '').isdigit()]
    
    if not year_columns:
        logger.warning("No valid year columns found in the table")
        return extracted_data

    latest_year = max(year_columns, key=lambda x: int(str(x).split()[-1]))
    extracted_data['ReportYear'] = int(str(latest_year).split()[-1])

    for metric, keywords in metrics.items():
        for index, row in df.iterrows():
            if any(keyword in ' '.join(row.astype(str)).lower() for keyword in keywords):
                try:
                    value = float(str(df.at[index, latest_year]).replace(',', ''))
                    unit = row.iloc[-1] if pd.notna(row.iloc[-1]) else ''
                    if unit:
                        value = convert_to_standard_unit(value, unit)
                    extracted_data[metric] = value
                    break
                except ValueError:
                    logger.warning(f"Could not convert value for {metric}")

    return extracted_data

def main():
    with open("../txt_files/apple.txt", "r", encoding="utf-8") as file:
        text = file.read()

    tables = extract_tables(text)
    all_extracted_data = []

    for i, table in enumerate(tables, 1):
        df = table_to_dataframe(table)
        
        if is_relevant_table(df):
            print(f"\nDataFrame for Table {i}:")
            print(df.to_string())
            print("\n" + "="*50 + "\n")
            
            extracted_data = extract_latest_year_data(df)
            if extracted_data:
                all_extracted_data.append(extracted_data)
        else:
            print(f"\nTable {i} is not relevant and will be skipped.")

    if all_extracted_data:
        latest_data = max(all_extracted_data, key=lambda x: x.get('ReportYear', 0))
        
        print("Extracted Environmental Data:")
        print(f"Report Year: {latest_data.get('ReportYear', 'N/A')}")
        for metric in ['EnergyConsumption', 'GHGEmissions', 'WaterUsage', 'WasteGenerated', 'RenewableEnergyUse']:
            print(f"{metric}: {latest_data.get(metric, 'N/A')} {'MWh' if 'Energy' in metric else 'tonne'}")

        # df_result = pd.DataFrame([latest_data])
        # df_result.to_csv('extracted_environmental_data.csv', index=False)
        # print("\nData saved to 'extracted_environmental_data.csv'")
    else:
        logger.error("No valid data extracted from tables.")

if __name__ == "__main__":
    main()
