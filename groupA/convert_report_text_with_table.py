import PyPDF2
import nltk
import re
import ssl
import os
import pandas as pd
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from gmft.auto import CroppedTable, AutoTableDetector, AutoTableFormatter
from gmft.pdf_bindings import PyPDFium2Document

# SSL workaround
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

# Initialize table detector and formatter with improved parameters
detector = AutoTableDetector()
detector.min_columns = 2  # Minimum number of columns to consider as table
detector.min_rows = 2     # Minimum number of rows
detector.line_scale = 15  # Adjust line detection sensitivity
detector.cell_thresh = 0.3  # Cell detection threshold

formatter = AutoTableFormatter()

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file."""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def clean_text(text):
    """Clean the text while preserving numbers, important punctuation, and potential table structures."""
    text = re.sub(r'(?<!\n)[ \t]+(?!\n)', ' ', text)
    text = re.sub(r'[^\w\s.,%()-]', '', text)
    text = re.sub(r'\s([.,%)-])', r'\1', text)
    text = re.sub(r'([,.])\s*([^\d])', r'\1 \2', text)
    return text.strip()

def tokenize_text(text):
    """Tokenize the text into sentences and words, preserving numbers with decimal points."""
    sentences = sent_tokenize(text)
    tokenized_sentences = []
    for sentence in sentences:
        sentence = re.sub(r'(\d+)\.(\d+)', r'\1DECIMAL\2', sentence)
        tokens = word_tokenize(sentence)
        tokens = [token.replace('DECIMAL', '.') for token in tokens]
        tokenized_sentences.append(tokens)
    return tokenized_sentences

def remove_stopwords(tokens):
    """Remove stopwords from the list of tokens."""
    stop_words = set(stopwords.words('english'))
    return [token for token in tokens if token not in stop_words]

def lemmatize_tokens(tokens):
    """Lemmatize the tokens."""
    lemmatizer = WordNetLemmatizer()
    return [lemmatizer.lemmatize(token) for token in tokens]

def preprocess_text(text):
    """Preprocess the text: clean, tokenize, remove stopwords, and lemmatize."""
    cleaned_text = clean_text(text)
    tokenized_sentences = tokenize_text(cleaned_text)
    processed_sentences = []
    for sentence_tokens in tokenized_sentences:
        filtered_tokens = remove_stopwords(sentence_tokens)
        lemmatized_tokens = lemmatize_tokens(filtered_tokens)
        processed_sentences.append(lemmatized_tokens)
    return processed_sentences

def format_for_ai(processed_sentences):
    """Format the preprocessed text for AI model input."""
    formatted_text = ""
    for sentence in processed_sentences:
        formatted_text += " ".join(sentence) + "\n"
    return formatted_text.strip()

def extract_tables_from_pdf(pdf_path):
    """Extract tables from PDF file."""
    doc = PyPDFium2Document(pdf_path)
    tables = []
    pages = []

    # Configure detector
    detector.min_columns = 2
    detector.min_rows = 2

    for page in doc:
        pages.append(page)
        detected_tables = detector.extract(page)
        if detected_tables:
            tables.extend(detected_tables)
    
    return tables, doc, pages

def format_table(table, table_number):
    """Format table with basic structure."""
    try:
        if hasattr(table, 'page') and table.page is not None:
            # Format table
            formatted_table = formatter.format(table)
            df = formatted_table.df()
            
            # Basic cleaning
            df = df.fillna('N/A')
            
            # Clean column names
            df.columns = [str(col).strip().replace('\n', ' ') for col in df.columns]
            
            # Format table text
            separator = "=" * 80
            title = f"Table {table_number}"
            
            # Convert DataFrame to string with basic formatting
            table_text = f"{separator}\n{title}\n{separator}\n"
            table_text += df.to_string(index=False, justify='left')
            table_text += f"\n{separator}\n\n"
            
            return table_text
        else:
            return f"Table {table_number} has no valid page reference.\n\n"
    except Exception as e:
        return f"Error processing Table {table_number}: {str(e)}\n\n"

def process_pdf(pdf_path):
    """Process PDF: extract text, tables, and combine them."""
    # Extract and process text
    raw_text = extract_text_from_pdf(pdf_path)
    cleaned_text = clean_text(raw_text)
    processed_text = preprocess_text(cleaned_text)
    formatted_text = format_for_ai(processed_text)

    # Extract and format tables
    tables, doc, pages = extract_tables_from_pdf(pdf_path)
    formatted_tables = "EXTRACTED TABLES:\n\n"
    for i, table in enumerate(tables):
        formatted_tables += format_table(table, i+1)

    # Close the document after processing
    doc.close()

    # Combine processed text and tables
    combined_content = f"{formatted_text}\n\nEXTRACTED TABLES:\n\n{formatted_tables}"
    return combined_content

if __name__ == "__main__":
    pdf_path = "../ESG_reports/apple.pdf"
    combined_content = process_pdf(pdf_path)
    
    # Create txt_files directory if it doesn't exist
    os.makedirs("../txt_files", exist_ok=True)
    
    # Save the combined data to a txt file
    output_file = "../txt_files/apple_combined.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(combined_content)
    
    print(f"\nCombined processed text and tables saved to: {output_file}")
