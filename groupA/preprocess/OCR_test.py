import os
import fitz  # PyMuPDF
from PIL import Image, ImageEnhance, ImageFilter
import easyocr
import pdfplumber
import re
import ssl
import logging

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

def extract_text_from_page(page, reader):
    """Extract text from a single page."""
    try:
        page_text = page.extract_text()
        if page_text:
            return page_text
        else:
            # If no text is extracted, use OCR
            page_image = page.to_image()
            image = preprocess_image(page_image.original)
            image.save("temp_image.png")
            result = reader.readtext("temp_image.png", detail=0)
            os.remove("temp_image.png")
            return " ".join(result)
    except Exception as e:
        logging.error(f"Error processing page: {e}")
        logging.error(f"Page content type: {type(page)}")
        logging.error(f"Page content: {page}")
        return ""

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    logging.info("Initializing OCR reader...")
    easyocr_reader = easyocr.Reader(['en'])
    logging.info("Reader initialized.")
    
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                logging.info(f"Processing page {page_num + 1}/{len(pdf.pages)}")
                page_text = extract_text_from_page(page, easyocr_reader)
                if page_text:
                    filtered_text = filter_text(page_text)
                    text += filtered_text + "\n\n"  # Add extra newline between pages
    except Exception as e:
        logging.error(f"Error processing PDF: {e}")
    
    return text

def detect_company_name(text):
    """Detect the company name from the extracted text."""
    # This is a simple implementation. You might want to improve this
    # based on the structure of your ESG reports.
    first_line = text.split('\n')[0]
    company_name = first_line.strip()
    return company_name if company_name else "Unknown Company"

if __name__ == "__main__":
    pdf_path = "../../ESG_reports/xiaomi.pdf"
    text = extract_text_from_pdf(pdf_path)
    if text:
        company_name = detect_company_name(text)
        output_file = f"../../md_files/xiaomi_2.md"
        
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, "w", encoding='utf-8') as f:
            f.write(text)
        logging.info(f"Text saved as markdown in {output_file}")
    logging.info("Process completed.")