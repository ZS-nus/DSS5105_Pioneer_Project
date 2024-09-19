import markdown
import re
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForTokenClassification, TrainingArguments, Trainer, DataCollatorForTokenClassification
from datasets import Dataset, Features, Sequence, Value, ClassLabel
import os
import torch

def markdown_to_text(markdown_string):
    """Convert a markdown string to plaintext"""
    html = markdown.markdown(markdown_string)
    soup = BeautifulSoup(html, features="html.parser")
    text = soup.get_text()
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

# Define label list (customize this based on your ESG categories)
label_list = ['O', 'B-Environmental', 'I-Environmental', 'B-Social', 'I-Social', 'B-Governance', 'I-Governance']
label2id = {label: i for i, label in enumerate(label_list)}
id2label = {i: label for i, label in enumerate(label_list)}

def tokenize_and_align_labels(texts, labels):
    tokenized_inputs = tokenizer(texts, truncation=True, is_split_into_words=True)
    labels = []
    for i, label in enumerate(labels):
        word_ids = tokenized_inputs.word_ids(batch_index=i)
        previous_word_idx = None
        label_ids = []
        for word_idx in word_ids:
            if word_idx is None:
                label_ids.append(-100)
            elif word_idx != previous_word_idx:
                label_ids.append(label2id[label[word_idx]])
            else:
                label_ids.append(label2id[label[word_idx]] if label[word_idx].startswith("I-") else label2id['O'])
            previous_word_idx = word_idx
        labels.append(label_ids)
    tokenized_inputs["labels"] = labels
    return tokenized_inputs

# Main program
if __name__ == "__main__":
    print(os.getcwd())
    # Define the file path
    md_file_path = '../ESG_reports/tesla.md'

    # Process Markdown file
    processed_text = process_markdown_file(md_file_path)

    print(f"Processed file: {md_file_path}")
    print(f"First 100 characters: {processed_text[:100]}...")
    print("-" * 50)

    # Tokenize the text
    tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
    
    # For this example, we'll use dummy labels. In a real scenario, you'd need to label your data.
    dummy_labels = ['O'] * len(processed_text.split())
    
    # Tokenize and align labels
    tokenized_input = tokenize_and_align_labels([processed_text.split()], [dummy_labels])
    
    # Create dataset
    dataset = Dataset.from_dict(tokenized_input)
    
    # Load pre-trained model
    model = AutoModelForTokenClassification.from_pretrained(
        "bert-base-uncased", 
        num_labels=len(label_list),
        id2label=id2label,
        label2id=label2id
    )

    # Set up training arguments
    training_args = TrainingArguments(
        output_dir="./results",
        evaluation_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=3,
        weight_decay=0.01,
    )

    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        eval_dataset=dataset,
        tokenizer=tokenizer,
        data_collator=DataCollatorForTokenClassification(tokenizer),
    )

    # Train the model
    trainer.train()

    # Save the model
    trainer.save_model("./esg_ner_model")

    print("Model training completed and saved.")