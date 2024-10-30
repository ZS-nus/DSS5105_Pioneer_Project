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

class PDFConverter:
    def __init__(self, storage_dir):
        self.storage_dir = Path(storage_dir)
        self.pdf_dir = self.storage_dir / "pdf_uploads"
        self.txt_dir = self.storage_dir / "txt_outputs"
        
        # Create directories if they don't exist
        self.pdf_dir.mkdir(parents=True, exist_ok=True)
        self.txt_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize NLTK components
        self._setup_nltk()
        
        # Initialize table detectors
        self._setup_table_detector()

    def _setup_nltk(self):
        """Setup NLTK and SSL"""
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
        
        # Initialize NLTK components
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))

    def _setup_table_detector(self):
        """Setup table detection components"""
        self.detector = AutoTableDetector()
        self.detector.min_columns = 2
        self.detector.min_rows = 2
        self.detector.line_scale = 15
        self.detector.cell_thresh = 0.3
        self.formatter = AutoTableFormatter()

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

    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file."""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text

    def _clean_text(self, text: str) -> str:
        """Clean the text while preserving numbers, important punctuation, and potential table structures."""
        text = re.sub(r'(?<!\n)[ \t]+(?!\n)', ' ', text)
        text = re.sub(r'[^\w\s.,%()-]', '', text)
        text = re.sub(r'\s([.,%)-])', r'\1', text)
        text = re.sub(r'([,.])\s*([^\d])', r'\1 \2', text)
        return text.strip()

    def _tokenize_text(self, text: str) -> list:
        """Tokenize the text into sentences and words, preserving numbers with decimal points."""
        sentences = sent_tokenize(text)
        tokenized_sentences = []
        for sentence in sentences:
            sentence = re.sub(r'(\d+)\.(\d+)', r'\1DECIMAL\2', sentence)
            tokens = word_tokenize(sentence)
            tokens = [token.replace('DECIMAL', '.') for token in tokens]
            tokenized_sentences.append(tokens)
        return tokenized_sentences

    def _remove_stopwords(self, tokens: list) -> list:
        """Remove stopwords from the list of tokens."""
        return [token for token in tokens if token not in self.stop_words]

    def _lemmatize_tokens(self, tokens: list) -> list:
        """Lemmatize the tokens."""
        return [self.lemmatizer.lemmatize(token) for token in tokens]

    def _preprocess_text(self, text: str) -> list:
        """Preprocess the text: clean, tokenize, remove stopwords, and lemmatize."""
        cleaned_text = self._clean_text(text)
        tokenized_sentences = self._tokenize_text(cleaned_text)
        processed_sentences = []
        for sentence_tokens in tokenized_sentences:
            filtered_tokens = self._remove_stopwords(sentence_tokens)
            lemmatized_tokens = self._lemmatize_tokens(filtered_tokens)
            processed_sentences.append(lemmatized_tokens)
        return processed_sentences

    def _format_for_ai(self, processed_sentences: list) -> str:
        """Format the preprocessed text for AI model input."""
        formatted_text = ""
        for sentence in processed_sentences:
            formatted_text += " ".join(sentence) + "\n"
        return "EXTRACTED TEXT:\n\n" + formatted_text.strip()

    def _extract_tables_from_pdf(self, pdf_path: str):
        """Extract tables from PDF file."""
        doc = PyPDFium2Document(pdf_path)
        tables = []
        pages = [page for page in doc]
        
        for page in pages:
            detected = self.detector.detect(page)
            if detected:
                for table in detected:
                    formatted = self.formatter.format(table)
                    if formatted is not None:
                        tables.append(formatted)
        
        return tables, doc, pages

    def _format_table(self, table: CroppedTable, table_num: int) -> str:
        """Format table with basic structure."""
        try:
            df = pd.DataFrame(table.data)
            df = df.fillna('N/A')
            df.columns = [str(col).strip().replace('\n', ' ') for col in df.columns]
            
            separator = "=" * 80
            title = f"Table {table_num}"
            
            table_text = f"{separator}\n{title}\n{separator}\n"
            table_text += df.to_string(index=False, justify='left')
            table_text += f"\n{separator}\n\n"
            
            return table_text
        except Exception as e:
            return f"Error processing Table {table_num}: {str(e)}\n\n"

    def _process_pdf_content(self, pdf_path: str) -> str:
        """Process PDF content: extract text, tables, and combine them."""
        # Extract and process text
        raw_text = self._extract_text_from_pdf(pdf_path)
        processed_text = self._preprocess_text(raw_text)
        formatted_text = self._format_for_ai(processed_text)

        # Extract and format tables
        tables, doc, pages = self._extract_tables_from_pdf(pdf_path)
        formatted_tables = ""
        for i, table in enumerate(tables):
            formatted_tables += self._format_table(table, i+1)

        # Close the document after processing
        doc.close()

        # Combine processed text and tables
        return f"{formatted_text}\n\n{formatted_tables}"