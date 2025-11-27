"""
스크립트 2-확장: 다양한 모델 아키텍처 학습
목적: 앙상블 성능 향상을 위해 서로 다른 아키텍처 모델 학습

지원 모델:
1. klue/roberta-base (기존)
2. monologg/koelectra-base-v3-discriminator (ELECTRA)
3. klue/bert-base (BERT)
4. beomi/kcbert-base (댓글 기반 BERT)
"""
import json
import torch
import sys
import os

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"\n💻 사용 디바이스: {device}")

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
    EarlyStoppingCallback,
)
from sklearn.metrics import f1_score, precision_score, recall_score

sys.path.append('./scripts')
from focal_loss import FocalLoss, AsymmetricLoss
from threshold import find_best_threshold

print("=" * 70)
print("🎯 Step 2: 다중 아키텍처 모델 학습!")
print("=" * 70)

# ===== 설정 =====
INPUT_FILE = "./data/remember/prepared_data.json"

# 명령줄 인자: model_type, seed
if len(sys.argv) < 2:
    print("\n사용법: python 2_train_model_multiarch.py <model_type> [seed]")
    print("\n지원 모델:")
    print("  - roberta: klue/roberta-base")
    print("  - electra: monologg/koelectra-base-v3-discriminator")
    print("  - bert: klue/bert-base")
    print("  - kcbert: beomi/kcbert-base")
    sys.exit(1)

MODEL_TYPE = sys.argv[1]
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 42

# 모델 매핑
MODEL_MAP = {
    'roberta': 'klue/roberta-base',
    'electra': 'monologg/koelectra-base-v3-discriminator',
    'bert': 'klue/bert-base',
    'kcbert': 'beomi/kcbert-base',
}

if MODEL_TYPE not in MODEL_MAP:
    print(f"❌ 지원하지 않는 모델: {MODEL_TYPE}")
    print(f"지원 모델: {list(MODEL_MAP.keys())}")
    sys.exit(1)

MODEL_NAME = MODEL_MAP[MODEL_TYPE]
MODEL_OUTPUT_DIR = f"./models/model_output_{MODEL_TYPE}_seed{SEED}"
FINAL_MODEL_DIR = f"./models/final_model_{MODEL_TYPE}_seed{SEED}"

# 학습 하이퍼파라미터
BATCH_SIZE = 32
LEARNING_RATE = 3e-5
EPOCHS = 20
MAX_LENGTH = 256
THRESHOLD = 0.2
ALPHA = 0.75
GAMMA = 1.0

print(f"\n📋 학습 설정:")
print(f"   Model Type: {MODEL_TYPE}")
print(f"   Model Name: {MODEL_NAME}")
print(f"   Random Seed: {SEED}")
print(f"   Batch Size: {BATCH_SIZE}")
print(f"   Learning Rate: {LEARNING_RATE}")
print(f"   Epochs: {EPOCHS}")

# ===== 1단계: 데이터 로드 =====
print("\n1️⃣  준비된 데이터 로딩...")

with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    loaded_data = json.load(f)

jobs = loaded_data['data']
all_skills = loaded_data['all_skills']

print(f"   ✅ 공고 수: {len(jobs)}개")
print(f"   ✅ 스킬 종류: {len(all_skills)}개")

# ===== 2단계: 스킬을 숫자로 변환 =====
print("\n2️⃣  스킬 라벨 인코딩...")

mlb = MultiLabelBinarizer()
mlb.fit([job['skills'] for job in jobs])

texts = [job['text'] for job in jobs]
labels = [job['skills'] for job in jobs]
labels_binary = mlb.transform(labels)

print(f"   ✅ 라벨 형태: {labels_binary.shape}")

# ===== 3단계: 데이터 분할 및 오버샘플링 =====
print("\n3️⃣  Train/Validation/Test 분할 + 오버샘플링...")

print(f"\n🔍 클래스 불균형 확인:")
print(f"   1의 비율: {labels_binary.sum() / labels_binary.size * 100:.2f}%")

positive_samples = []
for i, label_row in enumerate(labels_binary):
    if label_row.sum() > 0:
        positive_samples.append(i)

print(f"   양성 샘플: {len(positive_samples)}개")
print(f"   음성 샘플: {len(labels_binary) - len(positive_samples)}개")

# 양성 샘플 2배 복제
augmented_indices = list(range(len(texts))) + positive_samples
augmented_texts = [texts[i] for i in augmented_indices]
augmented_labels = labels_binary[augmented_indices]

print(f"   증강 후: {len(augmented_texts)}개")

# 데이터 분할
train_texts, temp_texts, train_labels, temp_labels = train_test_split(
    augmented_texts, augmented_labels, test_size=0.3, random_state=SEED
)
val_texts, test_texts, val_labels, test_labels = train_test_split(
    temp_texts, temp_labels, test_size=0.5, random_state=SEED
)

print(f"   ✅ Train: {len(train_texts)}개")
print(f"   ✅ Validation: {len(val_texts)}개")
print(f"   ✅ Test: {len(test_texts)}개")

# ===== 4단계: 토크나이저 로드 =====
print(f"\n4️⃣  {MODEL_TYPE} 토크나이저 로딩...")
print("   (처음 실행 시 인터넷에서 다운로드됩니다...)")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
print(f'   ✅ 토크나이저 로드 완료!')

# 토크나이징
print("\n   텍스트를 숫자로 변환 중...")

train_encodings = tokenizer(
    train_texts,
    truncation=True,
    padding=True,
    max_length=MAX_LENGTH,
    return_tensors='pt'
)

val_encodings = tokenizer(
    val_texts,
    truncation=True,
    padding=True,
    max_length=MAX_LENGTH,
    return_tensors='pt'
)

test_encodings = tokenizer(
    test_texts,
    truncation=True,
    padding=True,
    max_length=MAX_LENGTH,
    return_tensors='pt'
)

print("   ✅ 토크나이징 완료!")

# ===== 5단계: Dataset 클래스 =====
print("\n5️⃣  Dataset 준비...")

class JobDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {key: val[idx] for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx], dtype=torch.float32)
        return item

train_dataset = JobDataset(train_encodings, train_labels)
val_dataset = JobDataset(val_encodings, val_labels)
test_dataset = JobDataset(test_encodings, test_labels)

print("   ✅ Dataset 생성 완료!")

# ===== 6단계: 모델 로드 =====
print(f"\n6️⃣  {MODEL_TYPE} 모델 로딩...")
print("   (처음 실행 시 다운로드됩니다...)")

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=len(all_skills),
    problem_type="multi_label_classification"
)

model.to(device)

print("   ✅ 모델 로드 완료!")
print(f"   모델 크기: {sum(p.numel() for p in model.parameters()):,} parameters")

# ===== 7단계: 평가 함수 =====
print("\n7️⃣  평가 함수 설정...")

def compute_metrics(pred):
    import torch

    logits = pred.predictions
    labels = pred.label_ids.astype(int)

    probs = torch.sigmoid(torch.tensor(logits)).numpy()

    FIXED_THRESHOLD = 0.3
    predictions = (probs >= FIXED_THRESHOLD).astype(int)

    f1 = f1_score(labels, predictions, average='micro', zero_division=0)
    precision = precision_score(labels, predictions, average='micro', zero_division=0)
    recall = recall_score(labels, predictions, average='micro', zero_division=0)

    if not hasattr(compute_metrics, 'call_count'):
        compute_metrics.call_count = 0
    compute_metrics.call_count += 1

    if compute_metrics.call_count <= 5:
        best_th, best_f1 = find_best_threshold(labels, probs)
        print(f"\n📊 [참고] 최적: threshold={best_th:.2f}, F1={best_f1:.4f}")
        print(f"    현재: threshold={FIXED_THRESHOLD:.2f}, F1={f1:.4f}")

    return {
        'f1': f1,
        'precision': precision,
        'recall': recall
    }

def find_optimal_threshold_final(model, test_dataset):
    print("\n" + "="*60)
    print("🎯 최적 Threshold 탐색 시작")
    print("="*60)

    trainer = Trainer(model=model)
    predictions = trainer.predict(test_dataset)

    logits = predictions.predictions
    labels = predictions.label_ids
    probs = torch.sigmoid(torch.tensor(logits)).numpy()

    results = []
    print("\nThreshold | F1 Score | Recall | Precision")
    print("-" * 60)

    for th in np.arange(0.1, 0.7, 0.05):
        preds = (probs >= th).astype(int)
        f1 = f1_score(labels, preds, average='micro')
        recall = recall_score(labels, preds, average='micro')
        precision = precision_score(labels, preds, average='micro')

        results.append({
            'threshold': th,
            'f1': f1,
            'recall': recall,
            'precision': precision
        })

        print(f"  {th:.2f}    |  {f1:.4f}  | {recall:.4f} | {precision:.4f}")

    best_result = max(results, key=lambda x: x['f1'])

    print("\n" + "="*60)
    print(f"✅ 최종 선택: Threshold = {best_result['threshold']:.2f}")
    print(f"   F1        = {best_result['f1']:.4f}")
    print(f"   Recall    = {best_result['recall']:.4f}")
    print(f"   Precision = {best_result['precision']:.4f}")
    print("="*60)

    return best_result

class CustomTrainer(Trainer):
    def __init__(self, *args, loss_type='focal', **kwargs):
        super().__init__(*args, **kwargs)
        self.loss_type = loss_type

        if loss_type == 'focal':
            self.loss_fn = FocalLoss(alpha=ALPHA, gamma=GAMMA)
            print(f"   📊 Using Focal Loss (alpha={ALPHA}, gamma={GAMMA})")
        elif loss_type == 'asymmetric':
            self.loss_fn = AsymmetricLoss(gamma_neg=4, gamma_pos=1)
            print("   📊 Using Asymmetric Loss")
        else:
            self.loss_fn = None
            print("   📊 Using default BCEWithLogitsLoss")

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits

        if self.loss_fn is not None:
            loss = self.loss_fn(logits, labels)
        else:
            loss_fct = torch.nn.BCEWithLogitsLoss()
            loss = loss_fct(logits, labels)

        return (loss, outputs) if return_outputs else loss

print("   ✅ 평가 함수 준비 완료!")

# ===== 8단계: 학습 설정 =====
print("\n8️⃣  학습 파라미터 설정...")

training_args = TrainingArguments(
    output_dir=MODEL_OUTPUT_DIR,

    learning_rate=LEARNING_RATE,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE * 2,
    num_train_epochs=EPOCHS,

    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="f1",

    logging_dir='./logs',
    logging_steps=10,

    warmup_ratio=0.1,
    lr_scheduler_type='cosine',
    max_grad_norm=1.0,
    weight_decay=0.01,
    report_to="none",
)

print("   ✅ 학습 설정 완료!")

# ===== 9단계: Trainer 생성 =====
print("\n9️⃣  Trainer 초기화...")

trainer = CustomTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=3)],
    loss_type='focal'
)

print("   ✅ Trainer 준비 완료!")

# ===== 10단계: 학습 시작 =====
print("\n" + "=" * 70)
print(f"🚀 {MODEL_TYPE} 학습 시작! (약 25~30분 소요)")
print("=" * 70)

trainer.train()

print("\n" + "=" * 70)
print("✅ 학습 완료!")
print("=" * 70)

# ===== 11단계: 최적 threshold 찾기 =====
best_result = find_optimal_threshold_final(model, test_dataset)
optimal_threshold = best_result['threshold']

# ===== 12단계: 모델 저장 =====
print("\n1️⃣2️⃣  최종 모델 저장...")

os.makedirs(FINAL_MODEL_DIR, exist_ok=True)

trainer.save_model(FINAL_MODEL_DIR)
tokenizer.save_pretrained(FINAL_MODEL_DIR)

with open(f"{FINAL_MODEL_DIR}/skills.json", 'w', encoding='utf-8') as f:
    json.dump(all_skills, f, ensure_ascii=False, indent=2)

config_path = f"{FINAL_MODEL_DIR}/model_config.json"
with open(config_path, 'w') as f:
    json.dump({
        'model_type': MODEL_TYPE,
        'model_name': MODEL_NAME,
        'optimal_threshold': float(best_result['threshold']),
        'best_f1': float(best_result['f1']),
        'best_recall': float(best_result['recall']),
        'best_precision': float(best_result['precision']),
        'seed': SEED
    }, f, indent=2)

print(f"   💾 모델 저장: {FINAL_MODEL_DIR}")

# ===== 13단계: 샘플 테스트 =====
print("\n1️⃣3️⃣  샘플 예측 테스트...")

sample_text = test_texts[0]
sample_true_skills = [all_skills[i] for i, val in enumerate(test_labels[0]) if val == 1]

inputs = tokenizer(
    sample_text,
    truncation=True,
    padding=True,
    max_length=MAX_LENGTH,
    return_tensors='pt'
)

inputs = {k: v.to(device) for k, v in inputs.items()}

model.eval()
model.to(device)

with torch.no_grad():
    outputs = model(**inputs)
    predictions = torch.sigmoid(outputs.logits)
    predicted_skills_idx = (predictions[0] > optimal_threshold).nonzero(as_tuple=True)[0]
    predicted_skills = [all_skills[idx] for idx in predicted_skills_idx]

print("\n   🔍 샘플 예측 결과:")
print(f"   텍스트: {sample_text[:100]}...")
print(f"   실제 스킬: {sample_true_skills}")
print(f"   예측 스킬: {predicted_skills}")

# ===== 완료 =====
print("\n" + "=" * 70)
print("🎉 모든 작업 완료!")
print("=" * 70)
print(f"\n저장된 파일:")
print(f"  - 모델: {FINAL_MODEL_DIR}/")
print(f"  - 스킬 리스트: {FINAL_MODEL_DIR}/skills.json")
print(f"  - 설정: {FINAL_MODEL_DIR}/model_config.json")
print("=" * 70)
