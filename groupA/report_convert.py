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
    headers = []

    for line in lines:
        # Check if the line contains potential table data
        if re.search(r'\b(20\d{2}|[0-9]+(?:,[0-9]{3})*)\b', line):
            if not in_table:
                # Attempt to extract headers from the previous line or the current line
                if headers:
                    header_line = "| " + " | ".join(headers) + " |"
                    formatted_lines.append(header_line)
                    formatted_lines.append("|" + "---|" * len(headers))
                in_table = True
            
            # Extract data, allowing for commas in numbers
            data = re.findall(r'[\d,]+(?:\.\d+)?|[A-Za-z%]+', line)
            if data:
                formatted_row = "| " + " | ".join(data) + " |"
                formatted_lines.append(formatted_row)
        else:
            if in_table:
                # End of the table
                formatted_lines.append("")  # Add a blank line after table
                in_table = False
            # Check for potential headers in non-table lines
            potential_headers = re.findall(r'([A-Za-z\s()]+)', line)
            if potential_headers:
                headers = [header.strip() for header in potential_headers if header.strip()]

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
    os.makedirs("../txt_files", exist_ok=True)
    
    # Save the preprocessed data to a Markdown file in md_files directory
    output_file = "../txt_files/IBM.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Preprocessed ESG Data\n\n")
        f.write(formatted_text)
    
    print(f"\nPreprocessed data saved to: {output_file}")