"""
Stacking 메타 모델을 사용한 예측
학습된 메타 모델로 Wanted 데이터 예측
"""

import json
import torch
import numpy as np
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from tqdm import tqdm
import pickle
import os

print("=" * 70)
print("Step 3: Wanted Data Skill Prediction (Stacking TOP 2)")
print("=" * 70)

# ===== 설정 =====
WANTED_DIR = "./data/wanted/"
META_MODEL_DIR = "./models/meta_model_stacking_top2"
OUTPUT_DIR = "./data/wanted/wanted_predicted_stacking"
MAX_LENGTH = 256

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"\nDevice: {device}")

# ===== 1단계: 메타 모델 설정 로드 =====
print("\n[1] Loading meta-model configuration...")

if not Path(META_MODEL_DIR).exists():
    print(f"ERROR: Meta-model not found: {META_MODEL_DIR}")
    print("Please run train_stacking_top2.py first!")
    exit(1)

with open(f"{META_MODEL_DIR}/config.json", 'r') as f:
    config = json.load(f)

with open(f"{META_MODEL_DIR}/skills.json", 'r', encoding='utf-8') as f:
    all_skills = json.load(f)

with open(f"{META_MODEL_DIR}/meta_models.pkl", 'rb') as f:
    meta_models = pickle.load(f)

optimal_threshold = config['optimal_threshold']

print(f"    Base models: {config['n_models']}")
print(f"    Skills: {config['n_labels']}")
print(f"    Optimal threshold: {optimal_threshold:.2f}")
print(f"    Test F1: {config['test_f1']:.4f}")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ===== 2단계: Base 모델 로드 =====
print("\n[2] Loading base models...")

models = []
tokenizers = []

for i, model_dir in enumerate(config['base_model_dirs'], 1):
    print(f"    [{i}/{len(config['base_model_dirs'])}] {Path(model_dir).name}...")

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_dir)
        model = AutoModelForSequenceClassification.from_pretrained(model_dir)

        model.to(device)
        model.eval()

        tokenizers.append(tokenizer)
        models.append(model)

        print(f"        Loaded successfully")

    except Exception as e:
        print(f"        ERROR: {e}")
        exit(1)

print(f"\n    Total {len(models)} models loaded!")

# ===== 3단계: 원티드 파일 찾기 =====
print("\n[3] Searching for Wanted data files...")

wanted_files = list(Path(WANTED_DIR).glob("job_scraping_*.json"))

if not wanted_files:
    print(f"    ERROR: No files found!")
    exit()

print(f"    Found {len(wanted_files)} files")

# ===== 4단계: Stacking 예측 함수 =====
print("\n[4] Preparing stacking prediction function...")

def predict_skills_stacking(text):
    """
    Stacking 예측
    1. 모든 base 모델로 예측
    2. 예측 확률을 feature로 메타 모델 예측
    """
    if not text or not text.strip():
        return [], []

    # Base 모델 예측
    base_predictions = []

    for model, tokenizer in zip(models, tokenizers):
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
            base_predictions.append(probs)

    # Feature 준비: (n_models, n_labels) → (1, n_models * n_labels)
    stacking_features = np.concatenate(base_predictions).reshape(1, -1)

    # 메타 모델 예측
    meta_probs = np.zeros(len(all_skills))

    for label_idx, model in enumerate(meta_models):
        if model is not None:
            meta_probs[label_idx] = model.predict(stacking_features)[0]

    # Threshold 적용
    predicted_indices = (meta_probs > optimal_threshold).nonzero()[0]

    predicted_skills = []
    confidences = []

    for idx in predicted_indices:
        skill = all_skills[idx]
        confidence = float(meta_probs[idx])
        predicted_skills.append(skill)
        confidences.append(confidence)

    return predicted_skills, confidences

print("    Stacking prediction function ready!")

# ===== 5단계: 전체 파일 처리 =====
print("\n[5] Processing files with Stacking...")
print("\n" + "=" * 70)

total_jobs = 0
total_with_predictions = 0
all_predicted_skills = set()

for file_path in tqdm(wanted_files, desc="파일 처리"):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            jobs = json.load(f)

        for job in jobs:
            total_jobs += 1

            job_desc = job.get('job_description', {})

            text_parts = []
            if job_desc.get('position_detail'):
                text_parts.append(job_desc['position_detail'])
            if job_desc.get('main_tasks'):
                text_parts.append(job_desc['main_tasks'])
            if job_desc.get('requirements'):
                text_parts.append(job_desc['requirements'])
            if job_desc.get('preferred'):
                text_parts.append(job_desc['preferred'])

            full_text = ' '.join(text_parts)

            if full_text.strip():
                predicted_skills, confidences = predict_skills_stacking(full_text)

                if predicted_skills:
                    total_with_predictions += 1
                    all_predicted_skills.update(predicted_skills)

                    job['predicted_skills_stacking'] = predicted_skills
                    job['skill_confidences_stacking'] = {
                        skill: conf
                        for skill, conf in zip(predicted_skills, confidences)
                    }
                else:
                    job['predicted_skills_stacking'] = []
                    job['skill_confidences_stacking'] = {}
            else:
                job['predicted_skills_stacking'] = []
                job['skill_confidences_stacking'] = {}

        output_path = Path(OUTPUT_DIR) / file_path.name
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"\n    WARNING: Error processing {file_path.name}: {e}")
        continue

print("\n" + "=" * 70)
print("Stacking Prediction Results")
print("=" * 70)
print(f"Total jobs processed: {total_jobs:,}")
print(f"Jobs with predictions: {total_with_predictions:,} ({total_with_predictions/total_jobs*100:.1f}%)")
print(f"Unique skills predicted: {len(all_predicted_skills)}")
print("=" * 70)

# ===== 6단계: Top 스킬 =====
from collections import Counter
skill_counter = Counter()

for file_path in Path(OUTPUT_DIR).glob("*.json"):
    with open(file_path, 'r', encoding='utf-8') as f:
        jobs = json.load(f)
        for job in jobs:
            skill_counter.update(job.get('predicted_skills_stacking', []))

print("\n[6] Top 20 Most Predicted Skills (Stacking)...")
print("\n    Top 20:")
for rank, (skill, count) in enumerate(skill_counter.most_common(20), 1):
    print(f"      {rank:2d}. {skill}: {count} times")

print("\n" + "=" * 70)
print("STACKING PREDICTION COMPLETE!")
print("=" * 70)
print(f"\nSaved to: {OUTPUT_DIR}/")
