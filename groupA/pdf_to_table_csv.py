import pandas as pd
from gmft.auto import CroppedTable, AutoTableDetector, AutoTableFormatter
from gmft.pdf_bindings import PyPDFium2Document
import os

# Initialize table detector and formatter
detector = AutoTableDetector()
formatter = AutoTableFormatter()

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
    
    return tables, doc, pages  # Return page references

# Extract tables
pdf_path = "../ESG_reports/Apple ESG 2024.pdf"
output_dir = "../labeled_files/apple/"  # Output folder
os.makedirs(output_dir, exist_ok=True)  # Create output folder if it doesn't exist

tables, doc, pages = ingest_pdf(pdf_path)

# Iterate over each table and save as CSV
for i, table in enumerate(tables):
    print(f"\n--- Table {i + 1} ---")
    
    # Ensure CroppedTable has a valid page reference
    if hasattr(table, 'page') and table.page is not None:
        try:
            formatted_table = formatter.format(table)  # Convert CroppedTable to FormattedTable
            df = formatted_table.df()  # Export as Pandas DataFrame
            
            # Replace empty values with 'N/A' to enhance readability
            df.fillna('N/A', inplace=True)

            # Construct CSV file name
            csv_filename = os.path.join(output_dir, f"table_{i + 1}.csv")

            # Save DataFrame to CSV
            df.to_csv(csv_filename, index=False, encoding='utf-8-sig')  # Save as CSV without index
            
            print(f"Table {i + 1} saved to {csv_filename}")
        
        except Exception as e:
            print(f"Error processing table {i + 1}: {e}")
    else:
        print(f"Table {i + 1} has no valid page reference.")

print("All tables saved as CSV files.")

# Close the document after processing all tables
doc.close()
