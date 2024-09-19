import markdown
import re
from transformers import AutoTokenizer
from datasets import Dataset
from transformers import AutoModelForTokenClassification
from transformers import TrainingArguments, Trainer, DataCollatorForTokenClassification


def markdown_to_text(markdown_string):
    """Converts markdown text to plain text."""
    html = markdown.markdown(markdown_string)
    # Remove HTML tags using regex
    text = re.sub('<[^<]+?>', '', html)
    return text


tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')

def tokenize_and_align_labels(texts, labels_list):
    tokenized_inputs = tokenizer(
        texts,
        padding='max_length',
        truncation=True,
        max_length=128,
        is_split_into_words=False,
        return_offsets_mapping=True,
    )
    offset_mappings = tokenized_inputs.pop("offset_mapping")
    token_labels = []
    for i, offsets in enumerate(offset_mappings):
        labels = labels_list[i]
        label_ids = []
        for offset in offsets:
            if offset[0] == offset[1]:
                label_ids.append(-100)  # Special tokens
            else:
                # Assign label based on character offsets
                label_ids.append(labels.get(offset[0], 'O'))
        token_labels.append(label_ids)
    tokenized_inputs["labels"] = token_labels
    return tokenized_inputs

# Example data
texts = [
    markdown_to_text("# Company Report\nThe company reduced its carbon footprint."),
    markdown_to_text("# Sustainability\nNew policies for social welfare were introduced."),
]

# Example labels in the form of {char_index: label}
labels_list = [
    {31: 'B-Environmental', 37: 'I-Environmental'},  # 'carbon footprint'
    {35: 'B-Social', 41: 'I-Social'},  # 'social welfare'
]

# Tokenize and align labels
tokenized_dataset = tokenize_and_align_labels(texts, labels_list)

dataset = Dataset.from_dict(tokenized_dataset)

print(dataset)


num_labels = 5  # Adjust based on your label set
model = AutoModelForTokenClassification.from_pretrained(
    'bert-base-uncased',
    num_labels=num_labels
)

label_list = ['O', 'B-Environmental', 'I-Environmental', 'B-Social', 'I-Social']
id2label = {i: label for i, label in enumerate(label_list)}
label2id = {label: i for i, label in enumerate(label_list)}


model.config.id2label = id2label
model.config.label2id = label2id

training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=4,
    logging_dir='./logs',
    logging_steps=10,
    evaluation_strategy="no",
    save_strategy="no",
)

data_collator = DataCollatorForTokenClassification(tokenizer)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    tokenizer=tokenizer,
    data_collator=data_collator,
)

trainer.train()

def extract_esg_data(markdown_text):
    text = markdown_to_text(markdown_text)
    inputs = tokenizer(
        text,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=128,
    )
    outputs = model(**inputs)
    predictions = outputs.logits.argmax(-1).squeeze().tolist()
    tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'].squeeze())

    esg_data = []
    for token, pred in zip(tokens, predictions):
        label = id2label[pred]
        esg_data.append((token, label))
    return esg_data

