import os
import fitz  # PyMuPDF
from PIL import Image, ImageEnhance, ImageFilter
import easyocr
import pdfplumber
import re
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import logging
import csv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Disable SSL verification (not recommended for production)
ssl._create_default_https_context = ssl._create_unverified_context

def preprocess_image(image):
    """Preprocess the image to improve OCR accuracy."""
    image = image.convert('L')
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)
    image = image.filter(ImageFilter.MedianFilter())
    return image

def filter_text(text):
    """Filter out headers, footers, and page numbers from the text."""
    header_footer_pattern = re.compile(r'^(Header|Footer|Page \d+)', re.IGNORECASE)
    filtered_lines = [line for line in text.split('\n') if not header_footer_pattern.match(line.strip())]
    return '\n'.join(filtered_lines)

def extract_table_from_page(page):
    """Extract tables from a page using pdfplumber."""
    try:
        tables = page.extract_tables()
        table_data = []
        for table in tables:
            for row in table:
                table_data.append(row)
        return table_data
    except Exception as e:
        logging.error(f"Error extracting table from page: {e}")
        return []

def extract_text_from_page(page, reader):
    """Extract text from a single page."""
    try:
        page_text = page.extract_text()
        if page_text:
            return page_text
        else:
            page_image = page.to_image()
            image = preprocess_image(page_image.original)
            image.save("temp_image.png")
            result = reader.readtext("temp_image.png", detail=0)
            os.remove("temp_image.png")
            return " ".join(result)
    except Exception as e:
        logging.error(f"Error processing page: {e}")
        return ""

def extract_text_from_pdf(pdf_path):
    """Extract text and tables from a PDF file."""
    logging.info("Initializing OCR readers...")
    easyocr_reader = easyocr.Reader(['en'])
    logging.info("Readers initialized.")
    
    text = ""
    tables = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            with ThreadPoolExecutor() as executor:
                futures = [executor.submit(process_page, page, easyocr_reader) for page in pdf.pages]
                for future in tqdm(as_completed(futures), total=len(pdf.pages), desc="Processing pages"):
                    try:
                        page_text, page_tables = future.result()
                        text += page_text + "\n"
                        if page_tables:
                            tables.extend(page_tables)
                    except Exception as e:
                        logging.error(f"Error processing future result: {e}")
    except Exception as e:
        logging.error(f"Error opening or processing PDF: {e}")
        return None, None

    filtered_text = filter_text(text)
    logging.info("PDF text and table extraction complete.")
    return filtered_text, tables

def process_page(page, reader):
    """Process a page, extracting text and tables."""
    try:
        page_text = extract_text_from_page(page, reader)
        page_tables = extract_table_from_page(page)
        return page_text, page_tables
    except Exception as e:
        logging.error(f"Error processing page: {e}")
        return "", []

def extract_company_name(text):
    """Extract company name from the text."""
    company_pattern = re.compile(r'((?:[A-Z][a-z.]+ )*(?:Inc\.|Corp\.|Ltd\.|LLC|Company))')
    match = company_pattern.search(text[:1000])
    return match.group(1) if match else "Unknown Company"

def save_as_markdown(text, output_file, output_dir="."):
    """Save the extracted text as a markdown file in the specified directory."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_file_path = os.path.join(output_dir, output_file)
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    logging.info(f"Text saved as markdown in {output_file_path}")

def save_tables_as_csv(tables, output_file, output_dir="."):
    """Save extracted tables as CSV files."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_file_path = os.path.join(output_dir, output_file)
    with open(output_file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for table in tables:
            writer.writerows(table)
    logging.info(f"Tables saved as CSV in {output_file_path}")

if __name__ == "__main__":
    pdf_path = "../../ESG_reports/apple.pdf"
    logging.info(f"Extracting text and tables from {pdf_path}...")
    text, tables = extract_text_from_pdf(pdf_path)
    if text:
        company_name = extract_company_name(text)
        output_md = f"{company_name}.md"
        output_dir = "../../md_files"
        save_as_markdown(text, output_md, output_dir)
        
        if tables:
            output_csv = f"{company_name}_tables.csv"
            save_tables_as_csv(tables, output_csv, output_dir)
        
        logging.info("Process completed.")
    else:
        logging.error("Failed to extract text from PDF.")