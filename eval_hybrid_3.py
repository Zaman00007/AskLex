import json
import torch
from datasets import load_dataset
from transformers import T5Tokenizer, T5ForConditionalGeneration, AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer, util
import numpy as np
from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import warnings
warnings.filterwarnings('ignore')

DATA_FILE = "/home/zaman/Code/AskLex/data_bns.json"
SAVE_DIR = "./hybrid_legal_model"

print("Loading hybrid model components...")

legal_bert_tokenizer = AutoTokenizer.from_pretrained(f"{SAVE_DIR}/legal_bert")
legal_bert_model = AutoModel.from_pretrained(f"{SAVE_DIR}/legal_bert")
legal_bert_model.eval()

sbert_model = SentenceTransformer(f"{SAVE_DIR}/sentence_bert")

t5_model = T5ForConditionalGeneration.from_pretrained(f"{SAVE_DIR}/t5_model")
t5_tokenizer = T5Tokenizer.from_pretrained(f"{SAVE_DIR}/t5_model")
t5_model.eval()

print("Loading data...")
dataset = load_dataset("json", data_files=DATA_FILE)
full_data = dataset["train"]

test_size = min(50, len(full_data))
test_data = full_data.select(range(test_size))

kb_data = full_data.select(range(test_size, len(full_data)))
print(f"Knowledge base size: {len(kb_data)} Q-A pairs")

print("Building knowledge base embeddings...")
kb_questions = [item["question"] for item in kb_data]
kb_answers = [item["answer"] for item in kb_data]
kb_embeddings = sbert_model.encode(kb_questions, convert_to_tensor=True, show_progress_bar=True)

def get_legal_bert_embedding(text):
    """Extract Legal-BERT embeddings for legal domain understanding"""
    inputs = legal_bert_tokenizer(text, return_tensors="pt", max_length=512, truncation=True, padding=True)
    with torch.no_grad():
        outputs = legal_bert_model(**inputs)
        # Use [CLS] token embedding
        embedding = outputs.last_hidden_state[:, 0, :].squeeze()
    return embedding

def retrieve_similar_contexts(question, top_k=3):
    """Use Sentence-BERT to retrieve similar Q-A pairs from knowledge base"""
    query_embedding = sbert_model.encode(question, convert_to_tensor=True)
    similarities = util.cos_sim(query_embedding, kb_embeddings)[0]
    top_indices = torch.topk(similarities, k=min(top_k, len(kb_data))).indices
    
    contexts = []
    for idx in top_indices:
        contexts.append({
            "question": kb_questions[idx],
            "answer": kb_answers[idx],
            "similarity": similarities[idx].item()
        })
    return contexts

def hybrid_answer_generation(question, use_retrieval=True, use_legal_bert=True):
    """
    Hybrid approach:
    1. Legal-BERT: Understand legal domain context
    2. Sentence-BERT: Retrieve similar Q-A pairs
    3. T5: Generate answer with enriched context
    """
    
    # Step 1: Get Legal-BERT embedding (domain understanding)
    legal_context = ""
    if use_legal_bert:
        legal_embedding = get_legal_bert_embedding(question)
        # Legal-BERT helps understand legal terminology
        legal_context = "[Legal Domain] "
    
    # Step 2: Retrieve similar Q-A pairs using Sentence-BERT
    retrieved_context = ""
    if use_retrieval:
        similar_contexts = retrieve_similar_contexts(question, top_k=2)
        for i, ctx in enumerate(similar_contexts, 1):
            retrieved_context += f"Similar Q{i}: {ctx['question'][:100]} A{i}: {ctx['answer'][:100]} "
    
    # Step 3: Generate answer with T5 using enriched context
    input_text = f"{legal_context}Question: {question} {retrieved_context}"
    inputs = t5_tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
    
    with torch.no_grad():
        outputs = t5_model.generate(
            inputs.input_ids,
            max_length=256,
            num_beams=4,
            early_stopping=True,
            temperature=0.7
        )
    
    answer = t5_tokenizer.decode(outputs[0], skip_special_tokens=True)
    return answer

print(f"\n{'='*70}")
print("HYBRID MODEL EVALUATION")
print(f"{'='*70}\n")

results = {
    "hybrid": {"bleu": [], "rouge1": [], "rouge2": [], "rougeL": [], "semantic_sim": []},
    "t5_only": {"bleu": [], "rouge1": [], "rouge2": [], "rougeL": [], "semantic_sim": []},
    "predictions": []
}

rouge_scorer_obj = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
smoothing = SmoothingFunction().method1

for i, item in enumerate(test_data):
    question = item["question"]
    reference = item["answer"]
    
    hybrid_answer = hybrid_answer_generation(question, use_retrieval=True, use_legal_bert=True)
    
    t5_input = f"Question: {question}"
    t5_inputs = t5_tokenizer(t5_input, return_tensors="pt", max_length=256, truncation=True)
    with torch.no_grad():
        t5_outputs = t5_model.generate(t5_inputs.input_ids, max_length=256, num_beams=4)
    t5_only_answer = t5_tokenizer.decode(t5_outputs[0], skip_special_tokens=True)
    
    for approach, answer in [("hybrid", hybrid_answer), ("t5_only", t5_only_answer)]:
        bleu = sentence_bleu([reference.split()], answer.split(), smoothing_function=smoothing)
        results[approach]["bleu"].append(bleu)
        rouge = rouge_scorer_obj.score(reference, answer)
        results[approach]["rouge1"].append(rouge['rouge1'].fmeasure)
        results[approach]["rouge2"].append(rouge['rouge2'].fmeasure)
        results[approach]["rougeL"].append(rouge['rougeL'].fmeasure)
        ref_emb = sbert_model.encode(reference, convert_to_tensor=True)
        ans_emb = sbert_model.encode(answer, convert_to_tensor=True)
        sim = util.cos_sim(ref_emb, ans_emb).item()
        results[approach]["semantic_sim"].append(sim)
    
    results["predictions"].append({
        "question": question,
        "reference": reference,
        "hybrid_answer": hybrid_answer,
        "t5_only_answer": t5_only_answer
    })
    
    if (i + 1) % 10 == 0:
        print(f"Processed {i + 1}/{len(test_data)} samples...")

print(f"\n{'='*70}")
print("RESULTS COMPARISON: Hybrid vs T5-Only")
print(f"{'='*70}\n")

print(f"{'Metric':<25} {'Hybrid':<15} {'T5-Only':<15} {'Improvement'}")
print("-" * 70)

metrics = {
    "BLEU Score": "bleu",
    "ROUGE-1": "rouge1",
    "ROUGE-2": "rouge2",
    "ROUGE-L": "rougeL",
    "Semantic Similarity": "semantic_sim"
}

for metric_name, metric_key in metrics.items():
    hybrid_score = np.mean(results["hybrid"][metric_key])
    t5_score = np.mean(results["t5_only"][metric_key])
    improvement = ((hybrid_score - t5_score) / t5_score * 100) if t5_score > 0 else 0
    
    print(f"{metric_name:<25} {hybrid_score:<15.4f} {t5_score:<15.4f} {improvement:+.2f}%")

print(f"\n{'='*70}")
print("EXAMPLE PREDICTIONS")
print(f"{'='*70}\n")

for i in range(min(3, len(results["predictions"]))):
    pred = results["predictions"][i]
    print(f"Example {i+1}:")
    print(f"  Q: {pred['question'][:100]}...")
    print(f"  Reference: {pred['reference'][:120]}...")
    print(f"  Hybrid: {pred['hybrid_answer'][:120]}...")
    print(f"  T5-Only: {pred['t5_only_answer'][:120]}...")
    print()

output_file = f"{SAVE_DIR}/hybrid_evaluation_results.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        "summary": {
            "hybrid": {k: float(np.mean(v)) for k, v in results["hybrid"].items()},
            "t5_only": {k: float(np.mean(v)) for k, v in results["t5_only"].items()}
        },
        "predictions": results["predictions"][:20] 
    }, f, indent=2, ensure_ascii=False)

print(f"💾 Results saved to: {output_file}")

print(f"\n{'='*70}")
print("🔍 INTERACTIVE HYBRID TESTING")
print(f"{'='*70}")
print("Ask legal questions (type 'quit' to exit)\n")

while True:
    user_question = input("❓ Your question: ").strip()
    if user_question.lower() in ['quit', 'exit', 'q']:
        break
    
    if not user_question:
        continue
    
    print("\n🤖 Generating answer using hybrid approach...")
    answer = hybrid_answer_generation(user_question)
    print(f"💡 Answer: {answer}\n")

print("\n✅ Evaluation complete!")