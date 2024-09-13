import fitz  # PyMuPDF
from PIL import Image
import pytesseract

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file using OCR."""
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        text += pytesseract.image_to_string(image)
    return text

def save_as_markdown(text, output_file):
    """Save the extracted text as a markdown file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text)

if __name__ == "__main__":
    # Example usage
    pdf_path = "../ESG_reports/Apple_ESG_2024.pdf"
    text = extract_text_from_pdf(pdf_path)
    output_md = "output.md"
    save_as_markdown(text, output_md)