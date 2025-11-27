"""
후처리 스킬 매핑 (v2)
label_normalization.py의 매핑 테이블 재사용


"""

import json
from pathlib import Path
import re
from collections import defaultdict

# ✅ 정규화(label_normalization.py) import
import sys
sys.path.append('./scripts')
from label_normalization import skill_map, normalize_skills

EXCLUDE_KEYWORDS = {
    '구축', '프로젝트', '개발자', '커뮤니케이션', '연구',
    '프레임워크', '테스트', '아키텍처', '서비스 개발', '품질',
    '엔지니어링', '기획', '투자', '검증', '앱'
}

# ===== 기술 스킬 화이트리스트 =====
TECH_KEYWORDS = {
    # 프로그래밍 언어 관련
    'python', 'java', 'javascript', 'typescript', 'cpp', 'c', 'csharp', 
    'go', 'rust', 'kotlin', 'swift', 'php', 'ruby', 'scala',
    
    # 프레임워크/라이브러리
    'react', 'vue', 'angular', 'nextjs', 'django', 'flask', 'fastapi', 
    'spring', 'nestjs', 'express', 'laravel', 'rails',
    
    # 데이터베이스
    'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'mssql', 
    'dynamodb', 'cassandra', 'elasticsearch',
    
    # 클라우드/DevOps
    'aws', 'gcp', 'azure', 'docker', 'kubernetes', 'terraform', 
    'jenkins', 'ci', 'cd', 'github', 'gitlab', 'bitbucket',
    
    # AI/ML/데이터
    'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 
    'numpy', 'spark', 'hadoop', 'kafka', 'airflow', 'mlflow',
    'langchain', 'langgraph', 'langsmith', 'langgraph_studio',
    
    # 프론트엔드
    'html', 'css', 'sass', 'webpack', 'babel', 'redux', 'graphql',
    
    # 백엔드/API
    'backend', 'frontend', 'restful', 'REST API', 'grpc', 'graphql',
    
    # 도구
        # DevOps/backend
        'confluence', 'grafana', 'prometheus',

    'git', 'github', 'gitlab', 'jenkins', 'linux', 'nginx', 'apache',
    'jira', 'confluence'
}

print("=" * 70)
print("Step 4: Post-processing with Keyword Matching (Stacking)")
print("=" * 70)

# ===== 1단계: 스킬 데이터 로드 =====
print("\n[1] Loading skill data...")

# 전체 스킬 (1,774개 정규화 전)
with open('./data/remember/remember_251120.json', 'r', encoding='utf-8') as f:
    raw_jobs = json.load(f)

# 모든 스킬 추출
from label_normalization import normalize_skills, skill_map
all_skills_raw = set()
for job in raw_jobs:
    if '이 포지션에 필요한 전문분야/기술' in job:
        skills = [s['text'] for s in job['이 포지션에 필요한 전문분야/기술']]
        normalized = normalize_skills(skills, skill_map)
        all_skills_raw.update(normalized)

all_skills_normalized = sorted(list(all_skills_raw))  # 전체!

# 학습된 스킬 (300개) - Use stacking model skills
with open('./models/meta_model_stacking_top2/skills.json', 'r', encoding='utf-8') as f:
    trained_skills = set(json.load(f))

# 미학습 스킬
untrained_skills = [s for s in all_skills_normalized if s not in trained_skills]

print(f"    Total normalized skills: {len(all_skills_normalized)}")
print(f"    Trained skills: {len(trained_skills)}")
print(f"    Untrained skills: {len(untrained_skills)}")

# ===== 2단계: 역매핑 테이블 생성 =====
print("\n[2] Creating reverse mapping table...")

"""
skill_map: "파이썬" → "python"
reverse_map: "python" → ["파이썬", "python", "py", ...]

미학습 스킬을 텍스트에서 찾기 위한 키워드 목록
"""

# 정규화된 스킬 → 키워드들
reverse_map = defaultdict(set)

for key, value in skill_map.items():
    reverse_map[value].add(key)  # value(정규화)에 key(원본) 추가
    reverse_map[value].add(value)  # 정규화된 형태도 키워드로

# 미학습 스킬에 대해서만 reverse_map 생성
keyword_map = {}
for skill in all_skills_normalized:
    # 기술 키워드에 포함된 것만
    if skill.lower() in TECH_KEYWORDS or skill in TECH_KEYWORDS:
        if skill in reverse_map:
            keyword_map[skill] = list(reverse_map[skill])
        else:
            # reverse_map에 없으면 스킬 자체를 키워드로
            keyword_map[skill] = [skill, skill.replace('-', ' '), skill.replace(' ', '-')]

keyword_map = {k: v for k, v in keyword_map.items() if k not in EXCLUDE_KEYWORDS}

print(f"    Mapped {len(keyword_map)} skills")
print(f"\n    Examples:")
for skill in list(keyword_map.keys())[:5]:
    print(f"      {skill}: {list(keyword_map[skill])[:3]}")

# ===== 3단계: 후처리 함수 =====
print("\n[3] Defining post-processing function...")

def post_process_add_skills(text, predicted_skills, keyword_map):
    """
    텍스트에서 키워드 찾아서 미학습 스킬 추가
    
    Args:
        text: 공고 텍스트
        predicted_skills: AI가 예측한 스킬 (정규화된 형태)
        keyword_map: 미학습 스킬 → 키워드 매핑
    
    Returns:
        추가된 스킬 리스트
    """
    text_lower = text.lower()
    added_skills = []
    
    for skill, keywords in keyword_map.items():
        # 이미 예측된 스킬은 스킵
        if skill in predicted_skills:
            continue
        
        # 키워드 매칭
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # 정규식 패턴 (단어 경계)
            # 단, 특수문자 있으면 이스케이프
            pattern = r'\b' + re.escape(keyword_lower) + r'\b'
            
            if re.search(pattern, text_lower):
                added_skills.append(skill)
                break  # 하나라도 찾으면 다음 스킬로
    
    return added_skills

print("    Post-processing function ready!")

# ===== 4단계: 원티드 파일 후처리 =====
print("\n[4] Post-processing Wanted files...")

INPUT_DIR = "./data/wanted/wanted_predicted_stacking"
OUTPUT_DIR = "./data/wanted/wanted_final"

import os
os.makedirs(OUTPUT_DIR, exist_ok=True)

from tqdm import tqdm

files = list(Path(INPUT_DIR).glob("*.json"))

total_jobs = 0
total_added = 0
added_skill_counter = defaultdict(int)

for file_path in tqdm(files, desc="파일 처리"):
    with open(file_path, 'r', encoding='utf-8') as f:
        jobs = json.load(f)
    
    for job in jobs:
        total_jobs += 1

        # AI 예측 스킬 (정규화된 형태) - from stacking model
        ai_skills = job.get('predicted_skills_stacking', [])
        
        # 텍스트 추출
        job_desc = job.get('job_description', {})
        text_parts = []
        
        # 포지션명도 포함!
        if job.get('position'):
            text_parts.append(job['position'])
        
        if job_desc.get('position_detail'):
            text_parts.append(job_desc['position_detail'])
        if job_desc.get('main_tasks'):
            text_parts.append(job_desc['main_tasks'])
        if job_desc.get('requirements'):
            text_parts.append(job_desc['requirements'])
        if job_desc.get('preferred'):
            text_parts.append(job_desc['preferred'])
        
        full_text = ' '.join(text_parts)
        
        # 후처리로 미학습 스킬 추가
        added_skills = post_process_add_skills(full_text, ai_skills, keyword_map)
        
        if added_skills:
            total_added += len(added_skills)
            for skill in added_skills:
                added_skill_counter[skill] += 1
        
        # 최종 스킬 = AI + 후처리
        # ✅ 중복 제거 (너의 방식대로)
        final_skills = sorted(set(ai_skills + added_skills))
        
        job['predicted_skills_final'] = final_skills
        job['predicted_skills_ai'] = ai_skills  # 비교용
        job['predicted_skills_postprocess'] = added_skills  # 비교용
    
    # 저장
    output_path = Path(OUTPUT_DIR) / file_path.name
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)

# ===== 5단계: 통계 =====
print("\n" + "=" * 70)
print("POST-PROCESSING RESULTS")
print("=" * 70)
print(f"Total jobs processed: {total_jobs:,}")
print(f"Total skills added: {total_added:,}")
print(f"Avg skills added per job: {total_added/total_jobs:.2f}")
print(f"Unique skills added: {len(added_skill_counter)}")

print(f"\nTop 30 Most Added Skills:")
sorted_added = sorted(added_skill_counter.items(), key=lambda x: x[1], reverse=True)
for rank, (skill, count) in enumerate(sorted_added[:30], 1):
    print(f"   {rank:2d}. {skill}: {count} times")

# ===== 6단계: Before/After 비교 =====
print("\n" + "=" * 70)
print("BEFORE/AFTER COMPARISON")
print("=" * 70)

# AI만 vs AI+후처리 비교
ai_only_count = 0
final_count = 0

for file_path in Path(OUTPUT_DIR).glob("*.json"):
    with open(file_path, 'r', encoding='utf-8') as f:
        jobs = json.load(f)
        for job in jobs:
            ai_only_count += len(job.get('predicted_skills_ai', []))
            final_count += len(job.get('predicted_skills_final', []))

print(f"AI only:           Avg {ai_only_count/total_jobs:.2f} skills/job")
print(f"AI + Post-process: Avg {final_count/total_jobs:.2f} skills/job")
print(f"Increase:          +{(final_count-ai_only_count)/total_jobs:.2f} skills/job")

print("\n" + "=" * 70)
print("POST-PROCESSING COMPLETE!")
print(f"\nNext step: Run 5_integrate_all.py to integrate all data")
print("=" * 70)
print(f"\nSaved to: {OUTPUT_DIR}/")