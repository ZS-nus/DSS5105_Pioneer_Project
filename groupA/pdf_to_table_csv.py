import pandas as pd
import re
import numpy as np
from gmft.auto import CroppedTable, AutoTableDetector, AutoTableFormatter
from gmft.pdf_bindings import PyPDFium2Document
import os

# Initialize table detector and formatter
detector = AutoTableDetector()
formatter = AutoTableFormatter()

def is_numeric_string(s):
    """Check if a string contains numeric data"""
    # Remove common number formatting characters
    s = str(s).replace(',', '').replace('%', '').replace('$', '')
    s = s.strip()
    
    # Check if it's a number or contains numbers with units
    try:
        float(s.split()[0])  # Try to convert first word to float
        return True
    except:
        return False

def check_numeric_content(df):
    """
    Check if the DataFrame contains sufficient numeric data
    Returns True if at least 50% of non-header cells contain numbers
    """
    # Skip the header row
    if len(df) <= 1:  # If DataFrame has only header or is empty
        return False
    
    data_rows = df.iloc[1:]  # Get all rows except header
    total_cells = data_rows.size
    numeric_count = 0
    
    # Count cells containing numbers
    for column in data_rows.columns:
        numeric_count += sum(data_rows[column].apply(is_numeric_string))
    
    numeric_percentage = numeric_count / total_cells
    return numeric_percentage >= 0.5

def contains_year(df):
    """
    Enhanced check for valid year information and table structure
    Returns True only if the table contains valid year data and proper structure
    """
    # Check if DataFrame is empty or has weird structure
    if df.empty or len(df.columns) < 2:
        return False

    # Convert DataFrame to string to search for years
    df_str = df.to_string().lower()
    
    # More specific year patterns
    year_patterns = [
        r'\b(19|20)\d{2}\b',  # Match years 1900-2099
        r'\bfy\s?(19|20)\d{2}\b',  # Match FY2020, FY 2020
        r'\b(19|20)\d{2}[-/](19|20)\d{2}\b',  # Match year ranges like 2020-2021
    ]
    
    # Check for valid year patterns
    has_year = any(re.search(pattern, df_str) for pattern in year_patterns)
    
    # Additional table structure validation
    def is_valid_table_structure(df):
        # Check if table has reasonable dimensions
        if len(df) < 2 or len(df.columns) < 2:
            return False
            
        # Check if most cells contain actual data (not N/A or empty)
        non_empty_cells = df.notna().sum().sum()
        total_cells = df.size
        if non_empty_cells / total_cells < 0.5:  # At least 50% cells should have data
            return False
            
        # Check if column headers make sense
        headers = [str(col).lower() for col in df.columns]
        if all(len(str(header)) < 2 for header in headers):  # Headers should be meaningful
            return False
            
        return True

    return has_year and is_valid_table_structure(df)

def ingest_pdf(pdf_path):
    """ Extract tables from PDF file and return list of tables """
    doc = PyPDFium2Document(pdf_path)  # Open PDF document
    tables = []
    pages = []  # Keep references to page objects

    for page in doc:  # Iterate through each page
        pages.append(page)  # Keep reference to page object
        detected_tables = detector.extract(page)
        if detected_tables:
            tables.extend(detected_tables)
    
    return tables, doc, pages

def process_tables(pdf_path, output_dir):
    """Process PDF tables and save relevant ones to CSV"""
    try:
        os.makedirs(output_dir, exist_ok=True)
        tables, doc, pages = ingest_pdf(pdf_path)
        valid_table_count = 0
        
        for i, table in enumerate(tables):
            print(f"\nProcessing Table {i + 1}...")
            
            if not (hasattr(table, 'page') and table.page is not None):
                print(f"Table {i + 1} has no valid page reference - Skipping")
                continue
                
            try:
                formatted_table = formatter.format(table)
                df = formatted_table.df()
                
                # Additional preprocessing
                df = df.replace('', pd.NA).replace('N/A', pd.NA)  # Standardize empty values
                df = df.dropna(how='all')  # Drop completely empty rows
                df = df.dropna(axis=1, how='all')  # Drop completely empty columns
                
                # Check numeric content
                if not check_numeric_content(df):
                    print(f"Table {i + 1} rejected: Insufficient numeric data")
                    continue
                
                # Apply more stringent validation
                if not contains_year(df):
                    print(f"Table {i + 1} rejected: No valid year information or invalid structure")
                    continue
                
                # Further clean the table
                df = df.fillna('N/A')  # Fill remaining NA values
                
                # Save only if table looks valid
                if len(df.columns) >= 2 and len(df) >= 2:
                    valid_table_count += 1
                    csv_filename = os.path.join(output_dir, f"table_{valid_table_count}.csv")
                    df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
                    print(f"Table {i + 1} saved as table_{valid_table_count}.csv")
                else:
                    print(f"Table {i + 1} rejected: Invalid structure")
                
            except Exception as e:
                print(f"Error processing table {i + 1}: {str(e)}")
        
        print(f"\nProcessing complete. {valid_table_count} valid tables saved.")
        return valid_table_count
        
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return 0
    finally:
        if 'doc' in locals():
            doc.close()

def convert_pdf_to_csv(pdf_path: str, output_dir: str) -> dict:
    """
    Convert PDF tables to CSV files and return processing results
    """
    try:
        # Process the PDF and save tables
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
    # Example usage
    pdf_path = "../ESG_reports/apple.pdf"
    output_dir = "../labeled_files/apple/"
    
    result = convert_pdf_to_csv(pdf_path, output_dir)
    print(result)