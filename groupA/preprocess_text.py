import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize

# Ensure you have the necessary NLTK data files
nltk.download('punkt')

def clean_text(text):
    """Clean the extracted text."""
    # Remove unwanted characters and normalize whitespace
    text = re.sub(r'\s+', ' ', text)  # Replace multiple whitespace with a single space
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    return text

def tokenize_text(text):
    """Tokenize the cleaned text."""
    words = word_tokenize(text)
    sentences = sent_tokenize(text)
    return words, sentences

def preprocess_text(text):
    """Preprocess the extracted text."""
    cleaned_text = clean_text(text)
    words, sentences = tokenize_text(cleaned_text)
    return cleaned_text, words, sentences

def save_preprocessed_text(cleaned_text, words, sentences, output_file, output_dir="."):
    """Save the preprocessed text to a file."""
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Full path for the output file
    output_file_path = os.path.join(output_dir, output_file)
    
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write("Cleaned Text:\n")
        f.write(cleaned_text + "\n\n")
        f.write("Tokenized Words:\n")
        f.write(" ".join(words) + "\n\n")
        f.write("Tokenized Sentences:\n")
        f.write("\n".join(sentences))
    print(f"Preprocessed text saved in {output_file_path}")

if __name__ == "__main__":
    # Example usage
    sample_text = "This is a sample text for preprocessing. It includes multiple sentences and punctuation!"
    cleaned_text, words, sentences = preprocess_text(sample_text)
    output_file = "preprocessed_text.txt"
    output_dir = "./output"  # Directory to save the preprocessed text file
    save_preprocessed_text(cleaned_text, words, sentences, output_file, output_dir)