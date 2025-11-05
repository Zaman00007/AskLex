from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, TrainingArguments, Trainer, DataCollatorForSeq2Seq
import torch
import evaluate
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import time
import numpy as np

model_name = "google/flan-t5-small"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

dataset = load_dataset("json", data_files="/home/zaman/Code/LLM/data_bns.json")

def preprocess(examples):
    inputs = examples["question"]
    targets = examples["answer"]
    
    model_inputs = tokenizer(
        inputs, 
        max_length=512, 
        truncation=True, 
        padding=False  
    )
    
    labels = tokenizer(
        text_target=targets,  
        max_length=512, 
        truncation=True, 
        padding=False 
    )
    
    labels["input_ids"] = [
        [(l if l != tokenizer.pad_token_id else -100) for l in label] 
        for label in labels["input_ids"]
    ]
    
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

print("Preprocessing dataset...")
tokenized = dataset.map(preprocess, batched=True)

print("Sample input:", tokenized["train"][0]["input_ids"][:10])
print("Sample label:", tokenized["train"][0]["labels"][:10])

train_test_split = tokenized["train"].train_test_split(test_size=0.2, seed=42)
train_dataset = train_test_split["train"]
eval_dataset = train_test_split["test"]

print(f"Training samples: {len(train_dataset)}")
print(f"Evaluation samples: {len(eval_dataset)}")

data_collator = DataCollatorForSeq2Seq(
    tokenizer=tokenizer,
    model=model,
    label_pad_token_id=-100, 
    padding=True
)

training_args = TrainingArguments(
    output_dir="./legal-llm-hybrid",
    eval_strategy="steps",
    eval_steps=8,  
    save_strategy="steps",
    save_steps=8,
    learning_rate=3e-4,  
    per_device_train_batch_size=4,  
    per_device_eval_batch_size=4,
    num_train_epochs=100,  
    weight_decay=0.01,
    warmup_steps=10,  
    fp16=False,  
    logging_dir="./logs",
    logging_steps=2,  
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
    save_total_limit=3,  
    prediction_loss_only=True,
    dataloader_pin_memory=False,  
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    data_collator=data_collator,
    tokenizer=tokenizer, 
)

print("Starting training...")
trainer.train()

trainer.save_model("./legal-llm-hybrid")
tokenizer.save_pretrained("./legal-llm-hybrid")

print("Training completed successfully!")
print("Model saved to ./legal-llm-hybrid")

print("\n" + "="*60)
print("STARTING COMPREHENSIVE EVALUATION")
print("="*60)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

bleu_metric = evaluate.load("bleu")
rouge_metric = evaluate.load("rouge")

print("Loading sentence transformer for similarity calculation...")
similarity_model = SentenceTransformer('all-MiniLM-L6-v2')

eval_questions = []
eval_references = []

for item in eval_dataset:
    question = tokenizer.decode(item['input_ids'], skip_special_tokens=True)
    label_ids = [l if l != -100 else tokenizer.pad_token_id for l in item['labels']]
    reference = tokenizer.decode(label_ids, skip_special_tokens=True)
    
    eval_questions.append(question)
    eval_references.append(reference)

print(f"\nEvaluating on {len(eval_questions)} samples...")

predictions = []
response_times = []
exact_matches = 0

print("\nGenerating predictions...")
for i, question in enumerate(eval_questions):
    if i % 10 == 0:
        print(f"Progress: {i}/{len(eval_questions)}")
    
    inputs = tokenizer(question, return_tensors="pt", max_length=512, truncation=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    start_time = time.time()
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=512, num_beams=4, early_stopping=True)
    end_time = time.time()
    
    response_times.append(end_time - start_time)
    
    prediction = tokenizer.decode(outputs[0], skip_special_tokens=True)
    predictions.append(prediction)
    
    if prediction.strip().lower() == eval_references[i].strip().lower():
        exact_matches += 1

print("\nCalculating evaluation metrics...")

accuracy = (exact_matches / len(eval_questions)) * 100

bleu_results = bleu_metric.compute(
    predictions=predictions,
    references=[[ref] for ref in eval_references]
)

rouge_results = rouge_metric.compute(
    predictions=predictions,
    references=eval_references
)

print("Calculating semantic similarities...")
pred_embeddings = similarity_model.encode(predictions)
ref_embeddings = similarity_model.encode(eval_references)

similarities = []
for pred_emb, ref_emb in zip(pred_embeddings, ref_embeddings):
    similarity = cosine_similarity([pred_emb], [ref_emb])[0][0]
    similarities.append(similarity)

avg_similarity = np.mean(similarities)
min_similarity = np.min(similarities)
max_similarity = np.max(similarities)

avg_response_time = np.mean(response_times)
median_response_time = np.median(response_times)

print("\n" + "="*60)
print("EVALUATION RESULTS")
print("="*60)

print(f"\n📊 ACCURACY METRICS:")
print(f"   Exact Match Accuracy: {accuracy:.2f}%")
print(f"   Exact Matches: {exact_matches}/{len(eval_questions)}")

print(f"\n📝 BLEU SCORE:")
print(f"   BLEU: {bleu_results['bleu']*100:.2f}%")
print(f"   BLEU-1: {bleu_results['precisions'][0]*100:.2f}%")
print(f"   BLEU-2: {bleu_results['precisions'][1]*100:.2f}%")
print(f"   BLEU-3: {bleu_results['precisions'][2]*100:.2f}%")
print(f"   BLEU-4: {bleu_results['precisions'][3]*100:.2f}%")

print(f"\n📊 ROUGE SCORES:")
print(f"   ROUGE-1: {rouge_results['rouge1']*100:.2f}%")
print(f"   ROUGE-2: {rouge_results['rouge2']*100:.2f}%")
print(f"   ROUGE-L: {rouge_results['rougeL']*100:.2f}%")

print(f"\n🎯 SEMANTIC SIMILARITY:")
print(f"   Average Similarity: {avg_similarity*100:.2f}%")
print(f"   Min Similarity: {min_similarity*100:.2f}%")
print(f"   Max Similarity: {max_similarity*100:.2f}%")

print(f"\n⏱️  RESPONSE TIME:")
print(f"   Average Response Time: {avg_response_time*1000:.2f} ms")
print(f"   Median Response Time: {median_response_time*1000:.2f} ms")
print(f"   Min Response Time: {min(response_times)*1000:.2f} ms")
print(f"   Max Response Time: {max(response_times)*1000:.2f} ms")

print("\n💾 Saving detailed evaluation results...")
with open("./legal-llm-hybrid/evaluation_results.txt", "w") as f:
    f.write("="*60 + "\n")
    f.write("DETAILED EVALUATION RESULTS\n")
    f.write("="*60 + "\n\n")
    
    f.write(f"Total Samples: {len(eval_questions)}\n\n")
    
    f.write(f"Exact Match Accuracy: {accuracy:.2f}%\n")
    f.write(f"BLEU Score: {bleu_results['bleu']*100:.2f}%\n")
    f.write(f"Average Semantic Similarity: {avg_similarity*100:.2f}%\n")
    f.write(f"Average Response Time: {avg_response_time*1000:.2f} ms\n\n")
    
    f.write("="*60 + "\n")
    f.write("SAMPLE PREDICTIONS (First 10)\n")
    f.write("="*60 + "\n\n")
    
    for i in range(min(10, len(eval_questions))):
        f.write(f"Sample {i+1}:\n")
        f.write(f"Question: {eval_questions[i]}\n")
        f.write(f"Reference: {eval_references[i]}\n")
        f.write(f"Prediction: {predictions[i]}\n")
        f.write(f"Similarity: {similarities[i]*100:.2f}%\n")
        f.write(f"Response Time: {response_times[i]*1000:.2f} ms\n")
        f.write("-"*60 + "\n\n")

print("Detailed results saved to ./legal-llm-hybrid/evaluation_results.txt")

# Quick test example
print("\n" + "="*60)
print("QUICK TEST EXAMPLE")
print("="*60)

test_question = "I want to take divorce from my husband?"
inputs = tokenizer(test_question, return_tensors="pt", max_length=128, truncation=True)
inputs = {k: v.to(device) for k, v in inputs.items()}

start_time = time.time()
with torch.no_grad():
    outputs = model.generate(**inputs, max_length=128, num_beams=4, early_stopping=True)
end_time = time.time()

response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(f"\nQuestion: {test_question}")
print(f"Answer: {response}")
print(f"Response Time: {(end_time - start_time)*1000:.2f} ms")

print("\n" + "="*60)
print("EVALUATION COMPLETE!")
print("="*60)