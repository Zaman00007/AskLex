import matplotlib.pyplot as plt
import pandas as pd

logs = [
    {'loss': 0.0312, 'grad_norm': 1.5823049545288086, 'learning_rate': 6.612421526436864e-07, 'epoch': 99.80},
    {'loss': 0.0254, 'grad_norm': 1.241578221321106, 'learning_rate': 5.511024763215864e-07, 'epoch': 99.83},
    {'loss': 0.0219, 'grad_norm': 1.0164828300476074, 'learning_rate': 4.291287386215864e-07, 'epoch': 99.87},
    {'loss': 0.005, 'grad_norm': 0.1958053708076477, 'learning_rate': 3.5110533159947976e-07, 'epoch': 99.90},
    {'loss': 0.0047, 'grad_norm': 0.9036898612976074, 'learning_rate': 2.730819245773732e-07, 'epoch': 99.92},
    {'loss': 0.0079, 'grad_norm': 0.6011399626731873, 'learning_rate': 1.9505851755526657e-07, 'epoch': 99.95},
    {'loss': 0.0105, 'grad_norm': 0.4298454225063324, 'learning_rate': 1.5604681404421327e-07, 'epoch': 99.96},
    {'loss': 0.0147, 'grad_norm': 0.23955757915973663, 'learning_rate': 1.1703511053315994e-07, 'epoch': 99.97},
    {'loss': 0.0061, 'grad_norm': 0.20412515103816986, 'learning_rate': 3.901170351105331e-08, 'epoch': 100.00},
    {'loss': 0.0056, 'grad_norm': 0.23148994147777557, 'learning_rate': 1.9505851755526657e-08, 'epoch': 100.02},
]


# Convert to DataFrame
df = pd.DataFrame(logs)

# Fill missing values (e.g., eval_loss rows) with NaN
df = df.fillna(method='ffill')

# Plot loss and eval_loss
plt.figure(figsize=(10, 6))
plt.plot(df["epoch"], df["loss"], marker='o', label="Training Loss")
if "eval_loss" in df:
    plt.plot(df["epoch"], df["eval_loss"], marker='x', linestyle='--', label="Evaluation Loss", color='red')
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.title("Hybrid Model - Loss Trend (Last 10 Epochs)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Plot Grad Norm
plt.figure(figsize=(10, 5))
plt.plot(df["epoch"], df["grad_norm"], marker='o', color='orange')
plt.xlabel("Epoch")
plt.ylabel("Gradient Norm")
plt.title("Hybrid Model - Gradient Norm Trend (Last 10 Epochs)")
plt.grid(True)
plt.tight_layout()
plt.show()

# Plot Learning Rate
plt.figure(figsize=(10, 5))
plt.plot(df["epoch"], df["learning_rate"], marker='o', color='green')
plt.xlabel("Epoch")
plt.ylabel("Learning Rate")
plt.title("Hybrid Model - Learning Rate Schedule (Last 10 Epochs)")
plt.grid(True)
plt.tight_layout()
plt.show()
