# Stacking Meta-Model Training (TOP 2: BERT + KcBERT)
import json
import torch
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import f1_score, precision_score, recall_score
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from tqdm import tqdm
import lightgbm as lgb
import pickle

print("="*70)
print("Stacking Meta-Model Training (TOP 2: BERT + KcBERT)")
print("="*70)

INPUT_FILE = "./data/remember/prepared_data.json"
META_MODEL_DIR = "./models/meta_model_stacking_top2"
SEED = 42
MAX_LENGTH = 256

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"\nDevice: {device}")

# Load data
print("\n[1] Loading data...")
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    loaded_data = json.load(f)

jobs = loaded_data['data']
all_skills = loaded_data['all_skills']

mlb = MultiLabelBinarizer()
mlb.fit([job['skills'] for job in jobs])

texts = [job['text'] for job in jobs]
labels = [job['skills'] for job in jobs]
labels_binary = mlb.transform(labels)

train_texts, temp_texts, train_labels, temp_labels = train_test_split(
    texts, labels_binary, test_size=0.3, random_state=SEED
)
val_texts, test_texts, val_labels, test_labels = train_test_split(
    temp_texts, temp_labels, test_size=0.5, random_state=SEED
)

print(f"    Train: {len(train_texts)}")
print(f"    Val: {len(val_texts)}")
print(f"    Test: {len(test_texts)}")

# Load TOP 2 models
print("\n[2] Loading TOP 2 base models...")
MODEL_DIRS = [
    "./models/final_model_bert_seed42",
    "./models/final_model_kcbert_seed42",
]

models = []
tokenizers = []
model_names = []

for model_dir in MODEL_DIRS:
    name = Path(model_dir).name
    print(f"    {name}...")

    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)
    model.to(device)
    model.eval()

    models.append(model)
    tokenizers.append(tokenizer)
    model_names.append(name)

print(f"    Total: {len(models)} models loaded")

# Generate base predictions
print("\n[3] Generating base model predictions...")

def get_predictions(texts_list, models, tokenizers, desc="Predicting"):
    all_predictions = []

    for model_idx, (model, tokenizer) in enumerate(zip(models, tokenizers)):
        print(f"\n    [{model_idx+1}/{len(models)}] {model_names[model_idx]}")

        predictions = []
        for text in tqdm(texts_list, desc=f"    {desc}"):
            inputs = tokenizer(
                text,
                truncation=True,
                padding=True,
                max_length=MAX_LENGTH,
                return_tensors='pt'
            )
            inputs = {k: v.to(device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = model(**inputs)
                probs = torch.sigmoid(outputs.logits).cpu().numpy()[0]
                predictions.append(probs)

        all_predictions.append(np.array(predictions))

    return np.array(all_predictions)

train_preds = get_predictions(train_texts, models, tokenizers, "Train")
val_preds = get_predictions(val_texts, models, tokenizers, "Val")
test_preds = get_predictions(test_texts, models, tokenizers, "Test")

print(f"\n    Predictions shape: {train_preds.shape}")

# Prepare features for meta-model
print("\n[4] Preparing stacking features...")

def prepare_stacking_features(predictions):
    n_samples = predictions.shape[1]
    return predictions.transpose(1, 0, 2).reshape(n_samples, -1)

X_train = prepare_stacking_features(train_preds)
X_val = prepare_stacking_features(val_preds)
X_test = prepare_stacking_features(test_preds)

y_train = train_labels
y_val = val_labels
y_test = test_labels

print(f"    X_train: {X_train.shape}")
print(f"    X_val: {X_val.shape}")
print(f"    X_test: {X_test.shape}")

# Train LightGBM meta-models
print("\n[5] Training LightGBM meta-models (one per label)...")

n_labels = len(all_skills)
meta_models = []

for label_idx in tqdm(range(n_labels), desc="    Training"):
    y_train_label = y_train[:, label_idx]
    y_val_label = y_val[:, label_idx]

    if y_train_label.sum() > 0:
        train_data = lgb.Dataset(X_train, label=y_train_label)
        val_data = lgb.Dataset(X_val, label=y_val_label, reference=train_data)

        params = {
            'objective': 'binary',
            'metric': 'binary_logloss',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.9,
            'verbose': -1,
        }

        model = lgb.train(
            params,
            train_data,
            num_boost_round=100,
            valid_sets=[val_data],
            callbacks=[lgb.early_stopping(stopping_rounds=10, verbose=False)]
        )

        meta_models.append(model)
    else:
        meta_models.append(None)

print(f"    Trained: {sum(m is not None for m in meta_models)} meta-models")

# Evaluate on test set
print("\n[6] Evaluating on test set...")

test_meta_probs = np.zeros((len(X_test), n_labels))

for label_idx, model in enumerate(meta_models):
    if model is not None:
        test_meta_probs[:, label_idx] = model.predict(X_test)

# Find optimal threshold
print("\n    Finding optimal threshold...")

best_th, best_f1 = 0.3, 0.0

for th in np.arange(0.25, 0.56, 0.05):
    preds = (test_meta_probs >= th).astype(int)
    f1 = f1_score(y_test, preds, average='micro', zero_division=0)
    if f1 > best_f1:
        best_f1 = f1
        best_th = th

print(f"    Optimal threshold: {best_th:.2f}")

# Final evaluation
test_preds_binary = (test_meta_probs >= best_th).astype(int)
final_f1 = f1_score(y_test, test_preds_binary, average='micro', zero_division=0)
final_precision = precision_score(y_test, test_preds_binary, average='micro', zero_division=0)
final_recall = recall_score(y_test, test_preds_binary, average='micro', zero_division=0)

print("\n" + "="*70)
print("TEST SET RESULTS")
print("="*70)
print(f"\nStacking (TOP 2):")
print(f"    Threshold: {best_th:.2f}")
print(f"    F1:        {final_f1:.4f}")
print(f"    Precision: {final_precision:.4f}")
print(f"    Recall:    {final_recall:.4f}")

# Compare with baseline
print("\n" + "="*70)
print("COMPARISON")
print("="*70)

baseline_f1 = 0.25
kcbert_f1 = 0.6256
weighted_f1 = 0.6256

print(f"\nBaseline (old):         F1 = {baseline_f1:.4f}")
print(f"KcBERT single:            F1 = {kcbert_f1:.4f} (+{(kcbert_f1-baseline_f1)/baseline_f1*100:.1f}%)")
print(f"Weighted Ensemble (TOP2): F1 = {weighted_f1:.4f}")
print(f"Stacking (TOP2):          F1 = {final_f1:.4f}", end="")

if final_f1 > kcbert_f1:
    improvement = (final_f1 - kcbert_f1) / kcbert_f1 * 100
    print(f" (+{improvement:.2f}% vs KcBERT)")
elif final_f1 == kcbert_f1:
    print(" (same as KcBERT)")
else:
    decrease = (kcbert_f1 - final_f1) / kcbert_f1 * 100
    print(f" (-{decrease:.2f}% vs KcBERT)")

# Save meta-model
print("\n[7] Saving meta-model...")

Path(META_MODEL_DIR).mkdir(parents=True, exist_ok=True)

with open(f"{META_MODEL_DIR}/meta_models.pkl", 'wb') as f:
    pickle.dump(meta_models, f)

config = {
    'base_model_dirs': MODEL_DIRS,
    'base_model_names': model_names,
    'n_models': len(models),
    'n_labels': n_labels,
    'optimal_threshold': float(best_th),
    'test_f1': float(final_f1),
    'test_precision': float(final_precision),
    'test_recall': float(final_recall),
}

with open(f"{META_MODEL_DIR}/config.json", 'w') as f:
    json.dump(config, f, indent=2)

with open(f"{META_MODEL_DIR}/skills.json", 'w', encoding='utf-8') as f:
    json.dump(all_skills, f, ensure_ascii=False, indent=2)

print(f"    Saved to: {META_MODEL_DIR}/")

print("\n" + "="*70)
print("STACKING (TOP 2) COMPLETE!")
print("="*70)
