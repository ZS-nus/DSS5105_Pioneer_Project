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
        
        self.year_pattern = None  # Will store 'ascending' or 'descending'
        self.latest_year = None
        
        
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
                'comprehensive energy',
                'energy used',
                '^energy used$'
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
                'non-hazardous waste',
                'total generated',  # Add this keyword
                'nonhazardous waste'
            ],
            'RenewableEnergyUse': [
                'renewable energy',
                'clean energy',
                'green energy',
                'solar',
                'wind power',
                'renewable electricity',
                'renewable power',
                'renewable sources',
                'renewable electricity use'
            ],
            'EmployeeCount': [
                'full-time employees',
                'total workforce',
                'headcount',
                'total employees',
                'employees',  
                '^employees$'  
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
            # Check minimum table size
            if df.shape[1] < 2:  # Require at least 2 columns
                logger.info("Table rejected: Too few columns")
                return False

            # Check for year columns
            has_year = any('FY' in str(col) or '20' in str(col) for col in df.columns)
            logger.info(f"Has year columns: {has_year}")
            
            if not has_year:
                logger.info("Table rejected: No year columns found")
                return False
            
            # Check numeric content ratio (excluding first column)
            numeric_ratio = self.get_numeric_ratio(df)
            logger.info(f"Numeric ratio: {numeric_ratio:.2f}")
            if numeric_ratio < 0.6:  # Increased threshold to 60%
                logger.info("Table rejected: Insufficient numeric content")
                return False
                
            # Check average text length in first column (to filter out narrative text)
            first_col_text = df.iloc[:, 0].astype(str)
            avg_text_length = sum(len(str(text)) for text in first_col_text) / len(first_col_text)
            logger.info(f"Average text length in first column: {avg_text_length:.1f}")
            if avg_text_length > 100:  # Reject if average text length is too long
                logger.info("Table rejected: First column contains long narrative text")
                return False
            
            # Get first column text and column names for keyword checking
            first_col_text = ' '.join(first_col_text.str.lower())
            col_names = [str(col).lower() for col in df.columns]
            col_text = ' '.join(col_names)
            
            logger.info(f"First column text: {first_col_text}")
            logger.info(f"Column names: {col_text}")
            
            # Special check for employee data
            if 'employees' in first_col_text and numeric_ratio > 0.5:
                logger.info("Found employees in first column")
                return True
            
            # Check for relevant keywords in both first column and column names
            for metric_name, metric_keywords in self.metrics.items():
                for keyword in metric_keywords:
                    if keyword in first_col_text or keyword in col_text:
                        logger.info(f"Found relevant keyword: {keyword}")
                        return True
            
            logger.info("Table rejected: No relevant keywords found")
            return False
                
        except Exception as e:
            logger.warning(f"Error checking table relevance: {str(e)}")
            return False
    
    def detect_year_pattern_from_tables(self, tables_dict):
        """Analyze multiple tables to determine the common year pattern"""
        year_patterns = []
        valid_years = []
        
        for table_name, df in tables_dict.items():
            try:
                # Find columns that look like years
                year_cols = []
                for col in df.columns:
                    col_str = str(col).upper()
                    if 'FY' in col_str or '20' in col_str:
                        matches = re.findall(r'\d+', col_str)
                        if matches:
                            year_num = int(matches[0])
                            if year_num < 100:
                                year_num += 2000
                            if 2000 <= year_num <= 2100:
                                year_cols.append((col, year_num))
                
                if len(year_cols) >= 2:
                    # Sort by column index
                    col_indices = [list(df.columns).index(col) for col, _ in year_cols]
                    years = [year for _, year in year_cols]
                    
                    # Check if years are ascending or descending
                    if col_indices == sorted(col_indices) and years == sorted(years):
                        year_patterns.append('ascending')
                        valid_years.extend(years)
                    elif col_indices == sorted(col_indices) and years == sorted(years, reverse=True):
                        year_patterns.append('descending')
                        valid_years.extend(years)
            
            except Exception as e:
                logger.warning(f"Error analyzing year pattern in table {table_name}: {e}")
                continue
        
        # Determine most common pattern
        if year_patterns:
            self.year_pattern = max(set(year_patterns), key=year_patterns.count)
            logger.info(f"Detected year pattern: {self.year_pattern}")
            
            # Set latest year
            if valid_years:
                self.latest_year = max(valid_years)
                logger.info(f"Detected latest year: {self.latest_year}")
        
        return self.year_pattern, self.latest_year
    
    def get_numeric_ratio(self, df: pd.DataFrame) -> float:
        try:
            if df.shape[1] <= 1:
                return 0.0
                
            # Get data columns (exclude first column)
            data_cols = df.iloc[:, 1:]
            
            def is_numeric(val):
                val_str = str(val).strip()
                # Remove special characters and handle percentages
                val_str = re.sub(r'[†‡§¶]', '', val_str)
                val_str = val_str.replace(',', '').replace('%', '')
                try:
                    float(val_str)
                    return True
                except ValueError:
                    return False
            
            # Count numeric cells
            total_cells = data_cols.size
            numeric_cells = sum(data_cols.applymap(is_numeric).sum())
            
            return numeric_cells / total_cells if total_cells > 0 else 0.0
            
        except Exception as e:
            logger.warning(f"Error calculating numeric ratio: {str(e)}")
            return 0.0

    def extract_latest_year_data(self, df: pd.DataFrame) -> dict:
        """Extract data from the latest year column"""
        extracted_data = {}
        try:
            # Find year columns
            year_cols = []
            for col in df.columns[1:]:  # Skip first column (labels)
                col_str = str(col).upper()
                # Handle FY format (e.g., FY2023, FY23)
                if 'FY' in col_str:
                    # Try full year format first (FY2023)
                    fy_match = re.search(r'FY(\d{4})', col_str)
                    if fy_match:
                        year = int(fy_match.group(1))
                        year_cols.append((col, year))
                    else:
                        # Try short year format (FY23)
                        fy_match = re.search(r'FY(\d{2})', col_str)
                        if fy_match:
                            year = 2000 + int(fy_match.group(1))
                            year_cols.append((col, year))
                # Handle direct year format
                elif '20' in col_str:
                    matches = re.findall(r'20\d{2}', col_str)
                    if matches:
                        year = int(matches[0])
                        year_cols.append((col, year))

            # If no valid years found or years look suspicious
            if not year_cols or any(year > 2100 or year < 2000 for _, year in year_cols):
                # Use the detected pattern and latest year
                if self.year_pattern and self.latest_year:
                    numeric_cols = [col for col in df.columns[1:] 
                                if any(str(x).replace(',','').replace('.','').isdigit() 
                                        for x in df[col] if pd.notna(x))]
                    
                    if numeric_cols:
                        if self.year_pattern == 'ascending':
                            latest_col = numeric_cols[-1]
                        else:
                            latest_col = numeric_cols[0]
                        
                        latest_year = self.latest_year
                        extracted_data['ReportYear'] = latest_year
                        logger.info(f"Using detected year pattern: {self.year_pattern}, latest year: {latest_year}")
                    else:
                        logger.warning("No numeric columns found")
                        return {}
                else:
                    logger.warning("No year pattern detected and no valid year columns")
                    return {}
            else:
                # Use actual year columns
                latest_col, latest_year = max(year_cols, key=lambda x: x[1])
                extracted_data['ReportYear'] = latest_year
                logger.info(f"Found latest year: {latest_year} in column {latest_col}")

        # Rest of your existing code for extracting metrics...

            # Log DataFrame info for debugging
            logger.info(f"Processing DataFrame columns: {df.columns.tolist()}")
            logger.info("First few rows:")
            logger.info(df.head(2))

            # Handle special characters in numeric values
            def clean_numeric(val):
                if isinstance(val, str):
                    # Remove special characters like †, ‡, §, ¶, b
                    val = re.sub(r'[†‡§¶b]', '', val)
                    # Remove commas and spaces
                    val = val.replace(',', '').strip()
                return val

            # For each metric, look for rows that contain the keyword   
            for metric_name, keywords in self.metrics.items():
                try:
                    matching_rows = df[df.iloc[:, 0].str.contains('|'.join(keywords), 
                                                                na=False, case=False)]
                    
                    if not matching_rows.empty:
                        # Special handling for water usage
                        if metric_name == 'WaterUsage':
                            water_rows = df[df.iloc[:, 0].str.contains(
                                'water consumption|total water|water usage|water withdrawal', 
                                case=False, 
                                na=False
                            )]
                            if not water_rows.empty:
                                value_str = clean_numeric(str(water_rows.iloc[0][latest_col]))
                        else:
                            value_str = clean_numeric(str(matching_rows.iloc[0][latest_col]))

                        try:
                            if value_str and value_str not in ['-', '', 'nan']:
                                value = float(value_str)
                                extracted_data[metric_name] = value
                                logger.info(f"Found {metric_name}: {value}")
                        except ValueError as e:
                            logger.warning(f"Error converting value '{value_str}' to float: {e}")
                            continue

                except Exception as e:
                    logger.warning(f"Error extracting {metric_name}: {e}")
                    continue

            # Enhanced employee count extraction
            try:
                # Look for exact match with 'Employees' first
                employee_rows = df[df.iloc[:, 0].str.lower() == 'employees']
                
                # If no exact match, then try the keyword list
                if employee_rows.empty:
                    employee_rows = df[df.iloc[:, 0].str.contains('|'.join(self.metrics['EmployeeCount']), 
                                                                na=False, case=False)]
                
                if not employee_rows.empty:
                    value_str = clean_numeric(str(employee_rows.iloc[0][latest_col]))
                    if value_str and value_str not in ['-', '', 'nan']:
                        value = float(value_str)
                        extracted_data['EmployeeCount'] = int(value)
                        logger.info(f"Found Employee Count: {extracted_data['EmployeeCount']}")
            except Exception as e:
                logger.warning(f"Error extracting employee count: {e}")

            # Look for energy consumption
            try:
                # First try exact match for "Energy used"
                energy_rows = df[df.iloc[:, 0].str.lower() == 'energy used']
                
                # If no exact match, then try the keyword list
                if energy_rows.empty:
                    energy_rows = df[df.iloc[:, 0].str.contains('|'.join(self.metrics['EnergyConsumption']), 
                                                            na=False, case=False)]
                
                if not energy_rows.empty:
                    value_str = clean_numeric(str(energy_rows.iloc[0][latest_col]))
                    if value_str and value_str not in ['-', '', 'nan']:
                        value = float(value_str)
                        extracted_data['EnergyConsumption'] = value
                        logger.info(f"Found Energy Consumption: {extracted_data['EnergyConsumption']}")
            except Exception as e:
                logger.warning(f"Error extracting energy consumption: {e}")

            # Enhanced GHG emissions extraction
            try:
                ghg_rows = df[df.iloc[:, 0].str.contains('|'.join(self.metrics['GHGEmissions']), 
                                                    na=False, case=False)]
                if not ghg_rows.empty:
                    # Look specifically for Scope 1+2 total
                    scope12_rows = ghg_rows[ghg_rows.iloc[:, 0].str.contains(
                        'scope 1 and 2|total emissions', 
                        case=False, 
                        na=False
                    )]
                    if not scope12_rows.empty:
                        value_str = clean_numeric(str(scope12_rows.iloc[0][latest_col]))
                        if value_str and value_str not in ['-', '', 'nan']:
                            value = float(value_str)
                            extracted_data['GHGEmissions'] = value
                            logger.info(f"Found GHG Emissions: {extracted_data['GHGEmissions']}")
            except Exception as e:
                logger.warning(f"Error extracting GHG emissions: {e}")

            # Enhanced water usage extraction
            try:
                water_rows = df[df.iloc[:, 0].str.contains('|'.join(self.metrics['WaterUsage']), 
                                                        na=False, case=False)]
                if not water_rows.empty:
                    value_str = clean_numeric(str(water_rows.iloc[0][latest_col]))
                    if value_str and value_str not in ['-', '', 'nan']:
                        value = float(value_str)
                        # Convert million liters to cubic meters
                        if 'million' in str(water_rows.iloc[0, 0]).lower():
                            value *= 1000
                        extracted_data['WaterUsage'] = value
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
                        value_str = clean_numeric(str(row[latest_col]))
                        try:
                            if value_str and value_str not in ['-', '', 'nan']:
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
                    value_str = clean_numeric(str(renewable_rows.iloc[0][latest_col]))
                    if value_str and value_str not in ['-', '', 'nan']:
                        value = float(value_str)
                        extracted_data['RenewableEnergyUse'] = value
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