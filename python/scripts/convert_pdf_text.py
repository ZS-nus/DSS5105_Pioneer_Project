import PyPDF2
import nltk
import re
import ssl
import os
from pathlib import Path
import pandas as pd
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from gmft.auto import CroppedTable, AutoTableDetector, AutoTableFormatter
from gmft.pdf_bindings import PyPDFium2Document

# SSL and NLTK setup
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Download NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

# Initialize detectors
detector = AutoTableDetector()
detector.min_columns = 2
detector.min_rows = 2
detector.line_scale = 15
detector.cell_thresh = 0.3
formatter = AutoTableFormatter()

class PDFConverter:
    def __init__(self, storage_dir):
        self.storage_dir = Path(storage_dir)
        self.pdf_dir = self.storage_dir / "pdf_uploads"
        self.txt_dir = self.storage_dir / "txt_outputs"
        
        # Create directories if they don't exist
        self.pdf_dir.mkdir(parents=True, exist_ok=True)
        self.txt_dir.mkdir(parents=True, exist_ok=True)

    def save_uploaded_pdf(self, file_content: bytes, filename: str) -> str:
        """Save uploaded PDF file and return the path"""
        pdf_path = self.pdf_dir / filename
        with open(pdf_path, 'wb') as f:
            f.write(file_content)
        return str(pdf_path)

    def process_pdf(self, pdf_path: str, output_filename: str) -> dict:
        """Process PDF and return the file paths and status"""
        try:
            # Extract and process content
            combined_content = self._process_pdf_content(pdf_path)
            
            # Save to text file
            txt_path = self.txt_dir / output_filename
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(combined_content)
            
            return {
                "status": "success",
                "message": "PDF processed successfully",
                "pdf_path": str(pdf_path),
                "txt_path": str(txt_path)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error processing PDF: {str(e)}",
                "pdf_path": str(pdf_path),
                "txt_path": None
            }

    def _process_pdf_content(self, pdf_path):
        """Internal method to process PDF content"""
        # Extract and process text
        raw_text = self._extract_text_from_pdf(pdf_path)
        cleaned_text = self._clean_text(raw_text)
        processed_text = self._preprocess_text(cleaned_text)
        formatted_text = self._format_for_ai(processed_text)

        # Extract and format tables
        tables, doc, pages = self._extract_tables_from_pdf(pdf_path)
        formatted_tables = "EXTRACTED TABLES:\n\n"
        for i, table in enumerate(tables):
            formatted_tables += self._format_table(table, i+1)

        doc.close()
        return f"{formatted_text}\n\nEXTRACTED TABLES:\n\n{formatted_tables}"

    # ... [Keep all the helper methods from original convert_pdf_text.py, 
    #      but make them private by adding underscore prefix] ...