import torch
from transformers import BertTokenizer, BertForTokenClassification
from seqeval.metrics import classification_report
import argparse

def load_model_and_tokenizer(model_path):
    tokenizer = BertTokenizer.from_pretrained(model_path)
    model = BertForTokenClassification.from_pretrained(model_path)
    return model, tokenizer

def process_text(text, model, tokenizer, max_length=512):
    # Tokenize and encode the text
    encoded = tokenizer.encode_plus(
        text,
        add_special_tokens=True,
        max_length=max_length,
        truncation=True,
        padding='max_length',
        return_attention_mask=True,
        return_tensors='pt'
    )
    
    # Get the input IDs and attention mask
    input_ids = encoded['input_ids']
    attention_mask = encoded['attention_mask']
    
    # Perform inference
    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask)
    
    # Get the predicted labels
    predictions = torch.argmax(outputs.logits, dim=2)
    
    return predictions, attention_mask

def align_predictions_with_tokens(predictions, attention_mask, tokens, id2label):
    aligned_predictions = []
    for i, mask in enumerate(attention_mask[0]):
        if mask == 1:  # Only consider non-padding tokens
            aligned_predictions.append(id2label[predictions[0][i].item()])
    
    # Remove predictions for special tokens ([CLS] and [SEP])
    aligned_predictions = aligned_predictions[1:-1]
    tokens = tokens[1:-1]
    
    return list(zip(tokens, aligned_predictions))

def extract_esg_info(file_path, model_path):
    # Load the model and tokenizer
    model, tokenizer = load_model_and_tokenizer(model_path)
    
    # Load the id2label mapping
    id2label = model.config.id2label
    
    # Read the input file
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    
    # Process the text
    predictions, attention_mask = process_text(text, model, tokenizer)
    
    # Tokenize the text
    tokens = tokenizer.tokenize(text)
    
    # Align predictions with tokens
    aligned_results = align_predictions_with_tokens(predictions, attention_mask, tokens, id2label)
    
    # Extract and group ESG information
    esg_info = {}
    current_label = None
    current_text = []
    
    for token, label in aligned_results:
        if label != 'O':  # 'O' typically means "Outside" or not part of any entity
            if label != current_label:
                if current_label:
                    esg_info.setdefault(current_label, []).append(' '.join(current_text))
                current_label = label
                current_text = [token]
            else:
                current_text.append(token)
        else:
            if current_label:
                esg_info.setdefault(current_label, []).append(' '.join(current_text))
                current_label = None
                current_text = []
    
    # Add any remaining text
    if current_label:
        esg_info.setdefault(current_label, []).append(' '.join(current_text))
    
    return esg_info

def main():
    file_path = "../txt_files/apple.txt"
    model_path = "./esg_bert_model"  # Assuming the model is in the current directory

    esg_info = extract_esg_info(file_path, model_path)
    
    print("Extracted ESG Information from apple.txt:")
    for label, texts in esg_info.items():
        print(f"\n{label}:")
        for text in texts:
            print(f"  - {text}")

if __name__ == "__main__":
    main()
