import json
import torch
from datasets import load_dataset
from transformers import T5Tokenizer, T5ForConditionalGeneration
from sentence_transformers import SentenceTransformer, util
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import warnings
warnings.filterwarnings('ignore')

# Install required packages if needed:
# pip install rouge-score nltk scikit-learn

DATA_FILE = "/home/zaman/Code/AskLex/data_bns.json"
SAVE_DIR = "./hybrid_legal_model"

print("Loading models...")
# Load T5 model
t5_model = T5ForConditionalGeneration.from_pretrained(f"{SAVE_DIR}/t5_model")
t5_tokenizer = T5Tokenizer.from_pretrained(f"{SAVE_DIR}/t5_model")
t5_model.eval()

# Load Sentence-BERT model
sbert_model = SentenceTransformer(f"{SAVE_DIR}/sentence_bert")

print("Loading test data...")
dataset = load_dataset("json", data_files=DATA_FILE)
# Use a portion for testing (e.g., last 20% or create a separate test file)
test_data = dataset["train"].select(range(min(50, len(dataset["train"]))))

print(f"\nEvaluating on {len(test_data)} samples...\n")

# Initialize metrics storage
results = {
    "bleu_scores": [],
    "rouge_scores": {"rouge1": [], "rouge2": [], "rougeL": []},
    "semantic_similarities": [],
    "exact_matches": 0,
    "predictions": []
}

# Initialize scorers
rouge_scorer_obj = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
smoothing = SmoothingFunction().method1

# Evaluation loop
for i, item in enumerate(test_data):
    question = item["question"]
    reference_answer = item["answer"]
    
    # Generate answer using T5
    input_text = f"Question: {question}"
    inputs = t5_tokenizer(input_text, return_tensors="pt", max_length=256, truncation=True)
    
    with torch.no_grad():
        outputs = t5_model.generate(
            inputs.input_ids,
            max_length=256,
            num_beams=4,
            early_stopping=True,
            temperature=0.7
        )
    
    generated_answer = t5_tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Calculate BLEU score
    reference_tokens = reference_answer.split()
    generated_tokens = generated_answer.split()
    bleu = sentence_bleu([reference_tokens], generated_tokens, smoothing_function=smoothing)
    results["bleu_scores"].append(bleu)
    
    # Calculate ROUGE scores
    rouge_scores = rouge_scorer_obj.score(reference_answer, generated_answer)
    results["rouge_scores"]["rouge1"].append(rouge_scores['rouge1'].fmeasure)
    results["rouge_scores"]["rouge2"].append(rouge_scores['rouge2'].fmeasure)
    results["rouge_scores"]["rougeL"].append(rouge_scores['rougeL'].fmeasure)
    
    # Calculate semantic similarity using Sentence-BERT
    ref_embedding = sbert_model.encode(reference_answer, convert_to_tensor=True)
    gen_embedding = sbert_model.encode(generated_answer, convert_to_tensor=True)
    semantic_sim = util.cos_sim(ref_embedding, gen_embedding).item()
    results["semantic_similarities"].append(semantic_sim)
    
    # Check exact match
    if generated_answer.strip().lower() == reference_answer.strip().lower():
        results["exact_matches"] += 1
    
    # Store prediction
    results["predictions"].append({
        "question": question,
        "reference": reference_answer,
        "generated": generated_answer,
        "bleu": bleu,
        "semantic_similarity": semantic_sim
    })
    
    # Print progress
    if (i + 1) % 10 == 0:
        print(f"Processed {i + 1}/{len(test_data)} samples...")

# Calculate average metrics
print("\n" + "="*70)
print("EVALUATION RESULTS")
print("="*70)

print(f"\n📊 Overall Metrics:")
print(f"  • Average BLEU Score:        {np.mean(results['bleu_scores']):.4f}")
print(f"  • Average ROUGE-1:           {np.mean(results['rouge_scores']['rouge1']):.4f}")
print(f"  • Average ROUGE-2:           {np.mean(results['rouge_scores']['rouge2']):.4f}")
print(f"  • Average ROUGE-L:           {np.mean(results['rouge_scores']['rougeL']):.4f}")
print(f"  • Average Semantic Similarity: {np.mean(results['semantic_similarities']):.4f}")
print(f"  • Exact Match Accuracy:      {results['exact_matches']}/{len(test_data)} ({results['exact_matches']/len(test_data)*100:.2f}%)")

# Show best and worst predictions
print(f"\n🌟 Top 3 Best Predictions (by semantic similarity):")
sorted_predictions = sorted(results["predictions"], key=lambda x: x["semantic_similarity"], reverse=True)
for i, pred in enumerate(sorted_predictions[:3], 1):
    print(f"\n  #{i} (Similarity: {pred['semantic_similarity']:.4f}, BLEU: {pred['bleu']:.4f})")
    print(f"  Q: {pred['question'][:100]}...")
    print(f"  Reference: {pred['reference'][:150]}...")
    print(f"  Generated: {pred['generated'][:150]}...")

print(f"\n⚠️  Top 3 Worst Predictions (by semantic similarity):")
for i, pred in enumerate(sorted_predictions[-3:], 1):
    print(f"\n  #{i} (Similarity: {pred['semantic_similarity']:.4f}, BLEU: {pred['bleu']:.4f})")
    print(f"  Q: {pred['question'][:100]}...")
    print(f"  Reference: {pred['reference'][:150]}...")
    print(f"  Generated: {pred['generated'][:150]}...")

# Save detailed results
output_file = f"{SAVE_DIR}/evaluation_results.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        "summary": {
            "avg_bleu": float(np.mean(results['bleu_scores'])),
            "avg_rouge1": float(np.mean(results['rouge_scores']['rouge1'])),
            "avg_rouge2": float(np.mean(results['rouge_scores']['rouge2'])),
            "avg_rougeL": float(np.mean(results['rouge_scores']['rougeL'])),
            "avg_semantic_similarity": float(np.mean(results['semantic_similarities'])),
            "exact_matches": results['exact_matches'],
            "total_samples": len(test_data)
        },
        "predictions": results["predictions"]
    }, f, indent=2, ensure_ascii=False)

print(f"\n💾 Detailed results saved to: {output_file}")

# Interactive testing
print("\n" + "="*70)
print("🔍 INTERACTIVE TESTING")
print("="*70)
print("Enter your questions to test the model (type 'quit' to exit)")

while True:
    user_question = input("\n❓ Your question: ").strip()
    if user_question.lower() in ['quit', 'exit', 'q']:
        break
    
    if not user_question:
        continue
    
    # Generate answer
    input_text = f"Question: {user_question}"
    inputs = t5_tokenizer(input_text, return_tensors="pt", max_length=256, truncation=True)
    
    with torch.no_grad():
        outputs = t5_model.generate(
            inputs.input_ids,
            max_length=256,
            num_beams=4,
            early_stopping=True,
            temperature=0.7
        )
    
    answer = t5_tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"\n💡 Answer: {answer}")

print("\n✅ Evaluation complete!")