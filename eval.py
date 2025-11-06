from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import evaluate
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import time
import numpy as np
import pandas as pd
from datetime import datetime

# ============ LOAD TRAINED MODEL ============
print("="*60)
print("LOADING TRAINED MODEL")
print("="*60)

model_path = "/home/zaman/Code/AskLex/legal-llm-bns"
print(f"Loading model from: {model_path}")

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSeq2SeqLM.from_pretrained(model_path)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")
model.to(device)
model.eval()

print("Model loaded successfully!\n")

print("="*60)
print("LOADING EVALUATION DATA")
print("="*60)

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

tokenized = dataset.map(preprocess, batched=True)
train_test_split = tokenized["train"].train_test_split(test_size=0.2, seed=42)
eval_dataset = train_test_split["test"]

print(f"Evaluation samples: {len(eval_dataset)}\n")

# ============ LOAD EVALUATION METRICS ============
print("="*60)
print("LOADING EVALUATION METRICS")
print("="*60)

bleu_metric = evaluate.load("bleu")
rouge_metric = evaluate.load("rouge")
print("Loading sentence transformer for similarity calculation...")
similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
print("Metrics loaded successfully!\n")

# ============ PREPARE EVALUATION DATA ============
eval_questions = []
eval_references = []

for item in eval_dataset:
    question = tokenizer.decode(item['input_ids'], skip_special_tokens=True)
    label_ids = [l if l != -100 else tokenizer.pad_token_id for l in item['labels']]
    reference = tokenizer.decode(label_ids, skip_special_tokens=True)
    
    eval_questions.append(question)
    eval_references.append(reference)

# ============ GENERATE PREDICTIONS ============
print("="*60)
print("GENERATING PREDICTIONS")
print("="*60)

predictions = []
response_times = []
exact_matches = 0

print(f"Evaluating on {len(eval_questions)} samples...\n")

for i, question in enumerate(eval_questions):
    if i % 10 == 0:
        print(f"Progress: {i}/{len(eval_questions)}")
    
    inputs = tokenizer(question, return_tensors="pt", max_length=512, truncation=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    # Measure response time
    start_time = time.time()
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=512, num_beams=4, early_stopping=True)
    end_time = time.time()
    
    response_times.append(end_time - start_time)
    
    prediction = tokenizer.decode(outputs[0], skip_special_tokens=True)
    predictions.append(prediction)
    
    # Check for exact match
    if prediction.strip().lower() == eval_references[i].strip().lower():
        exact_matches += 1

print("\nPredictions completed!\n")

# ============ CALCULATE METRICS ============
print("="*60)
print("CALCULATING METRICS")
print("="*60)

# 1. Accuracy
accuracy = (exact_matches / len(eval_questions)) * 100

# 2. BLEU Score
bleu_results = bleu_metric.compute(
    predictions=predictions,
    references=[[ref] for ref in eval_references]
)

# 3. ROUGE Score
rouge_results = rouge_metric.compute(
    predictions=predictions,
    references=eval_references
)

# 4. Semantic Similarity
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

# 5. Response Time
avg_response_time = np.mean(response_times)
median_response_time = np.median(response_times)

print("Metrics calculated!\n")

# ============ DISPLAY RESULTS ============
print("="*60)
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

# ============ SAVE TO CSV ============
print("\n" + "="*60)
print("SAVING RESULTS TO CSV")
print("="*60)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# 1. Save detailed predictions CSV
detailed_df = pd.DataFrame({
    'question': eval_questions,
    'reference_answer': eval_references,
    'predicted_answer': predictions,
    'semantic_similarity': [s * 100 for s in similarities],
    'response_time_ms': [t * 1000 for t in response_times],
    'exact_match': [pred.strip().lower() == ref.strip().lower() 
                    for pred, ref in zip(predictions, eval_references)]
})

detailed_csv_path = f"{model_path}/evaluation_detailed_{timestamp}.csv"
detailed_df.to_csv(detailed_csv_path, index=False, encoding='utf-8')
print(f"✅ Detailed predictions saved to: {detailed_csv_path}")

# 2. Save summary metrics CSV
summary_df = pd.DataFrame({
    'Metric': [
        'Exact Match Accuracy (%)',
        'BLEU Score (%)',
        'BLEU-1 (%)',
        'BLEU-2 (%)',
        'BLEU-3 (%)',
        'BLEU-4 (%)',
        'ROUGE-1 (%)',
        'ROUGE-2 (%)',
        'ROUGE-L (%)',
        'Avg Semantic Similarity (%)',
        'Min Semantic Similarity (%)',
        'Max Semantic Similarity (%)',
        'Avg Response Time (ms)',
        'Median Response Time (ms)',
        'Min Response Time (ms)',
        'Max Response Time (ms)',
        'Total Samples',
        'Exact Matches'
    ],
    'Value': [
        f"{accuracy:.2f}",
        f"{bleu_results['bleu']*100:.2f}",
        f"{bleu_results['precisions'][0]*100:.2f}",
        f"{bleu_results['precisions'][1]*100:.2f}",
        f"{bleu_results['precisions'][2]*100:.2f}",
        f"{bleu_results['precisions'][3]*100:.2f}",
        f"{rouge_results['rouge1']*100:.2f}",
        f"{rouge_results['rouge2']*100:.2f}",
        f"{rouge_results['rougeL']*100:.2f}",
        f"{avg_similarity*100:.2f}",
        f"{min_similarity*100:.2f}",
        f"{max_similarity*100:.2f}",
        f"{avg_response_time*1000:.2f}",
        f"{median_response_time*1000:.2f}",
        f"{min(response_times)*1000:.2f}",
        f"{max(response_times)*1000:.2f}",
        f"{len(eval_questions)}",
        f"{exact_matches}"
    ]
})

summary_csv_path = f"{model_path}/evaluation_summary_{timestamp}.csv"
summary_df.to_csv(summary_csv_path, index=False)
print(f"✅ Summary metrics saved to: {summary_csv_path}")

# 3. Save statistics CSV (for analysis)
stats_df = pd.DataFrame({
    'similarity_mean': [avg_similarity * 100],
    'similarity_std': [np.std(similarities) * 100],
    'similarity_min': [min_similarity * 100],
    'similarity_max': [max_similarity * 100],
    'response_time_mean_ms': [avg_response_time * 1000],
    'response_time_std_ms': [np.std(response_times) * 1000],
    'response_time_median_ms': [median_response_time * 1000],
    'accuracy': [accuracy],
    'bleu': [bleu_results['bleu'] * 100],
    'rouge1': [rouge_results['rouge1'] * 100],
    'rouge2': [rouge_results['rouge2'] * 100],
    'rougeL': [rouge_results['rougeL'] * 100],
    'total_samples': [len(eval_questions)],
    'exact_matches': [exact_matches],
    'evaluation_date': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
})

stats_csv_path = f"{model_path}/evaluation_statistics_{timestamp}.csv"
stats_df.to_csv(stats_csv_path, index=False)
print(f"✅ Statistics saved to: {stats_csv_path}")

print("\n" + "="*60)
print("EVALUATION COMPLETE!")
print("="*60)
print(f"\n📁 All results saved in: {model_path}")
print(f"   - Detailed predictions: evaluation_detailed_{timestamp}.csv")
print(f"   - Summary metrics: evaluation_summary_{timestamp}.csv")
print(f"   - Statistics: evaluation_statistics_{timestamp}.csv")

# ============ QUICK TEST EXAMPLE ============
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

print("\n✨ Evaluation pipeline completed successfully! ✨")