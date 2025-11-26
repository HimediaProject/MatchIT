"""
스크립트 2: BERT 모델 학습하기

목적: 공고 텍스트를 보고 스킬을 예측하는 AI 모델 만들기
방법: BERT를 Fine-tuning (기존 학습된 모델을 우리 데이터에 맞게 조정)

===== BERT란? =====
- Bidirectional Encoder Representations from Transformers
- Google이 만든 언어 이해 AI
- 이미 방대한 텍스트로 학습되어 있음

===== Fine-tuning이란? =====
비유: BERT = 대학 졸업생
      Fine-tuning = 회사 입사 후 업무 교육
      
이미 언어를 이해하는 BERT에게
"구인공고에서 스킬 찾는 법"만 가르치는 것!
"""
import json
import torch
import sys

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"\n💻 사용 디바이스: {device}")

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer
from transformers import (
    BertTokenizer,           # 텍스트를 숫자로 변환
    BertForSequenceClassification,  # BERT 분류 모델
    Trainer,                 # 학습 도우미
    TrainingArguments,       # 학습 설정
    EarlyStoppingCallback,   # 오버피팅 방지
)
from sklearn.metrics import f1_score, precision_score, recall_score
import os

# ✅ 추가!
sys.path.append('./scripts')  # focal_loss.py 경로
from focal_loss import FocalLoss, AsymmetricLoss
from threshold import DynamicThresholdCallback, find_best_threshold

print("=" * 70)
print("🎯 Step 2: BERT 모델 학습 시작!")
print("=" * 70)

# ===== 설정 =====
INPUT_FILE = "./data/remember/prepared_data.json"
MODEL_OUTPUT_DIR = "./models/model_output"

# 학습 하이퍼파라미터
BATCH_SIZE = 32          # 한 번에 몇 개씩 학습할지 (GPU 메모리에 따라)
LEARNING_RATE = 3e-5     # 2e-5 / 3e-5 / 5e-5    # 학습 속도 (너무 빠르면 불안정, 너무 느리면 시간 오래 걸림)
EPOCHS = 20              # 전체 데이터를 몇 번 반복할지
MAX_LENGTH = 256         # 텍스트 최대 길이 (긴 텍스트는 잘림)

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 42
FINAL_MODEL_DIR = f"./models/final_model_seed{SEED}"

THRESHOLD = 0.2
ALPHA = 0.75
GAMMA = 1.0

# 한국어 전용 모델
MODEL_NAME = "klue/roberta-base"

# 다국어 지원 모델
# MODEL_NAME = "bert-base-multilingual-cased"

print("\n📋 학습 설정:")
print(f"   Batch Size: {BATCH_SIZE}")
print(f"   Learning Rate: {LEARNING_RATE}")
print(f"   Epochs: {EPOCHS}")
print(f"   Max Text Length: {MAX_LENGTH}")
print(f"\n🎲 Random Seed: {SEED}")

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

"""
왜 숫자로 바꿔?
→ AI는 숫자만 이해함!

예시:
스킬: ['Python', 'Java']
→ [1, 1, 0, 0, 0, ...] (Python=1, Java=1, 나머지=0)

이걸 Multi-label Binarization이라고 함
"""

mlb = MultiLabelBinarizer()
mlb.fit(job['skills'] for job in jobs)  # 모든 스킬 학습

# 각 공고의 스킬을 0/1로 변환
texts = [job['text'] for job in jobs]
labels = [job['skills'] for job in jobs]
labels_binary = mlb.transform(labels)  # [[0,1,1,0,...], ...]

print(f"   ✅ 라벨 형태: {labels_binary.shape}")
print(f"   예시: {labels[0][:3]} → {labels_binary[0][:10]}")

# ===== 3단계: 데이터 분할 =====
print("\n3️⃣  Train/Validation/Test 분할...")

"""
왜 나눠?
→ 오버피팅 방지!

Train (70%): 학습용
Validation (15%): 학습 중 성능 체크
Test (15%): 최종 평가용

비유:
Train = 문제집 풀기
Validation = 모의고사 (학습 방향 조정)
Test = 수능 (최종 실력 측정)
"""

# 먼저 70% train, 30% temp
# ✅ 수정: 양성 샘플 증강
from imblearn.over_sampling import RandomOverSampler
from collections import Counter

print(f"\n🔍 클래스 불균형 확인:")
print(f"   1의 비율: {labels_binary.sum() / labels_binary.size * 100:.2f}%")

# 오버샘플링 (1이 있는 샘플 복제)
# 주의: Multi-label이라 직접 처리
positive_samples = []
for i, label_row in enumerate(labels_binary):
    if label_row.sum() > 0:  # 1이 하나라도 있으면
        positive_samples.append(i)

print(f"   양성 샘플: {len(positive_samples)}개")
print(f"   음성 샘플: {len(labels_binary) - len(positive_samples)}개")

# 양성 샘플 2배 복제
augmented_indices = list(range(len(texts))) + positive_samples
augmented_texts = [texts[i] for i in augmented_indices]
augmented_labels = labels_binary[augmented_indices]

print(f"   증강 후: {len(augmented_texts)}개")

# 이걸로 분할
train_texts, temp_texts, train_labels, temp_labels = train_test_split(
    augmented_texts, augmented_labels, test_size=0.3, random_state=SEED
)
# temp를 다시 반반 나눠서 val(15%), test(15%)
val_texts, test_texts, val_labels, test_labels = train_test_split(
    temp_texts, temp_labels, test_size=0.5, random_state=SEED
)

print(f"   ✅ Train: {len(train_texts)}개")
print(f"   ✅ Validation: {len(val_texts)}개")
print(f"   ✅ Test: {len(test_texts)}개")

# ===== 4단계: BERT 토크나이저 로드 =====
print("\n4️⃣  BERT 토크나이저 로딩...")

"""
토크나이저가 뭐야?
→ 텍스트를 BERT가 이해할 수 있는 숫자로 변환

예시:
"Python 개발자" → [101, 2512, 1234, 5678, 102]
(각 숫자는 단어/문자를 의미)

bert-base-multilingual-cased:
- 다국어 지원 (한국어 OK!)
- 자동으로 인터넷에서 다운로드됨

klue/roberta-base:
- 한국어 특화 모델
- Input(text)가 한국어 이므로, 한국어 특화 모델이 더 맞음
  (데이터양은 적음)
- 정답(skill stack)이 영어지만, 컴퓨터는 0, 1 로 생각함.
"""
# # 토크나이저와 모델 불러오기
print("   (처음 실행 시 인터넷에서 다운로드됩니다...)")

# 다국어 지원 모델로 할 때,
# tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)

# 한국어 전용 모델로 할 때,
tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
print(f'   ✅ 토크나이저 로드 완료!')
print(f'   💻 Model_name: {MODEL_NAME}')

# 토크나이징 (텍스트 → 숫자)
print("\n   텍스트를 숫자로 변환 중...")

train_encodings = tokenizer(
    train_texts,
    truncation=True,      # 긴 텍스트는 자르기
    padding=True,         # 짧은 텍스트는 패딩
    max_length=MAX_LENGTH,
    return_tensors='pt'   # PyTorch 형식으로
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

# ===== 5단계: Dataset 클래스 만들기 =====
print("\n5️⃣  Dataset 준비...")

"""
Dataset이 뭐야?
→ PyTorch가 데이터를 쉽게 사용할 수 있게 포장하는 것

비유: 도시락 싸기
- 데이터 = 재료
- Dataset = 도시락 (먹기 편하게 포장)
"""

class JobDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels
    
    def __len__(self):
        return len(self.labels)
    
    def __getitem__(self, idx):
        item = {key: val[idx] for key, val in self.encodings.items()}
        # ✅ labels도 float로 변환 (중요!)
        item['labels'] = torch.tensor(self.labels[idx], dtype=torch.float32)
        return item

train_dataset = JobDataset(train_encodings, train_labels)
val_dataset = JobDataset(val_encodings, val_labels)
test_dataset = JobDataset(test_encodings, test_labels)

print("   ✅ Dataset 생성 완료!")

# ===== 6단계: BERT 모델 로드 =====
print("\n6️⃣  BERT 모델 로딩...")

"""
여기가 핵심!
- bert-base-multilingual-cased: 사전학습된 BERT
- num_labels: 우리가 예측할 스킬 개수
- problem_type: multi_label (여러 개 동시 예측)

이 모델은 이미 언어를 이해함
우리는 마지막 레이어만 우리 스킬에 맞게 조정!
"""

print("   (처음 실행 시 약 500MB 다운로드됩니다...)")

model = BertForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=len(all_skills),
    problem_type="multi_label_classification"
)

model.to(device)  # ✅ GPU로 이동!

print("   ✅ 모델 로드 완료!")
print(f"   모델 크기: {sum(p.numel() for p in model.parameters()):,} parameters")

# ===== 7단계: 평가 함수 정의 =====
print("\n7️⃣  평가 함수 설정...")

"""
모델 성능을 어떻게 측정할까?

F1 Score: 정확도와 재현율의 조화평균
- 1.0 = 완벽
- 0.0 = 최악
- 0.8 이상이면 좋음

Precision (정밀도): 예측한 것 중 맞은 비율
Recall (재현율): 실제 정답 중 찾은 비율
"""

def compute_metrics(pred):
    """
    모델 성능 평가
    
    중요:
    - pred.predictions는 logits (sigmoid 전)
    - sigmoid 적용해서 0~1 확률로 변환 필요

    학습중:
    - 고정 threshold로 모니터링만
    """
    import torch
    
    # 1. Logits 가져오기
    logits = pred.predictions
    labels = pred.label_ids.astype(int)
    
    # 2. Sigmoid 적용 (logits → 확률)
    probs = torch.sigmoid(torch.tensor(logits)).numpy()

    # ✅ 고정 threshold (참고용)
    FIXED_THRESHOLD = 0.3
    predictions = (probs >= FIXED_THRESHOLD).astype(int)
    
    # 평가 지표 계산
    f1 = f1_score(labels, predictions, average='micro', zero_division=0)
    precision = precision_score(labels, predictions, average='micro', zero_division=0)
    recall = recall_score(labels, predictions, average='micro', zero_division=0)
    
    # 🔍 참고용으로만 최적 threshold 출력 (계산에는 안 씀!)
    if not hasattr(compute_metrics, 'call_count'):
        compute_metrics.call_count = 0
    compute_metrics.call_count += 1
    
    if compute_metrics.call_count <= 5:
        best_th, best_f1 = find_best_threshold(labels, probs)
        print(f"\n📊 [참고] 이 validation set에서 최적: threshold={best_th:.2f}, F1={best_f1:.4f}")
        print(f"    현재 사용 중 (고정): threshold={FIXED_THRESHOLD:.2f}, F1={f1:.4f}")
    
    return {
        'f1': f1,
        'precision': precision,
        'recall': recall
    }

# 학습 완료 후 실행하는 별도 스크립트
def find_optimal_threshold_final(model, test_dataset):
    """
    ⭐ 학습 끝난 후 딱 한 번만 실행!
    ⭐ Test set (또는 Hold-out Validation set) 사용
    """
    print("\n" + "="*60)
    print("🎯 최적 Threshold 탐색 시작")
    print("="*60)
    
    # 예측
    trainer = Trainer(model=model)
    predictions = trainer.predict(test_dataset)
    
    logits = predictions.predictions
    labels = predictions.label_ids
    probs = torch.sigmoid(torch.tensor(logits)).numpy()
    
    # 여러 threshold 시도
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
    
    # 최고 F1 찾기
    best_result = max(results, key=lambda x: x['f1'])
    
    print("\n" + "="*60)
    print(f"✅ 최종 선택: Threshold = {best_result['threshold']:.2f}")
    print(f"   F1        = {best_result['f1']:.4f}")
    print(f"   Recall    = {best_result['recall']:.4f}")
    print(f"   Precision = {best_result['precision']:.4f}")
    print("="*60)
    
    return best_result

class CustomTrainer(Trainer):
    """
    Focal Loss를 사용하는 커스텀 Trainer
    
    불균형 데이터 처리:
    - 기본 BCEWithLogitsLoss 대신 FocalLoss 사용
    - 어려운 샘플에 더 집중
    """
    
    def __init__(self, *args, loss_type='focal', **kwargs):
        super().__init__(*args, **kwargs)
        self.loss_type = loss_type
        
        # Loss 함수 선택
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
        """
        Loss 계산 (Focal Loss 적용)
        """
        # Labels 추출
        labels = inputs.pop("labels")
        
        # Forward pass
        outputs = model(**inputs)
        logits = outputs.logits
        
        # Loss 계산
        if self.loss_fn is not None:
            loss = self.loss_fn(logits, labels)
        else:
            # 기본 Loss
            loss_fct = torch.nn.BCEWithLogitsLoss()
            loss = loss_fct(logits, labels)
        
        return (loss, outputs) if return_outputs else loss

print("   ✅ 평가 함수 준비 완료!")

# ===== 8단계: 학습 설정 =====
print("\n8️⃣  학습 파라미터 설정...")

"""
TrainingArguments: 학습 방법 설정

중요한 것들:
- learning_rate: 학습 속도
- per_device_train_batch_size: 한 번에 처리할 양
- num_train_epochs: 반복 횟수
- evaluation_strategy: 언제 검증할지
- load_best_model_at_end: 가장 좋은 모델 저장
"""

training_args = TrainingArguments(
    output_dir=MODEL_OUTPUT_DIR,
    
    # 학습 설정
    learning_rate=LEARNING_RATE,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE * 2,  # 평가는 더 크게
    num_train_epochs=EPOCHS,
    
    # 평가 및 저장
    eval_strategy="epoch",         # 매 epoch마다 평가
    save_strategy="epoch",
    load_best_model_at_end=True,        # 최고 모델 저장
    metric_for_best_model="f1",         # F1이 높은 걸 선택
    
    # 로깅
    logging_dir='./logs',
    logging_steps=10,
    
    # 기타
    warmup_ratio=0.1,                   # 처음엔 천천히 학습: warmup_steps=100
    lr_scheduler_type='cosine',
    max_grad_norm=1.0,
    weight_decay=0.01,                  # 정규화
    report_to="none",                   # wandb 같은 거 안 씀
)

print("   ✅ 학습 설정 완료!")

# ===== 9단계: Trainer 생성 =====
print("\n9️⃣  Trainer 초기화...")

"""
Trainer: 학습을 쉽게 해주는 도구
- 자동으로 학습/검증 진행
- 최고 모델 저장
- 로그 기록
"""

trainer = CustomTrainer(  # ← Trainer → CustomTrainer
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=3)],
    loss_type='focal'  # ✅ 'focal' 또는 'asymmetric'
)

print("   ✅ Trainer 준비 완료!")

# ===== 10단계: 학습 시작! =====
print("\n" + "=" * 70)
print("🚀 학습 시작! (약 25~30분 소요)")
print("=" * 70)
print("\n💡 팁:")
print("   - Epoch마다 F1 Score 확인하세요")
print("   - Train Loss는 계속 줄어야 정상")
print("   - Validation F1이 안 오르면 오버피팅 의심")
print("\n" + "=" * 70)

trainer.train()

print("\n" + "=" * 70)
print("✅ 학습 완료!")
print("=" * 70)

# 2. 최적 threshold 찾기 (딱 한 번!)
print("\n" + "="*70)
print("🎯 Test Set으로 최적 Threshold 탐색")
print("="*70)
best_result = find_optimal_threshold_final(model, test_dataset)  # ✅ best_result로 받기
optimal_threshold = best_result['threshold']  # ✅ threshold 추출

# 3. 실제 서비스에 사용
def predict_new_job(job_text):
    logits = model(job_text)
    probs = torch.sigmoid(logits)
    predictions = (probs >= optimal_threshold).int()  # ← 고정값 사용!
    return predictions

print(f"\n✅ 최종 모델 준비 완료! (Threshold={optimal_threshold:.2f})")

# ===== 11단계: 최종 평가 =====
print("\n🔟 Test 데이터로 최종 평가...")

"""
Test 데이터: 학습 중 단 한 번도 안 본 데이터
→ 진짜 실력 측정!
"""

# ===== 12단계: 모델 저장 =====
print("\n1️⃣1️⃣  최종 모델 저장...")

os.makedirs(FINAL_MODEL_DIR, exist_ok=True)

# 모델과 토크나이저 저장
trainer.save_model(FINAL_MODEL_DIR)
tokenizer.save_pretrained(FINAL_MODEL_DIR)

# 1. 스킬 리스트 저장
with open(f"{FINAL_MODEL_DIR}/skills.json", 'w', encoding='utf-8') as f:
    json.dump(all_skills, f, ensure_ascii=False, indent=2)

# 2. 모델 설정 저장
config_path = f"{FINAL_MODEL_DIR}/model_config.json"
with open(config_path, 'w') as f:
    json.dump({
        'optimal_threshold': float(best_result['threshold']),
        'best_f1': float(best_result['f1']),
        'best_recall': float(best_result['recall']),
        'best_precision': float(best_result['precision'])
    }, f, indent=2)

print(f"   💾 Threshold 저장: {config_path}")

print(f"   ✅ 모델 저장 완료: {FINAL_MODEL_DIR}")

# ===== 13단계: 샘플 예측 테스트 =====
print("\n1️⃣2️⃣  샘플 예측 테스트...")

# 테스트 데이터에서 하나 가져오기
sample_text = test_texts[0]
sample_true_skills = [all_skills[i] for i, val in enumerate(test_labels[0]) if val == 1]

# Device 설정
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"\n   💻 사용 중인 디바이스: {device}")

# 샘플 예측
inputs = tokenizer(
    sample_text,
    truncation=True,
    padding=True,
    max_length=MAX_LENGTH,
    return_tensors='pt'
)

# ✅ 입력을 GPU로 이동!
inputs = {k: v.to(device) for k, v in inputs.items()}

model.eval()
model.to(device)  # ✅ 모델도 GPU로!

with torch.no_grad():
    outputs = model(**inputs)
    predictions = torch.sigmoid(outputs.logits)
    predicted_skills_idx = (predictions[0] > optimal_threshold).nonzero(as_tuple=True)[0]
    predicted_skills = [all_skills[idx] for idx in predicted_skills_idx]

print("\n   🔍 샘플 예측 결과:")
print(f"   텍스트: {sample_text[:100]}...")
print(f"   실제 스킬: {sample_true_skills}")
print(f"   예측 스킬: {predicted_skills}")

# ===== 완료! =====
print("\n" + "=" * 70)
print("🎉 모든 작업 완료!")
print("=" * 70)
print(f"\n저장된 파일:")
print(f"  - 모델: {FINAL_MODEL_DIR}/")
print(f"  - 스킬 리스트: {FINAL_MODEL_DIR}/skills.json")
print(f"\n다음 단계: 3_predict_wanted_ensemble.py 실행")
print("=" * 70)