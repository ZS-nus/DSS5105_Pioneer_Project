import markdown
import re
from bs4 import BeautifulSoup
from transformers import AutoTokenizer
from datasets import Dataset, Features, Sequence, Value, ClassLabel
from transformers import AutoModelForTokenClassification
from transformers import TrainingArguments, Trainer, DataCollatorForTokenClassification
import os

def markdown_to_text(markdown_string):
    """Convert a markdown string to plaintext"""
    # Convert markdown to HTML
    html = markdown.markdown(markdown_string)
    # Create a BeautifulSoup object to parse the HTML
    soup = BeautifulSoup(html, features="html.parser")
    # Get the text content
    text = soup.get_text()
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def read_markdown_file(file_path):
    """Read a Markdown file and return its content"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def process_markdown_file(file_path):
    """Process a single Markdown file"""
    markdown_content = read_markdown_file(file_path)
    plain_text = markdown_to_text(markdown_content)
    return plain_text

# Main program
if __name__ == "__main__":
    print(os.getcwd())
    # Define the file path
    md_file_path = '../ESG_reports/tesla.md'  # Changed this line

    # Process Markdown file
    processed_text = process_markdown_file(md_file_path)

    print(f"Processed file: {md_file_path}")
    print(f"First 100 characters: {processed_text[:100]}...")
    print("-" * 50)