import json
from datasets import load_dataset
from transformers import (
    AutoTokenizer, AutoModelForTokenClassification, Trainer, TrainingArguments,
    T5Tokenizer, T5ForConditionalGeneration
)
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader
import os

DATA_FILE = "/home/zaman/Code/AskLex/data_bns.json"
SAVE_DIR = "./hybrid_legal_model"
os.makedirs(SAVE_DIR, exist_ok=True)

dataset = load_dataset("json", data_files=DATA_FILE)
train_data = dataset["train"]

print("\nLoading Legal-BERT...")
legal_bert_name = "nlpaueb/legal-bert-base-uncased"
legal_bert_model = AutoModelForTokenClassification.from_pretrained(legal_bert_name)
legal_bert_tokenizer = AutoTokenizer.from_pretrained(legal_bert_name)

legal_bert_model.save_pretrained(os.path.join(SAVE_DIR, "legal_bert"))
legal_bert_tokenizer.save_pretrained(os.path.join(SAVE_DIR, "legal_bert"))

print("\nFine-tuning Sentence-BERT on Q–A similarity...")
sbert_name = "sentence-transformers/all-MiniLM-L6-v2"
sbert_model = SentenceTransformer(sbert_name)

# Fixed: Use MultipleNegativesRankingLoss for Q-A pairs
examples = []
for item in train_data:
    q = item["question"]
    a = item["answer"]
    examples.append(InputExample(texts=[q, a]))

train_dataloader = DataLoader(examples, shuffle=True, batch_size=8)
# Changed to MultipleNegativesRankingLoss which is better for Q-A pairs
train_loss = losses.MultipleNegativesRankingLoss(model=sbert_model)

sbert_model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=3,  # Increased from 1
    warmup_steps=100,
    show_progress_bar=True
)
sbert_model.save(os.path.join(SAVE_DIR, "sentence_bert"))
print("Sentence-BERT fine-tuning complete.")

print("\nFine-tuning T5 on Q–A generation...")
t5_model_name = "google/flan-t5-base"
t5_model = T5ForConditionalGeneration.from_pretrained(t5_model_name)
t5_tokenizer = T5Tokenizer.from_pretrained(t5_model_name)

def preprocess(examples):
    inputs = ["Question: " + q for q in examples["question"]]
    targets = [a for a in examples["answer"]]
    model_inputs = t5_tokenizer(inputs, truncation=True, padding="max_length", max_length=256)
    labels = t5_tokenizer(targets, truncation=True, padding="max_length", max_length=256)
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

tokenized_dataset = train_data.map(preprocess, batched=True, remove_columns=["question", "answer"])

training_args = TrainingArguments(
    output_dir=os.path.join(SAVE_DIR, "t5_model"),
    per_device_train_batch_size=4,
    num_train_epochs=3,
    save_strategy="epoch",
    logging_dir="./logs",
    logging_steps=100,
)

trainer = Trainer(
    model=t5_model,
    args=training_args,
    train_dataset=tokenized_dataset,
)
trainer.train()

t5_model.save_pretrained(os.path.join(SAVE_DIR, "t5_model"))
t5_tokenizer.save_pretrained(os.path.join(SAVE_DIR, "t5_model"))
print("T5 fine-tuning complete.")

print("\n✅ Hybrid model training complete.")
print(f"Models saved in: {SAVE_DIR}")