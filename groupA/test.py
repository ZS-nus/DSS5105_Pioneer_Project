import PyPDF2
from transformers import BartTokenizer, BartForConditionalGeneration

# Load BART model for summarization
tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    return text

# Function to summarize text using BART
def summarize_text(text):
    # Tokenize the input text
    inputs = tokenizer(text, return_tensors="pt", max_length=1024, truncation=True)

    # Generate the summary
    summary_ids = model.generate(inputs['input_ids'], max_length=150, min_length=40, length_penalty=2.0, num_beams=4, early_stopping=True)

    # Decode and return the summary
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

# Main process
pdf_path = "/Users/siusing/Documents/NUS_DSS/SEM1/DSS5105 DS Projects/DSS5105_Pioneer_Project/ESG_reports/2023-ESG-At-A-Glance.pdf"  # Replace with your PDF file path
pdf_text = extract_text_from_pdf(pdf_path)
summary = summarize_text(pdf_text)

print("Summarized Data:", summary)