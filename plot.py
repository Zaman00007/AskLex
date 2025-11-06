import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV
df = pd.read_csv("./results/dataset2.csv")

df["Model Type"] = ["Hybrid", "T5"]

metrics_main = [
    "Exact Match Accuracy (%)", "BLEU Score (%)", "BLEU-1 (%)", "BLEU-2 (%)",
    "BLEU-3 (%)", "BLEU-4 (%)", "ROUGE-1 (%)", "ROUGE-2 (%)", "ROUGE-L (%)",
    "Avg Semantic Similarity (%)"
]
metric_time = ["Avg Response Time (ms)"]

# --- Plot 1: Main performance metrics ---
plt.figure(figsize=(12, 6))
df_main = df.set_index("Model Type")[metrics_main].transpose()
df_main.plot(kind="bar", figsize=(12, 6), width=0.8)
plt.title("Model Performance Comparison: Hybrid vs T5")
plt.xlabel("Metrics")
plt.ylabel("Percentage (%)")
plt.xticks(rotation=45, ha="right")
plt.legend(title="Model Type")
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# --- Plot 2: Average Response Time ---
plt.figure(figsize=(6, 5))
df_time = df.set_index("Model Type")[metric_time]
df_time.plot(kind="bar", color=["#4C72B0", "#55A868"], legend=False, width=0.5)
plt.title("Average Response Time Comparison")
plt.ylabel("Response Time (ms)")
plt.xticks(rotation=0)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()
