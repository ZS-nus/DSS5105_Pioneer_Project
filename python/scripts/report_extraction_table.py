import pandas as pd
import os
import logging
import re
from pathlib import Path
from datetime import datetime
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TableDataExtractor:
    def __init__(self):
        # Define unit conversions
        self.conversions = {
            'kwh': 0.001,  # kWh to MWh
            'gwh': 1000,   # GWh to MWh
            'mt': 1,       # Metric tonnes to tonnes
            'kg': 0.001,   # kg to tonnes
            'ml': 0.000001,# milliliters to tonnes (assuming water density)
            'm3': 1,       # cubic meters to tonnes (assuming water density)
            'million gallons': 3785.41  # million gallons to tonnes
        }
        
        # Initialize metrics dictionary with specific keywords
        self.metrics = {
            'EnergyConsumption': [
                'energy consumption',
                'electricity consumption',
                'power consumption',
                'total energy',
                'comprehensive energy'
            ],
            'GHGEmissions': [
                'ghg emissions',
                'greenhouse gas emissions',
                'carbon emissions',
                'scope 1 and 2',
                'total ghg'
            ],
            'WaterUsage': [
                'water consumption',
                'water usage',
                'water withdrawal',
                'total water'
            ],
            'WasteGenerated': [
                'waste generated',
                'total waste',
                'hazardous waste',
                'non-hazardous waste'
            ],
            'RenewableEnergyUse': [
                'renewable energy',
                'clean energy',
                'green energy',
                'solar',
                'wind power'
            ],
            'EmployeeCount': [
                'full-time employees',
                'total workforce',
                'headcount',
                'total employees'
            ]
        }

        # Initialize combined data structure
        self.combined_data = {
            "ReportYear": None,
            "EnergyConsumption": None,
            "GHGEmissions": None,
            "WaterUsage": None,
            "WasteGenerated": None,
            "RenewableEnergyUse": None,
            "EmployeeCount": None
        }

    def convert_to_standard_units(self, value: float, unit: str) -> float:
        """Convert values to standard units (MWh for energy, tonnes for others)"""
        return value * self.conversions.get(unit.lower(), 1)

    def is_relevant_table(self, df: pd.DataFrame) -> bool:
        """Check if table contains relevant environmental data"""
        try:
            # Check for year columns
            has_year = any('FY' in str(col) or '20' in str(col) for col in df.columns)
            logger.info(f"Has year columns: {has_year}")
            
            if not has_year:
                return False
            
            # Get first column text and column names for keyword checking
            first_col = df.iloc[:, 0].astype(str).str.lower()
            first_col_text = ' '.join(first_col)
            col_names = [str(col).lower() for col in df.columns]
            col_text = ' '.join(col_names)
            
            logger.info(f"First column text: {first_col_text}")
            logger.info(f"Column names: {col_text}")
            
            # Check for relevant keywords in both first column and column names
            for metric_keywords in self.metrics.values():
                for keyword in metric_keywords:
                    if keyword in first_col_text or keyword in col_text:
                        logger.info(f"Found relevant keyword: {keyword}")
                        return True
            
            return False
                
        except Exception as e:
            logger.warning(f"Error checking table relevance: {str(e)}")
            return False

    def is_intensity_metric(self, row_text: str) -> bool:
        """Check if the row represents an intensity metric"""
        intensity_indicators = [
            'per unit of',
            'per capita',
            '/rmb',
            '/person',
            'intensity',
            'per revenue'
        ]
        return any(indicator in row_text.lower() for indicator in intensity_indicators)

    def extract_latest_year_data(self, df: pd.DataFrame) -> dict:
        """Extract data for the latest year from the table"""
        try:
            extracted_data = {}
            
            # Get year columns
            year_columns = [col for col in df.columns if 'FY' in str(col) or '20' in str(col)]
            
            if not year_columns:
                logger.warning("No valid year columns found in the table")
                return extracted_data

            # Log DataFrame info for debugging
            logger.info(f"Processing DataFrame columns: {df.columns.tolist()}")
            logger.info("First few rows:")
            logger.info(df.head(2))

            # Get latest year with validation
            latest_year = None
            latest_year_num = 0
            
                    # For each metric, look for rows that contain the keyword but are NOT intensity metrics
            for metric_name, keywords in self.metrics.items():
                try:
                    matching_rows = df[df.iloc[:, 0].str.contains('|'.join(keywords), 
                                                                na=False, case=False)]
                    
                    # Filter out intensity metrics
                    matching_rows = matching_rows[~matching_rows.iloc[:, 0].apply(
                        lambda x: self.is_intensity_metric(str(x))
                    )]

                    if not matching_rows.empty:
                        value_str = str(matching_rows.iloc[0][latest_year]).replace(',', '')
                        value = float(value_str) if value_str not in ['-', '', 'nan'] else None
                        
                        if value is not None:
                            extracted_data[metric_name] = value
                            logger.info(f"Found {metric_name}: {value}")

                except Exception as e:
                    logger.warning(f"Error extracting {metric_name}: {e}")
                    continue
            
            for col in year_columns:
                try:
                    year_str = str(col).strip()
                    if 'FY' in year_str.upper():
                        # Extract all digits from the string
                        digits = re.findall(r'\d+', year_str)
                        if digits:
                            year_num = int(digits[0])
                            # If it's a 4-digit year, use it directly
                            if year_num > 1000:
                                full_year = year_num
                            else:
                                # If it's a 2-digit year, assume 2000s
                                full_year = 2000 + year_num
                    else:
                        # Direct year format (e.g., "2023")
                        full_year = int(re.findall(r'\d{4}', year_str)[0])
                    
                    # Validate year is reasonable
                    current_year = datetime.now().year
                    if 2000 <= full_year <= current_year + 1:
                        if full_year > latest_year_num:
                            latest_year_num = full_year
                            latest_year = col
                except ValueError:
                    continue
            
            if not latest_year:
                logger.warning("No valid year found in columns")
                return extracted_data
                
            logger.info(f"Latest year column found: {latest_year} (year: {latest_year_num})")
            extracted_data['ReportYear'] = latest_year_num

            # Look for employee count
            try:
                employee_rows = df[df.iloc[:, 0].str.contains('|'.join(self.metrics['EmployeeCount']), 
                                                            na=False, case=False)]
                if not employee_rows.empty:
                    value_str = str(employee_rows.iloc[0][latest_year]).replace(',', '')
                    extracted_data['EmployeeCount'] = int(float(value_str))
                    logger.info(f"Found Employee Count: {extracted_data['EmployeeCount']}")
            except Exception as e:
                logger.warning(f"Error extracting employee count: {e}")

            # Look for energy consumption
            try:
                energy_rows = df[df.iloc[:, 0].str.contains('|'.join(self.metrics['EnergyConsumption']), 
                                                          na=False, case=False)]
                if not energy_rows.empty:
                    value_str = str(energy_rows.iloc[0][latest_year]).replace(',', '')
                    extracted_data['EnergyConsumption'] = float(value_str)
                    logger.info(f"Found Energy Consumption: {extracted_data['EnergyConsumption']}")
            except Exception as e:
                logger.warning(f"Error extracting energy consumption: {e}")

            # Look for GHG emissions
            try:
                ghg_rows = df[df.iloc[:, 0].str.contains('|'.join(self.metrics['GHGEmissions']), 
                                                       na=False, case=False)]
                if not ghg_rows.empty:
                    value_str = str(ghg_rows.iloc[0][latest_year]).replace(',', '')
                    extracted_data['GHGEmissions'] = float(value_str)
                    logger.info(f"Found GHG Emissions: {extracted_data['GHGEmissions']}")
            except Exception as e:
                logger.warning(f"Error extracting GHG emissions: {e}")

            # Look for water usage
            try:
                water_rows = df[df.iloc[:, 0].str.contains('|'.join(self.metrics['WaterUsage']), 
                                                         na=False, case=False)]
                if not water_rows.empty:
                    value_str = str(water_rows.iloc[0][latest_year]).replace(',', '')
                    extracted_data['WaterUsage'] = float(value_str)
                    logger.info(f"Found Water Usage: {extracted_data['WaterUsage']}")
            except Exception as e:
                logger.warning(f"Error extracting water usage: {e}")

            # Look for waste data
            try:
                waste_rows = df[df.iloc[:, 0].str.contains('|'.join(self.metrics['WasteGenerated']), 
                                                         na=False, case=False)]
                if not waste_rows.empty:
                    total_waste = 0
                    for _, row in waste_rows.iterrows():
                        value_str = str(row[latest_year]).replace(',', '')
                        try:
                            total_waste += float(value_str)
                        except ValueError:
                            continue
                    if total_waste > 0:
                        extracted_data['WasteGenerated'] = total_waste
                        logger.info(f"Found Waste Generated: {extracted_data['WasteGenerated']}")
            except Exception as e:
                logger.warning(f"Error extracting waste data: {e}")

            # Look for renewable energy
            try:
                renewable_rows = df[df.iloc[:, 0].str.contains('|'.join(self.metrics['RenewableEnergyUse']), 
                                                             na=False, case=False)]
                if not renewable_rows.empty:
                    value_str = str(renewable_rows.iloc[0][latest_year]).replace(',', '')
                    extracted_data['RenewableEnergyUse'] = float(value_str)
                    logger.info(f"Found Renewable Energy Use: {extracted_data['RenewableEnergyUse']}")
            except Exception as e:
                logger.warning(f"Error extracting renewable energy data: {e}")

            logger.info(f"Extracted data from table: {extracted_data}")
            return extracted_data
                
        except Exception as e:
            logger.error(f"Error extracting data: {str(e)}")
            return {}

    def is_intensity_metric(self, row_text: str) -> bool:
        """Check if the row represents an intensity metric"""
        intensity_indicators = [
            'per unit of',
            'per capita',
            '/rmb',
            '/person',
            'intensity',
            'per revenue',
            'million'
        ]
        return any(indicator in str(row_text).lower() for indicator in intensity_indicators)

    def process_tables(self, table_dir: str) -> dict:
        """Process all CSV tables in the directory"""
        try:
            if not table_dir:
                logger.error("Table directory path is empty or None")
                return {
                    "status": "error",
                    "message": "Invalid table directory path",
                    "data": None
                }

            table_dir = Path(table_dir)
            if not table_dir.exists():
                logger.error(f"Table directory not found: {table_dir}")
                return {
                    "status": "error",
                    "message": f"Table directory not found: {table_dir}",
                    "data": None
                }

            csv_files = list(table_dir.glob('*.csv'))
            if not csv_files:
                logger.error(f"No CSV files found in directory: {table_dir}")
                return {
                    "status": "error",
                    "message": "No CSV files found in directory",
                    "data": None
                }

            processed_tables = []
            year_counts = {}  # Track frequency of each year
            combined_data = self.combined_data.copy()  # Create a copy of the template

            for csv_file in csv_files:
                try:
                    logger.info(f"\nProcessing {csv_file.name}")
                    df = pd.read_csv(csv_file)
                    
                    if df.empty:
                        logger.info(f"Table {csv_file.name} rejected: Empty DataFrame")
                        continue

                    if not self.is_relevant_table(df):
                        logger.info(f"Table {csv_file.name} rejected: Not relevant")
                        continue

                    # Skip tables that only contain intensity metrics
                    first_col_values = df.iloc[:, 0].astype(str)
                    if all(self.is_intensity_metric(val) for val in first_col_values):
                        logger.info(f"Skipping {csv_file.name}: Contains only intensity metrics")
                        continue

                    extracted_data = self.extract_latest_year_data(df)
                    if extracted_data:
                        # Track year frequency
                        if 'ReportYear' in extracted_data:
                            year = extracted_data['ReportYear']
                            year_counts[year] = year_counts.get(year, 0) + 1
                        
                        # Update combined data with absolute values only
                        for key, value in extracted_data.items():
                            if key in combined_data and value is not None:
                                row_text = df[df.iloc[:, 0].astype(str).str.contains(
                                    '|'.join(self.metrics.get(key, [])), 
                                    case=False, 
                                    na=False
                                )].iloc[0, 0]
                                
                                # Only update if not an intensity metric
                                if not self.is_intensity_metric(str(row_text)):
                                    combined_data[key] = value
                                    logger.info(f"Updated {key} with absolute value: {value}")
                                else:
                                    logger.info(f"Skipped intensity metric for {key}: {row_text}")
                        
                        processed_tables.append({
                            "table_name": csv_file.name,
                            "found_metrics": list(extracted_data.keys()),
                            "is_relevant": True
                        })
                    else:
                        logger.info(f"Table {csv_file.name} rejected: No valid data extracted")

                except Exception as e:
                    logger.error(f"Error processing table {csv_file.name}: {str(e)}")
                    continue

            # After processing all tables, set the most frequent year
            if year_counts:
                most_common_year = max(year_counts.items(), key=lambda x: x[1])[0]
                logger.info(f"Most common year across tables: {most_common_year} "
                        f"(appeared in {year_counts[most_common_year]} tables)")
                combined_data['ReportYear'] = most_common_year
            else:
                logger.warning("No valid years found across tables")

            # Clean the data for JSON serialization
            clean_metrics = {}
            for key, value in combined_data.items():
                # Convert nan to None and keep other values
                if isinstance(value, float) and math.isnan(value):
                    clean_metrics[key] = None
                else:
                    clean_metrics[key] = value

            # Track what metrics were found and not found
            found_metrics = []
            missing_metrics = []
            
            # Check what metrics were found
            for metric, value in clean_metrics.items():
                if metric != 'ReportYear':  # Skip ReportYear from this check
                    if value is not None:
                        found_metrics.append(metric)
                    else:
                        missing_metrics.append(metric)

            # Get report name from directory path
            report_name = Path(table_dir).name

            return {
                "status": "success",
                "data": {
                    "report_name": report_name,
                    "metrics": {
                        "ReportYear": clean_metrics['ReportYear'],
                        "EnergyConsumption": clean_metrics['EnergyConsumption'],
                        "GHGEmissions": clean_metrics['GHGEmissions'],
                        "WaterUsage": clean_metrics['WaterUsage'],
                        "WasteGenerated": clean_metrics['WasteGenerated'],
                        "RenewableEnergyUse": clean_metrics['RenewableEnergyUse'],
                        "EmployeeCount": clean_metrics['EmployeeCount']
                    },
                    "metrics_found": found_metrics,
                    "metrics_missing": missing_metrics
                }
            }

        except Exception as e:
            logger.error(f"Critical error in process_tables: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "message": f"Critical error processing tables: {str(e)}",
                "data": None
            }

def main():
    """Test the TableDataExtractor"""
    extractor = TableDataExtractor()
    result = extractor.process_tables("path/to/table/directory")
    print(result)

if __name__ == "__main__":
    main()