import os
import re
import logging
import pandas as pd
import numpy as np
import torch
from pathlib import Path
import platform
from fuzzywuzzy import process

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('pioneer_api')

# Update imports to use recommended paths
from gmft.detectors.tatr import TATRTableDetectorConfig
from gmft.formatters.tatr import TATRFormatConfig
from gmft.auto import AutoTableDetector, AutoTableFormatter
from gmft.pdf_bindings import PyPDFium2Document

# Add global configurations
detector_config = TATRTableDetectorConfig(
    detector_base_threshold=0.5,
    torch_device=None  # Will be set after device detection
)

formatter_config = TATRFormatConfig(
    formatter_base_threshold=0.3,
    image_processor_path='microsoft/table-transformer-detection',
    formatter_path='microsoft/table-transformer-structure-recognition',
    no_timm=True,
    torch_device=None,  # Will be set after device detection
    verbosity=1,
    remove_null_rows=True,
    enable_multi_header=False,
    semantic_spanning_cells=False,
    large_table_threshold=10,
    large_table_row_overlap_threshold=0.2,
    large_table_maximum_rows=1000
)

def get_device():
    """
    Automatically detect and return the best available device
    Returns: str - 'mps', 'cuda', or 'cpu'
    """
    print("\nSystem Information:")
    print("-" * 50)
    print(f"Python Version: {platform.python_version()}")
    print(f"PyTorch Version: {torch.__version__}")
    
    if platform.system() == "Darwin" and platform.processor() == "arm":
        mps_available = torch.backends.mps.is_available()
        mps_built = torch.backends.mps.is_built()
        print("\nApple Silicon Information:")
        print(f"MPS Built: {mps_built}")
        print(f"MPS Available: {mps_available}")
        
        if mps_available:
            print("→ Using Apple M-series GPU (MPS)")
            return 'mps'
    
    cuda_available = torch.cuda.is_available()
    print("\nCUDA Information:")
    print(f"CUDA Available: {cuda_available}")
    
    if cuda_available:
        print(f"CUDA Version: {torch.version.cuda}")
        print(f"GPU Device: {torch.cuda.get_device_name(0)}")
        print("→ Using CUDA GPU")
        return 'cuda'
    
    print("\n→ Using CPU")
    return 'cpu'

def check_numeric_content(df):
    """Enhanced check for numeric content"""
    try:
        def is_numeric(x):
            if pd.isna(x):
                return False
            try:
                # Remove common non-numeric characters
                clean_str = str(x).replace(',', '').replace('%', '').replace('$', '').strip()
                if clean_str.replace('.', '').replace('-', '').isdigit():
                    return True
                float(clean_str)
                return True
            except:
                return False

        # Skip first column (usually labels)
        data_cols = df.iloc[:, 1:] if df.shape[1] > 1 else df
        
        # Calculate numeric ratio
        total_cells = data_cols.size
        numeric_cells = sum(data_cols.applymap(is_numeric).sum())
        numeric_ratio = numeric_cells / total_cells if total_cells > 0 else 0
        
        # Check average text length in first column
        if df.shape[1] > 1:
            first_col = df.iloc[:, 0].astype(str)
            avg_text_length = sum(len(str(text)) for text in first_col) / len(first_col)
            has_long_text = avg_text_length > 100
        else:
            has_long_text = False
            avg_text_length = 0
        
        logger.info(f"Numeric ratio: {numeric_ratio:.2f}, Avg text length: {avg_text_length:.1f}")
        
        # Return True only if:
        # 1. High enough numeric ratio (>60%)
        # 2. No long narrative text
        # 3. At least 2 columns
        return numeric_ratio > 0.6 and not has_long_text and df.shape[1] >= 2
        
    except Exception as e:
        logger.error(f"Error checking numeric content: {str(e)}")
        return False

def process_complex_table(table, formatter):
    """Process complex table structure with enhanced validation"""
    try:
        formatted_table = formatter.format(table)
        df = pd.DataFrame(formatted_table.df())
        
        # Quick validation before proceeding
        if df.empty or df.shape[1] < 2:
            logger.info("Table rejected: Empty or too few columns")
            return None
            
        # Check if table appears to be narrative text
        first_col = df.iloc[:, 0].astype(str)
        avg_text_length = sum(len(str(text)) for text in first_col) / len(first_col)
        if avg_text_length > 100:
            logger.info("Table rejected: Contains long narrative text")
            return None
        
        return df
        
    except Exception as e:
        logger.error(f"Error formatting table: {str(e)}")
        return None

def clean_dataframe(df):
    """Clean and preprocess dataframe"""
    # Drop empty rows and columns
    df = df.dropna(how='all')
    df = df.dropna(axis=1, how='all')
    
    # Handle MultiIndex columns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [' '.join(col).strip() for col in df.columns.values]
    
    return df

def normalize_headers(df):
    """Normalize column headers"""
    standard_columns = {
        'EnergyConsumption(MWh)': ['energy consumption', 'total energy use', 'energy use', 'total', 'mwh'],
        'WaterUsage(cubic meters)': ['water usage', 'water use', 'water consumption', 'water metrics'],
        'WasteGenerated(tonne)': ['waste generated', 'waste', 'waste production'],
        'Year': ['year', 'fiscal year', 'fy', 'period'],
        'Metric': ['metric', 'category', 'indicators', 'unit']
    }
    
    fiscal_years = ['2023', '2022', '2021', '2020', '2019']
    for year in fiscal_years:
        standard_columns[f'FY{year}'] = [f'fy{year}', str(year), f'fiscal year {year}']
    
    all_variations = {var.lower(): key for key, vars in standard_columns.items() for var in vars}
    
    new_columns = []
    for col in df.columns:
        col_clean = str(col).lower().strip()
        if re.match(r'(fy)?\d{2,4}', col_clean):
            year_match = re.search(r'\d{2,4}', col_clean)
            if year_match:
                year = year_match.group()
                if len(year) == 2:
                    year = '20' + year
                new_columns.append(f'FY{year}')
            else:
                new_columns.append(col.upper())
        else:
            match, score = process.extractOne(col_clean, all_variations.keys())
            if score >= 80:
                new_columns.append(all_variations[match])
            else:
                new_columns.append(col)
    
    df.columns = new_columns
    return df

def handle_complex_table(df):
    """Handle complex table structures and try to fix common issues"""
    try:
        # Handle multi-level headers
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [' '.join(map(str, col)).strip() for col in df.columns.values]
        
        # Handle merged cells and hierarchical structure
        df = df.fillna(method='ffill')
        
        # Clean column names
        df.columns = [str(col).strip() for col in df.columns]
        
        # Handle hierarchical rows
        if 'Unit' in df.columns:
            hierarchy_cols = df.columns[0:df.columns.get_loc('Unit')]
            df[hierarchy_cols] = df[hierarchy_cols].fillna(method='ffill')
        
        # Remove completely empty rows and columns
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # Handle footnotes but preserve important notes
        df = df[~df.iloc[:, 0].astype(str).str.contains(r'^\s*[\*\†‡§]|^Note:', na=False)]
        
        return df
    except Exception as e:
        logger.error(f"Error handling complex table: {str(e)}")
        return df

def validate_data(df):
    """Enhanced validation of dataframe content"""
    try:
        # Check if dataframe is empty
        if df is None or df.empty:
            logger.info("Table rejected: Empty dataframe")
            return False
            
        # Check minimum size
        if len(df) < 2 or len(df.columns) < 2:
            logger.info("Table rejected: Too small (min 2 rows and columns required)")
            return False
            
        # Check if all columns are empty strings or NaN
        if all(df.columns.astype(str).str.strip() == ''):
            logger.info("Table rejected: Empty column headers")
            return False
            
        # Check for excessive missing values
        missing_ratio = df.isna().sum().sum() / (df.shape[0] * df.shape[1])
        if missing_ratio > 0.5:
            logger.info(f"Table rejected: Too many missing values ({missing_ratio:.2%})")
            return False
            
        # Check numeric content
        if not check_numeric_content(df):
            logger.info("Table rejected: Insufficient numeric content or contains long narrative text")
            return False
            
        # Check for either year information or relevant content
        if not (contains_year(df) or check_relevant_content(df)):
            logger.info("Table rejected: No year information or relevant content found")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Error validating data: {str(e)}")
        return False

def contains_year(df):
    """Enhanced year detection in both columns and content"""
    year_pattern = r'\b(19|20)\d{2}\b|FY\d{2,4}|\d{4}/\d{2,4}|20\d{2}-\d{2,4}|\'?\d{2}|\(\d{4}\)'
    
    def check_year(x):
        if pd.isna(x):
            return False
        x_str = str(x).upper()
        if 'FY' in x_str:
            return True
        if bool(re.search(year_pattern, x_str)):
            try:
                year = convert_year_format(x_str)
                return year is not None and 1900 <= year <= 2100
            except:
                return False
        return False

    # Check column names
    has_year_in_cols = any(check_year(col) for col in df.columns)
    
    # Check content
    if len(df) > 0:
        # Check all cells for year mentions
        has_year_in_data = any(
            df[col].astype(str).apply(check_year).any()
            for col in df.columns
        )
        
        # Check for year mentions in text content
        text_content = df.astype(str).values.flatten()
        years_in_text = [m.group() for text in text_content 
                        for m in re.finditer(year_pattern, str(text))]
        has_year_in_text = len(years_in_text) > 0
        
        logger.info(f"Year detection - Headers: {has_year_in_cols}, "
                   f"In data: {has_year_in_data}, "
                   f"In text: {has_year_in_text}")
        
        return has_year_in_cols or has_year_in_data or has_year_in_text
    
    return has_year_in_cols

def check_relevant_content(df):
    """Check if table contains relevant environmental/sustainability metrics"""
    relevant_keywords = {
        'energy': ['energy', 'electricity', 'power', 'mwh', 'kwh', 'consumption'],
        'emissions': ['ghg', 'emissions', 'carbon', 'co2', 'scope', 'mtco2e'],
        'water': ['water', 'effluent', 'discharge', 'withdrawal', 'consumption'],
        'waste': ['waste', 'recycling', 'landfill', 'hazardous', 'disposal'],
        'renewable': ['renewable', 'solar', 'wind', 'clean energy'],
        'environmental': ['environmental', 'sustainability', 'climate', 'footprint'],
        'employees': [
            'employees', 'workforce', 'headcount', 'staff', 'personnel',
            'full-time', 'part-time', 'fte', 'total employees',
            'permanent employees', 'temporary employees',
            'total workforce', 'global workforce', 'employee count'
        ]
    }
    
    # Convert all content to string and lowercase for searching
    content = df.astype(str).values.flatten()
    text_content = ' '.join(content).lower()
    
    # Check for keywords in content
    found_keywords = []
    for category, keywords in relevant_keywords.items():
        if any(keyword in text_content for keyword in keywords):
            found_keywords.append(category)
    
    if found_keywords:
        logger.info(f"Found relevant keywords: {found_keywords}")
        return True
    return False

def convert_year_format(year_str: str) -> int:
    """Convert various year formats to standard YYYY format"""
    try:
        year_str = str(year_str).strip().upper()
        
        if year_str.startswith('FY'):
            year_num = year_str[2:].split('/')[0]
            if len(year_num) == 2:
                return 2000 + int(year_num)
            return int(year_num)
            
        if '/' in year_str:
            return int(year_str.split('/')[0])
            
        if len(year_str) == 4:
            return int(year_str)
        if len(year_str) == 2:
            return 2000 + int(year_str)
            
        raise ValueError(f"Unrecognized year format: {year_str}")
        
    except Exception as e:
        logger.warning(f"Error converting year format '{year_str}': {str(e)}")
        return None

def ingest_pdf(pdf_path):
    """Updated PDF ingestion"""
    doc = PyPDFium2Document(pdf_path)
    tables = []
    pages = []

    for page_number, page in enumerate(doc):
        pages.append(page)
        detected_tables = detector.detect(page)
        if detected_tables:
            for table in detected_tables:
                table.page_number = page_number
            tables.extend(detected_tables)

    return tables, doc, pages

def process_pdf(pdf_path, output_dir):
    """Main function to process PDF and extract tables"""
    doc = None
    table_files = []
    
    try:
        logger.info(f"Processing PDF: {pdf_path}")
        os.makedirs(output_dir, exist_ok=True)
        
        device = get_device()
        detector_config.torch_device = device
        formatter_config.torch_device = device
        
        global detector, formatter
        detector = AutoTableDetector(config=detector_config)
        formatter = AutoTableFormatter(config=formatter_config)
        
        tables, doc, pages = ingest_pdf(pdf_path)
        valid_table_count = 0
        
        if not tables:
            logger.info("No tables found in the document")
            return {
                "status": "success",
                "message": "No tables found in the document",
                "table_count": 0,
                "table_files": []
            }
        
        for i, table in enumerate(tables):
            try:
                logger.info(f"\nProcessing Table {i + 1}")
                
                df = process_complex_table(table, formatter)
                if df is None:
                    logger.info(f"Table {i + 1} rejected: Could not format table")
                    continue
                
                logger.info(f"Raw table {i + 1} content:\n{df.head()}")
                logger.info(f"Columns: {df.columns.tolist()}")
                
                df = clean_dataframe(df)
                df = handle_complex_table(df)
                
                if df.empty:
                    logger.info(f"Table {i + 1} rejected: Empty after cleaning")
                    continue
                
                df = normalize_headers(df)
                
                if not validate_data(df):
                    logger.info(f"Table {i + 1} rejected: Failed validation")
                    continue
                
                has_year = contains_year(df)
                
                if has_year:
                    valid_table_count += 1
                    csv_filename = f"table_{valid_table_count}.csv"
                    csv_path = os.path.join(output_dir, csv_filename)
                    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                    
                    table_files.append({
                        "filename": csv_filename,
                        "path": csv_path,
                        "rows": len(df),
                        "columns": len(df.columns)
                    })
                    
                    logger.info(f"Saved table {valid_table_count} to {csv_filename}")
                else:
                    logger.info(f"Table {i + 1} rejected: No year information")
                
            except Exception as e:
                logger.error(f"Error processing table {i + 1}: {str(e)}")
                continue
        
        if valid_table_count == 0:
            return {
                "status": "success",
                "message": "No valid tables found after processing",
                "table_count": 0,
                "table_files": []
            }
        
        return {
            "status": "success",
            "message": f"Successfully processed {valid_table_count} valid tables",
            "table_count": valid_table_count,
            "table_files": table_files
        }
        
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        return {
            "status": "error",
            "message": f"Error processing PDF: {str(e)}",
            "table_count": 0,
            "table_files": []
        }
    finally:
        if doc:
            try:
                doc.close()
            except:
                pass

def convert_pdf_to_csv(pdf_path: str, output_dir: str) -> dict:
    """Wrapper function to process PDF and handle errors"""
    try:
        result = process_pdf(pdf_path, output_dir)
        if result["status"] == "error":
            return {
                "status": "error",
                "message": result["message"],
                "table_count": 0,
                "table_files": []
            }
        return result
    except Exception as e:
        logger.error(f"Error in convert_pdf_to_csv: {str(e)}")
        return {
            "status": "error",
            "message": f"Error processing PDF: {str(e)}",
            "table_count": 0,
            "table_files": []
        }

if __name__ == "__main__":
    pdf_path = "test.pdf"
    output_dir = "output"
    
    try:
        result = process_pdf(pdf_path, output_dir)
        print(result)
    except Exception as e:
        print(f"Error: {str(e)}")