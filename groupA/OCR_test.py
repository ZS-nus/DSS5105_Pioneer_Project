import os
import fitz  # PyMuPDF
from PIL import Image, ImageEnhance, ImageFilter
import easyocr
import pdfplumber
import re
import ssl

# Disable SSL verification (not recommended for production)
ssl._create_default_https_context = ssl._create_unverified_context

def preprocess_image(image):
    """Preprocess the image to improve OCR accuracy."""
    # Convert to grayscale
    image = image.convert('L')
    # Increase contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)
    # Apply a filter to remove noise
    image = image.filter(ImageFilter.MedianFilter())
    return image

def filter_text(text):
    """Filter out headers, footers, and page numbers from the text."""
    # Define patterns for headers, footers, and page numbers
    header_footer_pattern = re.compile(r'^(Header|Footer|Page \d+)', re.IGNORECASE)
    
    # Split text into lines and filter out unwanted lines
    filtered_lines = []
    for line in text.split('\n'):
        if not header_footer_pattern.match(line.strip()):
            filtered_lines.append(line)
    
    return '\n'.join(filtered_lines)

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file using OCR and layout detection."""
    print("Initializing easyocr reader...")
    reader = easyocr.Reader(['en'])  # Initialize the easyocr reader with English language
    print("Reader initialized.")
    
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            print(f"Processing page {page_num + 1}/{len(pdf.pages)}...")
            # Extract text using pdfplumber
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
            else:
                # If no text is found, perform OCR
                page_image = page.to_image()
                image = page_image.original
                image = preprocess_image(image)
                image.save("temp_image.png")  # Save the image temporarily
                result = reader.readtext("temp_image.png", detail=0)  # Perform OCR
                text += " ".join(result) + "\n"
                os.remove("temp_image.png")  # Remove the temporary image file
    
    # Filter out headers, footers, and page numbers
    filtered_text = filter_text(text)
    print("OCR processing complete.")
    return filtered_text

def save_as_markdown(text, output_file, output_dir="."):
    """Save the extracted text as a markdown file in the specified directory."""
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Full path for the output file
    output_file_path = os.path.join(output_dir, output_file)
    
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Text saved as markdown in {output_file_path}")

if __name__ == "__main__":
    # Example usage
    pdf_path = "../ESG_reports/apple.pdf"
    print(f"Extracting text from {pdf_path}...")
    text = extract_text_from_pdf(pdf_path)
    output_md = "apple.md"
    output_dir = "../ESG_reports"  # Directory to save the markdown file
    save_as_markdown(text, output_md, output_dir)
    print("Process completed.")