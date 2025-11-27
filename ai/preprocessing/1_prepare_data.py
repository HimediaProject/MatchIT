"""
스크립트 1: 리멤버 데이터 준비하기

목적: JSON 파일에서 학습에 필요한 데이터만 추출
입력: remember_251120.json -> rawdata
출력: 학습 가능한 형태의 데이터
"""

import json
import pandas as pd
from collections import Counter
from label_normalization import normalize_skills, skill_map

# ===== 설정 =====
INPUT_FILE = "./data/remember/remember_251120.json"  # 너가 업로드한 파일
OUTPUT_FILE = "./data/remember/prepared_data.json"   # 준비된 데이터 저장

print("=" * 60)
print("🎯 Step 1: 리멤버 데이터 준비 시작!")
print("=" * 60)

# ===== 1단계: 데이터 로드 =====
print("\n1️⃣  JSON 파일 읽는 중...")
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

print(f"   ✅ 총 {len(raw_data)}개 공고 로드 완료!")

# ===== 2단계: 스킬 태그 있는 것만 필터링 =====
print("\n2️⃣  스킬 태그 있는 공고만 선별 중...")

tech_keywords = set(skill_map.values())
filtered_data = []
skill_field = "이 포지션에 필요한 전문분야/기술"

for job in raw_data:
    # 스킬 태그가 있고, 비어있지 않은 경우만
    if skill_field in job and job[skill_field]:
        filtered_data.append(job)

print(f"   ✅ 스킬 태그 있는 공고: {len(filtered_data)}개")

# ===== 3단계: 학습 데이터 형태로 변환 + 노이즈 제거 =====
print("\n3️⃣  학습 가능한 형태로 변환 + 노이즈 제거 중...")

"""
학습에 필요한 것:
1. text (입력): 공고 내용 (주요업무, 자격요건 등)
2. labels (정답): 스킬 리스트
"""
prepared_data = []
all_skills = set()

for job in filtered_data:
    text_parts = []
    
    if job.get('주요업무'):
        text_parts.append(job['주요업무'])
    if job.get('자격 요건'):
        text_parts.append(job['자격 요건'])
    if job.get('우대사항'):
        text_parts.append(job['우대사항'])
    
    full_text = ' '.join(text_parts)
    
    raw_skills = [skill['text'] for skill in job[skill_field]]
    skills = normalize_skills(raw_skills, skill_map)
    
    if not full_text.strip() or not skills:
        continue
    
    # ✅ 노이즈 체크 (tech skill 있는지)
    job_skills = set(skills)
    if not (job_skills & tech_keywords):
        continue  # tech skill 없으면 제외!
    
    prepared_data.append({
        'text': full_text,
        'skills': skills,
        'title': job.get('title', 'N/A')
    })
    
    all_skills.update(skills)

print(f"   ✅ 준비된 데이터: {len(prepared_data)}개 (노이즈 제거 완료)")
print(f"   ✅ 총 스킬 종류: {len(all_skills)}개")

# ===== 4단계: 스킬 분포 확인 =====
print("\n4️⃣  스킬 분포 확인 중...")

# 모든 스킬 카운트
skill_counter = Counter()
for item in prepared_data:
    skill_counter.update(item['skills'])

# 상위 20개 스킬
print("\n   📊 가장 많이 등장한 스킬 Top 100:")
for skill, count in skill_counter.most_common(100):
    print(f"      {skill}: {count}회")

# ===== 4.5단계: 라벨 제한 전처리 =====
TOP_N = 300

skill_counter_clean = Counter()
for item in prepared_data:
    skill_counter_clean.update(item['skills'])

top_skills = set([s for s, _ in skill_counter_clean.most_common(TOP_N)])
print(f"\n   ⚙️ TOP {TOP_N} 스킬 선택")
print(f"   ✅ 최종 라벨 수: {len(top_skills)}개")

# 희귀 스킬 제거
filtered_prepared_data = []
for item in prepared_data:  # ← tech_filtered 아님!
    filtered_skills = [s for s in item['skills'] if s in top_skills]
    if filtered_skills:
        filtered_prepared_data.append({
            'text': item['text'],
            'skills': filtered_skills,
            'title': item['title']
        })

print(f"   ✅ 라벨 제한 후 데이터: {len(filtered_prepared_data)}개")

# ===== 5단계: 저장 =====
print("\n5️⃣  데이터 저장 중...")

# 실제 등장 스킬만 추출
actual_skills = set()
for item in filtered_prepared_data:
    actual_skills.update(item['skills'])

print(f"   ✅ 실제 사용 스킬: {len(actual_skills)}개")

# 준비된 데이터 저장
output_data = {
    'data': filtered_prepared_data,
    'all_skills': sorted(list(actual_skills)),
    'skill_counts': {s: skill_counter_clean[s] for s in actual_skills},  # ✅
    'stats': {
        'total_jobs': len(filtered_prepared_data),
        'total_skills': len(actual_skills),  # ✅
        'avg_skills_per_job': sum(len(item['skills']) for item in filtered_prepared_data) / len(filtered_prepared_data)
    }
}

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"   ✅ 저장 완료: {OUTPUT_FILE}")

# ===== 6단계: 최종 통계 =====
print("\n" + "=" * 60)
print("📊 최종 통계")
print("=" * 60)
print(f"총 공고 수: {output_data['stats']['total_jobs']:,}개")
print(f"총 스킬 종류: {output_data['stats']['total_skills']:,}개")
print(f"공고당 평균 스킬: {output_data['stats']['avg_skills_per_job']:.1f}개")
print("=" * 60)

# ===== 7단계: 샘플 확인 =====
print("\n🔍 샘플 데이터 확인:")
print("-" * 60)
for i, sample in enumerate(prepared_data[:3], 1):
    print(f"\n[샘플 {i}]")
    print(f"제목: {sample['title']}")
    print(f"텍스트 길이: {len(sample['text'])}자")
    print(f"스킬: {sample['skills'][:5]}")  # 처음 5개만
    print(f"텍스트 미리보기: {sample['text'][:100]}...")

print("\n✅ 데이터 준비 완료!")
print("\n다음 단계: 2_train_model.py 실행")