import os
import re
import logging
import pandas as pd
import numpy as np
import torch
from fuzzywuzzy import process
import platform

# Update imports to use recommended paths
from gmft.detectors.tatr import TATRTableDetectorConfig
from gmft.formatters.tatr import TATRFormatConfig
from gmft.auto import AutoTableDetector, AutoTableFormatter
from gmft.pdf_bindings import PyPDFium2Document

# Configure logging with more detailed format
logging.basicConfig(
    filename='table_extraction.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_device():
    """
    Automatically detect and return the best available device
    Returns: str - 'mps', 'cuda', or 'cpu'
    """
    # Print detailed system information
    print("\nSystem Information:")
    print("-" * 50)
    print(f"Python Version: {platform.python_version()}")
    print(f"PyTorch Version: {torch.__version__}")
    
    # Check if running on macOS with Apple Silicon
    if platform.system() == "Darwin" and platform.processor() == "arm":
        mps_available = torch.backends.mps.is_available()
        mps_built = torch.backends.mps.is_built()
        print("\nApple Silicon Information:")
        print(f"MPS Built: {mps_built}")
        print(f"MPS Available: {mps_available}")
        
        if mps_available:
            print("→ Using Apple M-series GPU (MPS)")
            return 'mps'
    
    # Check CUDA availability
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

# Get the best available device
print("\nDetecting available devices...")
device = get_device()
print(f"\nSelected Device: {device}")
print("-" * 50 + "\n")

# Create detector and formatter configurations
detector_config = TATRTableDetectorConfig(
    detector_base_threshold=0.7,
    torch_device=device
)

formatter_config = TATRFormatConfig(
    formatter_base_threshold=0.7,  # Base threshold for table feature confidence
    image_processor_path='microsoft/table-transformer-detection',
    formatter_path='microsoft/table-transformer-structure-recognition',
    no_timm=True,
    torch_device=device,  # Use detected device
    verbosity=1,
    remove_null_rows=True,
    enable_multi_header=False,
    semantic_spanning_cells=False,
    large_table_threshold=10,
    large_table_row_overlap_threshold=0.2,
    large_table_maximum_rows=1000
)

# Initialize detector and formatter with configurations
detector = AutoTableDetector(config=detector_config)
formatter = AutoTableFormatter(config=formatter_config)

# Print device information at startup
logging.info(f"""
Device Information:
------------------
PyTorch Version: {torch.__version__}
System: {platform.system()}
Processor: {platform.processor()}
CUDA Available: {torch.cuda.is_available()}
MPS Available: {torch.backends.mps.is_available() if hasattr(torch.backends, 'mps') else False}
Selected Device: {device}
""")

def normalize_headers(df):
    standard_columns = {
        'EnergyConsumption(MWh)': ['energy consumption', 'total energy use', 'energy use', 'energy consumption (mwh)'],
        'GHG Emissions(tonne (Mt) of CO2e)': ['ghg emissions', 'emissions', 'co2 emissions', 'carbon emissions'],
        'WaterUsage(tonne (Mt))': ['water usage', 'water use', 'water consumption'],
        'WasteGenerated (tonne)': ['waste generated', 'waste', 'waste production'],
        'RenewableEnergyUse (MWh)': ['renewable energy use', 'renewable energy', 'renewable (%)', 'percent renewable energy']
    }

    all_variations = {var.lower(): key for key, vars in standard_columns.items() for var in vars}

    new_columns = []
    for col in df.columns:
        col_clean = re.sub(r'[^a-zA-Z0-9\s%]', '', col.lower())
        col_clean = col_clean.strip()
        match, score = process.extractOne(col_clean, all_variations.keys())
        if score >= 80:
            new_columns.append(all_variations[match])
        else:
            new_columns.append(col)
    df.columns = new_columns
    return df

def clean_dataframe(df):
    df = df.dropna(axis=0, how='all')
    df = df.dropna(axis=1, how='all')
    df = df.reset_index(drop=True)
    return df

def check_numeric_content(df):
    numeric_cols = df.apply(lambda s: pd.to_numeric(s, errors='coerce').notnull().mean() > 0.5)
    return numeric_cols.any()

def contains_year(df):
    """Check if the DataFrame contains any year values."""
    year_pattern = r'\b(19|20)\d{2}\b'
    
    # Replace applymap with map for each column
    has_year = any(
        df[col].map(lambda x: bool(re.search(year_pattern, str(x)))).any()
        for col in df.columns
    )
    
    return has_year

def validate_data(df):
    # Implement data validation logic as needed
    return True

def process_complex_table(table):
    formatted_table = formatter.format(table)
    df = formatted_table.df()
    # If the table has multi-level headers, flatten them
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [' '.join(col).strip() for col in df.columns.values]
    return df

def ingest_pdf(pdf_path):
    doc = PyPDFium2Document(pdf_path)
    tables = []
    pages = []

    for page_number, page in enumerate(doc):
        pages.append(page)
        detected_tables = detector.detect(page)
        if detected_tables:
            for table in detected_tables:
                table.page_number = page_number  # Keep track of page number if needed
            tables.extend(detected_tables)

    return tables, doc, pages

def process_tables(pdf_path, output_dir):
    try:
        os.makedirs(output_dir, exist_ok=True)
        tables, doc, pages = ingest_pdf(pdf_path)
        valid_table_count = 0

        for i, table in enumerate(tables):
            logging.info(f"Processing Table {i + 1}")

            try:
                df = process_complex_table(table)
                df = clean_dataframe(df)
                df = normalize_headers(df)

                if check_numeric_content(df) and contains_year(df) and validate_data(df):
                    valid_table_count += 1
                    csv_filename = os.path.join(output_dir, f"table_{valid_table_count}.csv")
                    df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
                    logging.info(f"Table {i + 1} saved as table_{valid_table_count}.csv")
                else:
                    logging.warning(f"Table {i + 1} rejected: Does not meet criteria")

            except Exception as e:
                logging.error(f"Error processing table {i + 1}: {str(e)}")

        logging.info(f"Processing complete. {valid_table_count} valid tables saved.")
        return valid_table_count

    except Exception as e:
        logging.error(f"Error processing PDF: {str(e)}")
        return 0
    finally:
        if 'doc' in locals():
            doc.close()

def convert_pdf_to_csv(pdf_path: str, output_dir: str) -> dict:
    try:
        valid_tables = process_tables(pdf_path, output_dir)

        return {
            "status": "success",
            "message": f"Successfully processed {valid_tables} tables with year information",
            "tables_processed": valid_tables,
            "output_directory": output_dir
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error processing PDF: {str(e)}",
            "tables_processed": 0,
            "output_directory": output_dir
        }

if __name__ == "__main__":
    pdf_path = "../ESG_reports/samsung.pdf"
    output_dir = "../labeled_files/samsung/"

    result = convert_pdf_to_csv(pdf_path, output_dir)
    print(result)