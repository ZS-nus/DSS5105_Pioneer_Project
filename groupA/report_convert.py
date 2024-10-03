import PyPDF2
import nltk
import re
import ssl
import os
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

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
    # Replace multiple spaces with a single space, except for potential table rows
    text = re.sub(r'(?<!\n)[ \t]+(?!\n)', ' ', text)
    
    # Remove special characters except dots in numbers, commas, and some punctuation
    text = re.sub(r'[^\w\s.,%()-]', '', text)
    
    # Remove spaces before punctuation
    text = re.sub(r'\s([.,%)-])', r'\1', text)
    
    # Ensure there's a space after commas and dots not in numbers
    text = re.sub(r'([,.])\s*([^\d])', r'\1 \2', text)
    
    return text.strip()

def tokenize_text(text):
    """Tokenize the text into sentences and words, preserving numbers with decimal points."""
    sentences = sent_tokenize(text)
    tokenized_sentences = []
    for sentence in sentences:
        # Temporarily replace decimal points in numbers with a placeholder
        sentence = re.sub(r'(\d+)\.(\d+)', r'\1DECIMAL\2', sentence)
        tokens = word_tokenize(sentence)
        # Restore decimal points
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

def detect_and_format_tables(text):
    """Detect potential table rows and format them."""
    lines = text.split('\n')
    formatted_lines = []
    in_table = False
    table_header = False
    
    for line in lines:
        # Detect if the line looks like a table row (contains year and multiple numbers)
        if re.search(r'\b(FY\s*\d{4}|\d{4})\b.*\b\d+([.,]\d+)?\b.*\b\d+([.,]\d+)?\b', line):
            if not in_table:
                formatted_lines.append("\n| Year | Value 1 | Value 2 | Value 3 | Value 4 | Value 5 |")
                formatted_lines.append("|------|--------|--------|--------|--------|--------|")
                in_table = True
            formatted_lines.append("| " + " | ".join(line.split()) + " |")
        else:
            if in_table:
                formatted_lines.append("")  # Add a blank line after table
                in_table = False
            formatted_lines.append(line)
    
    return "\n".join(formatted_lines)

def format_for_ai(processed_sentences):
    """Format the preprocessed text for AI model input, preserving some structure."""
    formatted_text = ""
    for sentence in processed_sentences:
        formatted_text += " ".join(sentence) + "\n"
    
    # Detect and format tables
    formatted_text = detect_and_format_tables(formatted_text)
    
    return formatted_text.strip()

def extract_and_preprocess_esg_data(pdf_path):
    """Main function to extract and preprocess ESG data from PDF."""
    raw_text = extract_text_from_pdf(pdf_path)
    cleaned_text = clean_text(raw_text)
    processed_text = preprocess_text(cleaned_text)
    formatted_text = format_for_ai(processed_text)
    return formatted_text

if __name__ == "__main__":
    pdf_path = "../ESG_reports/IBM.pdf"  # Adjust this path as needed
    raw_text = extract_text_from_pdf(pdf_path)
    cleaned_text = clean_text(raw_text)
    processed_text = preprocess_text(cleaned_text)
    formatted_text = format_for_ai(processed_text)
    
    # Create md_files directory if it doesn't exist
    os.makedirs("../md_files", exist_ok=True)
    
    # Save the preprocessed data to a Markdown file in md_files directory
    output_file = "../md_files/ibm_preprocessed.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Preprocessed ESG Data for Apple\n\n")
        f.write(formatted_text)
    
    print(f"\nPreprocessed data saved to: {output_file}")