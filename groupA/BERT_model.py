import os
import json
import torch
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, KFold
from transformers import RobertaTokenizer, RobertaForTokenClassification
from transformers import Trainer, TrainingArguments, get_linear_schedule_with_warmup
from torch.utils.data import Dataset, WeightedRandomSampler
from seqeval.metrics import accuracy_score, precision_score, recall_score, f1_score
from seqeval.scheme import IOB2

# Set random seed for reproducibility
torch.manual_seed(42)

# Load the tokenizer
tokenizer = RobertaTokenizer.from_pretrained('roberta-base')

# Define paths
input_data_path = '../txt_files'
labeled_data_path = '../labeled_files'  # Update this to your JSON files directory

print(f"Input data path: {os.path.abspath(input_data_path)}")
print(f"Labeled data path: {os.path.abspath(labeled_data_path)}")

def load_data(input_path, label_path):
    texts = []
    labels = []
    for filename in os.listdir(input_path):
        if filename.endswith('.txt'):
            with open(os.path.join(input_path, filename), 'r', encoding='utf-8') as file:
                texts.append(file.read())
            
            # Construct the label filename
            label_filename = os.path.join(label_path, filename.replace('.txt', '_labels.json'))
            print(f"Looking for label file: {label_filename}")
            if os.path.exists(label_filename):
                with open(label_filename, 'r', encoding='utf-8') as file:
                    label_data = json.load(file)
                    labels.append(label_data)
            else:
                print(f"Warning: Label file not found for {filename}")
                labels.append([])  # Add an empty list of labels if file not found
    
    return texts, labels

# Load the data
texts, labels = load_data(input_data_path, labeled_data_path)

print(f"Number of texts loaded: {len(texts)}")
print(f"Number of label sets loaded: {len(labels)}")
if labels:
    print(f"Sample of first label set: {labels[0][:10]}")  # Print first 10 labels of the first document

def process_labels(labels):
    processed_labels = []
    for doc_labels in labels:
        doc_processed = []
        for label in doc_labels:
            # Assuming each label is a dictionary with a 'label' key
            if isinstance(label, dict) and 'label' in label:
                doc_processed.append(label['label'])
            else:
                print(f"Unexpected label format: {label}")
                doc_processed.append('O')  # Use 'O' as a default label
        processed_labels.append(doc_processed)
    return processed_labels

# Process the labels
processed_labels = process_labels(labels)

# Create label to id mapping
unique_labels = set([label for doc_labels in processed_labels for label in doc_labels])
print(f"Unique labels: {unique_labels}")
label2id = {label: id for id, label in enumerate(unique_labels)}
id2label = {id: label for label, id in label2id.items()}

# Use the first label as default for padding (or you can choose any other strategy)
default_label = list(unique_labels)[0] if unique_labels else 'O'
print(f"Using '{default_label}' as default label for padding")

# Tokenize and encode the dataset
input_ids = []
attention_masks = []
encoded_labels = []

for text, doc_labels in zip(texts, processed_labels):
    encoded = tokenizer.encode_plus(
        text,
        add_special_tokens=True,
        max_length=512,
        truncation=True,
        padding='max_length',
        return_attention_mask=True,
        return_tensors='pt'
    )
    
    input_ids.append(encoded['input_ids'])
    attention_masks.append(encoded['attention_mask'])
    
    # Encode labels
    label_ids = [label2id[label] for label in doc_labels]
    # Pad or truncate label_ids to match input_ids length
    label_ids = label_ids[:512] + [label2id[default_label]] * (512 - len(label_ids))
    encoded_labels.append(torch.tensor(label_ids))

# Convert lists to tensors
input_ids = torch.cat(input_ids, dim=0)
attention_masks = torch.cat(attention_masks, dim=0)
labels = torch.stack(encoded_labels)

# Split the data into train and validation sets
train_inputs, val_inputs, train_masks, val_masks, train_labels, val_labels = train_test_split(
    input_ids, attention_masks, labels, test_size=0.2, random_state=42
)

# Create a custom dataset
class ESGDataset(Dataset):
    def __init__(self, inputs, masks, labels):
        self.inputs = inputs
        self.masks = masks
        self.labels = labels
    
    def __len__(self):
        return len(self.inputs)
    
    def __getitem__(self, idx):
        return {
            'input_ids': self.inputs[idx],
            'attention_mask': self.masks[idx],
            'labels': self.labels[idx]
        }

# Create datasets
train_dataset = ESGDataset(train_inputs, train_masks, train_labels)
val_dataset = ESGDataset(val_inputs, val_masks, val_labels)

# Prepare the model
model = RobertaForTokenClassification.from_pretrained('roberta-base', num_labels=len(unique_labels))

# Set up training arguments
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=10,  # Increased from 3
    per_device_train_batch_size=32,  # Increased from 16
    per_device_eval_batch_size=64,
    warmup_steps=1000,  # Increased from 500
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=10,
    evaluation_strategy="steps",
    eval_steps=100,
    save_steps=1000,
    save_total_limit=2,
    learning_rate=2e-5,  # Explicitly set learning rate
)

# Modify the compute_metrics function
def compute_metrics(p):
    predictions, labels = p
    predictions = np.argmax(predictions, axis=2)

    true_predictions = [
        [id2label[p] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]
    true_labels = [
        [id2label[l] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]

    return {
        "accuracy": accuracy_score(true_labels, true_predictions),
        "precision": precision_score(true_labels, true_predictions),
        "recall": recall_score(true_labels, true_predictions),
        "f1": f1_score(true_labels, true_predictions)
    }

# Set up K-fold cross-validation
k_folds = 5  # Increased from 2
kf = KFold(n_splits=k_folds, shuffle=True, random_state=42)

# Lists to store metrics for each fold
accuracies = []
precisions = []
recalls = []
f1_scores = []

# Perform K-fold cross-validation
for fold, (train_idx, val_idx) in enumerate(kf.split(input_ids)):
    print(f"Fold {fold + 1}/{k_folds}")
    
    # Split the data
    train_inputs, val_inputs = input_ids[train_idx], input_ids[val_idx]
    train_masks, val_masks = attention_masks[train_idx], attention_masks[val_idx]
    train_labels, val_labels = labels[train_idx], labels[val_idx]
    
    # Create datasets
    train_dataset = ESGDataset(train_inputs, train_masks, train_labels)
    val_dataset = ESGDataset(val_inputs, val_masks, val_labels)
    
    # Prepare the model
    model = RobertaForTokenClassification.from_pretrained('roberta-base', num_labels=len(unique_labels))
    
    # Set up training arguments
    training_args = TrainingArguments(
        output_dir=f'./results/fold_{fold + 1}',
        num_train_epochs=20,  # Increased from 3
        per_device_train_batch_size=32,  # Increased from 16
        per_device_eval_batch_size=64,
        warmup_steps=1000,  # Increased from 500
        weight_decay=0.01,
        logging_dir=f'./logs/fold_{fold + 1}',
        logging_steps=10,
        evaluation_strategy="steps",
        eval_steps=100,
        save_steps=1000,
        save_total_limit=2,
        learning_rate=2e-5,  # Explicitly set learning rate
    )
    
    # Create weighted sampler to handle class imbalance
    label_counts = torch.bincount(train_labels.flatten())
    class_weights = 1. / label_counts.float()
    sample_weights = class_weights[train_labels.flatten()]
    sampler = WeightedRandomSampler(sample_weights, len(sample_weights))

    # Create Trainer instance
    data_collator = lambda data: {'input_ids': torch.stack([f['input_ids'] for f in data]),
                                    'attention_mask': torch.stack([f['attention_mask'] for f in data]),
                                    'labels': torch.stack([f['labels'] for f in data])}
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics
    )

    # Add learning rate scheduler
    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=1000,
        num_training_steps=len(train_dataset) * training_args.num_train_epochs
    )

    # Train the model
    trainer.train()
    
    # Evaluate the model
    eval_results = trainer.evaluate()
    
    # Store the metrics
    accuracies.append(eval_results['eval_accuracy'])
    precisions.append(eval_results['eval_precision'])
    recalls.append(eval_results['eval_recall'])
    f1_scores.append(eval_results['eval_f1'])

# Print average metrics across all folds
print("\nAverage Metrics Across All Folds:")
print(f"Accuracy: {np.mean(accuracies):.4f} (+/- {np.std(accuracies):.4f})")
print(f"Precision: {np.mean(precisions):.4f} (+/- {np.std(precisions):.4f})")
print(f"Recall: {np.mean(recalls):.4f} (+/- {np.std(recalls):.4f})")
print(f"F1-score: {np.mean(f1_scores):.4f} (+/- {np.std(f1_scores):.4f})")

# Train final model on all data
print("\nTraining final model on all data...")
full_dataset = ESGDataset(input_ids, attention_masks, labels)

final_model = RobertaForTokenClassification.from_pretrained('roberta-base', num_labels=len(unique_labels))

final_training_args = TrainingArguments(
    output_dir='./final_model',
    num_train_epochs=5,  # Increased from 3
    per_device_train_batch_size=32,  # Increased from 16
    per_device_eval_batch_size=64,
    warmup_steps=1000,  # Increased from 500
    weight_decay=0.01,
    logging_dir='./final_logs',
    logging_steps=10,
    save_steps=1000,
    save_total_limit=2,
    learning_rate=2e-5,  # Explicitly set learning rate
)

final_trainer = Trainer(
    model=final_model,
    args=final_training_args,
    train_dataset=full_dataset,
    compute_metrics=compute_metrics
)

final_trainer.train()

# Save the final model
final_model.save_pretrained("./esg_bert_model")
tokenizer.save_pretrained("./esg_bert_model")

print("Final model training completed and saved!")