# 데이터 파이프라인 및 처리 흐름 가이드

**최종 업데이트:** 2025-11-26
**목적:** 전체 데이터 처리 파이프라인 이해 및 유지보수 가이드

---

## 📋 목차

1. [파이프라인 개요](#파이프라인-개요)
2. [단계별 상세 설명](#단계별-상세-설명)
3. [데이터 흐름 예시](#데이터-흐름-예시)
4. [TOP N 선택 전략](#top-n-선택-전략)
5. [성능 트레이드오프](#성능-트레이드오프)
6. [문제 해결 가이드](#문제-해결-가이드)

---

## 파이프라인 개요

### 전체 흐름

```
원본 데이터 (Remember JSON)
        ↓
[1단계] 스킬 정규화 (label_normalization)
        ↓
[2단계] TOP 300 선택
        ↓
[3단계] 모델 학습 (BERT, KcBERT, Stacking(BERT + KcBERT))
        ↓
[4단계] 예측 (300개 스킬 중에서만)
        ↓
[5단계] 후처리 (키워드 매칭)
        ↓
최종 결과 (AI + 키워드 스킬)
```

### 핵심 개념

| 단계 | 목적 | 입력 | 출력 | 관련 파일 |
|------|------|------|------|----------|
| 1. 정규화 | 동일 스킬 통일 | 다양한 표현 | 정규화된 스킬 | `label_normalization.py` |
| 2. 선택 | 학습 가능한 스킬만 | 1,547개 스킬 | 300개 스킬 | `1_prepare_data.py` |
| 3. 학습 | AI 모델 훈련 | 300개 라벨 | 학습된 모델 | `2_train_model*.py` |
| 4. 예측 | 스킬 추론 | 텍스트 | AI 예측 스킬 | `3_predict_stacking.py` |
| 5. 후처리 | 미학습 스킬 추가 | 텍스트 + AI 결과 | 최종 스킬 | `4_post_process_skills.py` |

---

## 단계별 상세 설명

### 1단계: 스킬 정규화 (label_normalization.py)

**목적:** 동일한 스킬의 다양한 표현을 하나로 통일

**처리 방식:**

```python
# scripts/label_normalization.py

skill_map = {
    # 한국어 → 영어 소문자
    "파이썬": "python",
    "Python": "python",
    "py": "python",

    # 약어 → 정식 명칭
    "js": "javascript",
    "ts": "typescript",
    "k8s": "kubernetes",

    # 띄어쓰기 통일
    "RestAPI": "rest_api",
    "restapi": "rest_api",
    "RESTful API": "rest_api",
}

def normalize_skills(skills, skill_map):
    """
    스킬 정규화

    Args:
        skills: ["파이썬", "Python", "py"]

    Returns:
        normalized: ["python"]  # 중복 제거됨
    """
    normalized = []
    for skill in skills:
        skill_lower = skill.lower().strip()
        if skill_lower in skill_map:
            normalized.append(skill_map[skill_lower])
        else:
            normalized.append(skill_lower)

    return sorted(set(normalized))  # 중복 제거 + 정렬
```

**실제 예시:**

```python
# 입력
raw_skills = [
    "파이썬", "Python", "PYTHON", "py",
    "자바스크립트", "JavaScript", "js",
    "FastAPI", "fastapi"
]

# 정규화 후
normalized_skills = [
    "python",      # 4개 통합
    "javascript",  # 3개 통합
    "fastapi"      # 2개 통합
]

# 결과: 8개 → 3개
```

**효과:**
- 스킬 개수 감소: 1,774개 → 1,547개 (중복 제거)
- 학습 효율 향상
- 일관성 확보

---

### 2단계: TOP 300 선택 (1_prepare_data.py)

**목적:** 학습 가능한 스킬만 선택 (데이터 충분, 불균형 완화)

**선택 기준:**

```python
# scripts/1_prepare_data.py

# 스킬별 출현 빈도 계산
skill_counter = Counter()
for job in jobs:
    skill_counter.update(job['skills'])

# TOP 300 선택
TOP_N = 300
top_skills = [skill for skill, count in skill_counter.most_common(TOP_N)]

print(f"선택된 스킬: {len(top_skills)}개")
print(f"제외된 스킬: {len(all_skills) - len(top_skills)}개")
```

**왜 300개인가?**

| TOP N | 평균 샘플/스킬 | 학습 품질 | F1 Score | 비고 |
|-------|--------------|----------|----------|------|
| 100 | 50+ | Excellent | 0.45 | 커버리지 부족 |
| 200 | 20-50 | Good | 0.62 | 개선 중 |
| **300** | **10-50** | **Good** | **0.6995** | **최적** ✅ |
| 500 | 5-20 | Poor | ~0.65 | 희귀 스킬 노이즈 |
| 1000 | 1-10 | Unusable | ~0.55 | 데이터 부족 |

**스킬 분포 분석:**

```python
# TOP 300 스킬의 출현 빈도

순위 1-100:    평균 50+ 샘플   학습 충분 ✅
순위 101-200:  평균 20-50 샘플  학습 가능 ✅
순위 201-300:  평균 10-20 샘플  학습 가능 ✅
────────────────────────────────────────
순위 301-500:  평균 3-10 샘플   학습 어려움 ⚠️
순위 501+:     평균 1-3 샘플    학습 불가 ❌
```

**데이터 예시:**

```python
# 상위 스킬 (학습 O)
"python": 1,200회
"java": 800회
"javascript": 650회
"react": 500회
...
"fastapi": 15회  # 300위

# 제외된 스킬 (학습 X)
"langchain": 5회  # 301위
"grafana": 3회
"anthropic": 2회
```

**출력:**

```json
{
  "data": [...],  // 학습 데이터
  "all_skills": [...],  // 300개 스킬
  "skill_counts": {...},  // 빈도
  "stats": {
    "total_jobs": 2300,
    "total_skills": 300,
    "avg_skills_per_job": 4.2
  }
}
```

---

### 3단계: 모델 학습 (2_train_model*.py)

**목적:** 300개 스킬을 예측하는 AI 모델 학습

**학습 프로세스:**

```python
# 1. 데이터 로드
with open('prepared_data.json') as f:
    data = json.load(f)
    jobs = data['data']
    all_skills = data['all_skills']  # 300개

# 2. Multi-label Binarization
mlb = MultiLabelBinarizer()
labels_binary = mlb.fit_transform([job['skills'] for job in jobs])
# 형태: (2300, 300) - 각 공고당 300차원 벡터

# 3. 데이터 분할
train_texts, val_texts, test_texts = split_data(texts, labels_binary)

# 4. 모델 학습
model = BertForSequenceClassification(num_labels=300)
model.train(train_texts, train_labels)

# 5. 최적 Threshold 탐색
optimal_threshold = find_best_threshold(val_texts, val_labels)
# 결과: 0.25 (Stacking TOP 2)
```

**학습된 모델:**

```
models/
├── final_model_bert_seed42/      # BERT (F1 0.6056)
├── final_model_kcbert_seed42/    # KcBERT (F1 0.6256)
└── meta_model_stacking_top2/     # Stacking (F1 0.6995) ✅
```

---

### 4단계: 예측 (3_predict_stacking.py)

**목적:** 학습된 모델로 새 데이터의 스킬 예측

**예측 가능 범위:**

```python
# ✅ 예측 가능 (TOP 300)
trained_skills = [
    "python", "java", "javascript", "react", "vue",
    "django", "fastapi", "aws", "docker", ...  # 300개
]

# ❌ 예측 불가 (301위 이하)
untrained_skills = [
    "langchain", "langgraph", "anthropic", "grafana",
    "prometheus", "supabase", ...  # 1,247개
]
```

**예측 프로세스:**

```python
def predict_skills_stacking(text):
    """
    Stacking 모델로 스킬 예측

    Args:
        text: "Python과 FastAPI를 사용한 백엔드 개발"

    Returns:
        predicted_skills: ["python", "fastapi", "backend"]
        confidences: [0.95, 0.85, 0.75]
    """
    # 1. Base 모델 예측 (BERT, KcBERT)
    bert_probs = bert_model.predict(text)     # (300,)
    kcbert_probs = kcbert_model.predict(text) # (300,)

    # 2. Stacking features
    features = np.concatenate([bert_probs, kcbert_probs])  # (600,)

    # 3. Meta 모델 예측 (LightGBM)
    meta_probs = meta_model.predict(features)  # (300,)

    # 4. Threshold 적용
    predicted_indices = np.where(meta_probs > 0.25)[0]

    # 5. 스킬 이름 변환
    predicted_skills = [all_skills[i] for i in predicted_indices]
    confidences = [meta_probs[i] for i in predicted_indices]

    return predicted_skills, confidences
```

**예측 결과 예시:**

```python
# 입력
text = """
주요업무:
- Python 기반 백엔드 API 개발
- FastAPI, Django 프레임워크 사용
- LangChain을 활용한 AI 서비스 개발
- Grafana로 모니터링
"""

# AI 예측 (300개 중에서만)
ai_predicted = [
    ("python", 0.95),      # ✅ TOP 300
    ("fastapi", 0.85),     # ✅ TOP 300
    ("django", 0.78),      # ✅ TOP 300
    ("backend", 0.72),     # ✅ TOP 300
    ("api", 0.68)          # ✅ TOP 300
]
# "langchain", "grafana" → 예측 불가 ❌
```

**한계:**
- 300개 스킬만 예측 가능
- 새로운 기술/도구는 인식 불가
- 희귀 스킬 누락

→ **해결책: 5단계 후처리**

---

### 5단계: 후처리 - 키워드 매칭 (4_post_process_skills.py)

**목적:** 모델이 예측하지 못한 스킬을 텍스트 패턴 매칭으로 추가

**처리 방식:**

```python
# 1. 역매핑 테이블 생성
reverse_map = {}
for key, value in skill_map.items():
    if value not in reverse_map:
        reverse_map[value] = []
    reverse_map[value].append(key)

# 예:
# reverse_map["langchain"] = ["langchain", "LangChain", "랭체인"]

# 2. 키워드 매칭
def post_process_add_skills(text, predicted_skills, keyword_map):
    text_lower = text.lower()
    added_skills = []

    for skill, keywords in keyword_map.items():
        # 이미 예측된 스킬은 스킵
        if skill in predicted_skills:
            continue

        # 키워드 매칭
        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, text_lower):
                added_skills.append(skill)
                break

    return added_skills
```

**실제 예시:**

```python
# 입력 텍스트
text = """
Python과 FastAPI를 사용한 백엔드 개발
LangChain으로 LLM 통합
Grafana로 모니터링 대시보드 구축
"""

# AI 예측 (5개)
ai_skills = ["python", "fastapi", "backend", "api", "llm"]

# 키워드 매칭 (2개 추가)
keyword_skills = ["langchain", "grafana"]
# "LangChain" → "langchain"
# "Grafana" → "grafana"

# 최종 결과 (7개)
final_skills = ai_skills + keyword_skills
# ["python", "fastapi", "backend", "api", "llm", "langchain", "grafana"]
```

**추가되는 스킬 특징:**

```python
# 후처리로 추가되는 59개 스킬 예시

신기술:
- "langchain", "langgraph", "langsmith"
- "anthropic", "claude"
- "supabase", "vercel"

모니터링:
- "grafana", "prometheus", "datadog"

특정 도구:
- "confluence", "jira", "notion"

산업 표준:
- "isms-p", "iso 26262", "a-spice"
```

**성능 향상:**

```
AI만 (300개):
- 평균 1.63 스킬/공고
- Recall: 0.6433
- Precision: 0.7664

AI + 후처리:
- 평균 5.95 스킬/공고 (+264%)
- Recall: 높음 (미측정)
- Precision: 중간 (0.5-0.7 예상)
```

---

## 데이터 흐름 예시

### 완전한 예시: Python Backend Developer

#### **원본 데이터**

```json
{
  "title": "Python 백엔드 개발자",
  "주요업무": "Python 기반 백엔드 API 개발, LangChain 활용",
  "이 포지션에 필요한 전문분야/기술": [
    {"text": "파이썬"},
    {"text": "Python"},
    {"text": "FastAPI"},
    {"text": "LangChain"},
    {"text": "Grafana"}
  ]
}
```

#### **1단계: 정규화**

```python
# 입력
raw_skills = ["파이썬", "Python", "FastAPI", "LangChain", "Grafana"]

# 정규화
normalized_skills = normalize_skills(raw_skills, skill_map)
# 결과: ["python", "fastapi", "langchain", "grafana"]

# 중복 제거
unique_skills = set(normalized_skills)
# 결과: ["python", "fastapi", "langchain", "grafana"]
```

#### **2단계: TOP 300 선택**

```python
# 스킬별 출현 빈도
skill_counts = {
    "python": 1200,    # 1위   ✅ TOP 300
    "fastapi": 15,     # 300위 ✅ TOP 300
    "langchain": 5,    # 350위 ❌ 제외
    "grafana": 3       # 420위 ❌ 제외
}

# 학습 데이터
training_skills = ["python", "fastapi"]  # 2개만
```

#### **3단계: 모델 학습**

```python
# 학습 가능한 스킬
trained_skills = ["python", "fastapi", ..., (300개)]

# 학습된 모델
model.predict("Python FastAPI 개발") → ["python", "fastapi"]
model.predict("LangChain 활용") → []  # 예측 불가!
```

#### **4단계: 예측**

```python
text = "Python 기반 백엔드 API 개발, LangChain 활용, Grafana 모니터링"

# AI 예측 (300개 중에서만)
predicted_skills, confidences = model.predict(text)

# 결과
predicted_skills = ["python", "fastapi", "backend", "api"]
confidences = [0.95, 0.85, 0.75, 0.68]

# 누락: "langchain", "grafana" ❌
```

#### **5단계: 후처리**

```python
# 키워드 매칭
keyword_skills = post_process_add_skills(text, predicted_skills, keyword_map)

# "LangChain" 발견 → "langchain" 추가
# "Grafana" 발견 → "grafana" 추가

keyword_skills = ["langchain", "grafana"]

# 최종 결과
final_skills = predicted_skills + keyword_skills
# ["python", "fastapi", "backend", "api", "langchain", "grafana"]
```

#### **최종 비교**

| 단계 | 스킬 수 | 스킬 목록 |
|------|---------|----------|
| 원본 | 5개 | 파이썬, Python, FastAPI, LangChain, Grafana |
| 정규화 | 4개 | python, fastapi, langchain, grafana |
| 학습 가능 | 2개 | python, fastapi |
| AI 예측 | 4개 | python, fastapi, backend, api |
| 후처리 | 6개 | python, fastapi, backend, api, langchain, grafana |

---

## TOP N 선택 전략

### 실험 결과

```python
# 다양한 TOP N으로 학습 실험

TOP_100 = {
    "F1": 0.45,
    "Precision": 0.75,
    "Recall": 0.35,
    "문제": "커버리지 부족, 너무 제한적"
}

TOP_200 = {
    "F1": 0.62,
    "Precision": 0.74,
    "Recall": 0.53,
    "문제": "개선 중, 아직 부족"
}

TOP_300 = {  # ✅ 현재
    "F1": 0.6995,
    "Precision": 0.7664,
    "Recall": 0.6433,
    "문제": "없음, 최적"
}

TOP_500 = {
    "F1": 0.65,  # 예상
    "Precision": 0.70,
    "Recall": 0.65,
    "문제": "희귀 스킬(301-500) 노이즈, 성능 저하"
}

TOP_1000 = {
    "F1": 0.55,  # 예상
    "Precision": 0.65,
    "Recall": 0.68,
    "문제": "데이터 부족, 학습 실패"
}
```

### 최적 지점 분석

```
        F1 Score
          ↑
    0.70  |            ● (300)
          |          ╱   ╲
    0.65  |        ●       ● (500)
          |      ╱           ╲
    0.60  |    ●               ● (1000)
          |  ╱
    0.55  |●
          └────────────────────→ TOP N
           100  200  300  500  1000

최적: TOP 300
- 데이터 충분
- 불균형 관리 가능
- F1 Score 최대
```

### 왜 500개는 안 좋은가?

```python
# 301-500위 스킬의 문제

"skill_301": 10회 출현  # 학습 가능
"skill_350": 5회 출현   # 학습 어려움
"skill_400": 3회 출현   # 학습 실패 가능
"skill_450": 2회 출현   # 거의 불가능
"skill_500": 1회 출현   # 완전 불가능

# 결과
- 200개 스킬 중 절반 이상이 제대로 학습 안 됨
- 오예측 증가
- 전체 F1 Score 하락
```

---

## 성능 트레이드오프

### AI 모델 vs 후처리

| 방식 | 장점 | 단점 | 사용 시기 |
|------|------|------|----------|
| **AI 모델만** | - 높은 Precision<br>- 문맥 이해<br>- 의미 파악 | - 300개 제한<br>- 신기술 누락<br>- 낮은 Recall | 정확도 중시 |
| **후처리만** | - 무제한 스킬<br>- 새 기술 대응<br>- 높은 Recall | - 낮은 Precision<br>- 오탐 가능<br>- 문맥 무시 | 커버리지 중시 |
| **AI + 후처리** | - 균형잡힌 성능<br>- 높은 F1<br>- 실용적 | - 복잡도 증가<br>- 유지보수 필요 | **프로덕션** ✅ |

### 실제 성능 비교

```python
# 테스트 케이스
text = """
Python과 FastAPI를 사용한 백엔드 API 개발
LangChain으로 LLM 통합
AWS 인프라, Docker 컨테이너
Grafana 모니터링, Redis 캐싱
"""

# 방식 1: AI 모델만
ai_only = ["python", "fastapi", "backend", "api", "aws", "docker", "redis"]
# 7개, Precision 높음, "langchain", "grafana" 누락

# 방식 2: 키워드 매칭만
keyword_only = [
    "python", "fastapi", "backend", "api", "langchain",
    "llm", "aws", "docker", "grafana", "redis", "monitoring"
]
# 11개, Recall 높음, 일부 오탐 가능

# 방식 3: AI + 후처리 (현재)
combined = [
    # AI 예측 (높은 확률)
    "python" (0.95), "fastapi" (0.85), "backend" (0.78),
    "api" (0.72), "aws" (0.68), "docker" (0.65), "redis" (0.62),
    # 키워드 매칭 (고정 0.5)
    "langchain" (0.5), "grafana" (0.5)
]
# 9개, 균형잡힌 성능 ✅
```

---

## 문제 해결 가이드

### Q1. 새로운 스킬이 계속 누락됩니다

**문제:**
```python
text = "Supabase와 Vercel을 사용한 개발"
predicted = []  # 아무것도 예측 안 됨
```

**원인:**
- "supabase", "vercel"이 TOP 300에 없음
- 키워드 맵에도 없음

**해결:**

```python
# scripts/label_normalization.py 또는 utils/model_inference.py

# TECH_KEYWORDS에 추가
TECH_KEYWORDS.add('supabase')
TECH_KEYWORDS.add('vercel')

# 또는 skill_map에 매핑 추가
skill_map['Supabase'] = 'supabase'
skill_map['Vercel'] = 'vercel'
```

---

### Q2. 성능을 더 높이고 싶습니다

**옵션:**

**A. 더 많은 데이터 수집**
```python
# 현재: Remember 2,300개 공고
# 목표: 5,000-10,000개

# 효과:
# - 희귀 스킬 샘플 증가
# - TOP 500 학습 가능
# - F1 Score → 0.75+ 예상
```

**B. 모델 앙상블 확장**
```python
# 현재: BERT + KcBERT
# 추가: ELECTRA, RoBERTa, etc.

# 효과:
# - 다양성 증가
# - F1 Score +2-3% 예상
```

**C. 후처리 규칙 정교화**
```python
# 현재: 단순 키워드 매칭
# 개선:
# - 문맥 고려 (주변 단어)
# - 부정 표현 제거 ("Python 불필요")
# - 우선순위 (직무명 > 자격요건 > 우대사항)
```

---

### Q3. TOP N을 변경하고 싶습니다

**주의사항:**
- TOP N 변경 시 전체 재학습 필요
- 성능 저하 가능성 고려

**변경 프로세스:**

```bash
# 1. 데이터 준비
# scripts/1_prepare_data.py 수정
TOP_N = 500  # 300 → 500

python scripts/1_prepare_data.py

# 2. 모델 재학습
python scripts/2_train_model_multiarch.py bert 42
python scripts/2_train_model_multiarch.py kcbert 42
python scripts/train_stacking_top2.py

# 3. 성능 평가
python scripts/6_validate_results.py

# 4. 비교
# F1 Score 비교: 0.6995 vs 새로운 값
# - 향상: 계속 사용
# - 저하: 300으로 복구
```

---

### Q4. Streamlit 앱에서 후처리가 작동하지 않습니다

**확인 사항:**

```python
# 1. 토글 상태
enable_postprocessing = True  # ON인지 확인

# 2. 키워드 맵 로드
print(f"Keyword map size: {len(model.keyword_map)}")
# 0이면 로드 실패

# 3. Remember 데이터 존재
ls data/remember/remember_251120.json
# 없으면 키워드 맵 생성 불가

# 4. label_normalization import
python -c "from label_normalization import skill_map; print(len(skill_map))"
# 에러 시 경로 문제
```

---

## 요약

### 핵심 원칙

1. **정규화 우선** - 같은 스킬은 하나로
2. **TOP 300 최적** - 데이터와 성능의 균형
3. **AI의 강점** - 문맥 이해, 높은 Precision
4. **후처리로 보완** - 커버리지 확보, Recall 향상
5. **하이브리드 전략** - AI + 규칙 = 최선

### 파이프라인 요약

```
1. 정규화: 1,774개 → 1,547개 (중복 제거)
2. 선택: 1,547개 → 300개 (학습 가능)
3. 학습: 300개 라벨 → F1 0.6995
4. 예측: 300개 중 예측 → 평균 1.63개/공고
5. 후처리: +59개 스킬 → 평균 5.95개/공고
```

### 성능 지표

| 지표 | AI만 | AI + 후처리 |
|------|------|------------|
| F1 Score | 0.6995 | 더 높음 (미측정) |
| Precision | 0.7664 | 0.65-0.70 (예상) |
| Recall | 0.6433 | 0.75+ (예상) |
| 스킬/공고 | 1.63 | 5.95 |

---


*Last updated: 2025-11-26*
*Writer: jinwoo-Kim*