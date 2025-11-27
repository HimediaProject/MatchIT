"""
스크립트 4: 전체 데이터 통합하기

목적: 리멤버 + 원티드(예측 완료) → 하나의 DB 준비 데이터
출력: 통합된 JSON 파일 (DB에 바로 넣을 수 있는 형태)
"""
import hashlib
import json
import re
from label_normalization import skill_map
from pathlib import Path
from collections import Counter


print("=" * 70)
print("Step 5: Integrate Remember + Wanted Data")
print("=" * 70)

# ===== 설정 =====
REMEMBER_FILE = "./data/remember/remember_251120.json"
WANTED_DIR = "./data/wanted/wanted_final"
OUTPUT_FILE = "./results/final_integrated_jobs.json"

print(f"\nRemember: {REMEMBER_FILE}")
print(f"Wanted: {WANTED_DIR}")
print(f"Output: {OUTPUT_FILE}")

# ===== 1단계: 리멤버 데이터 로드 =====
print("\n[1] Loading Remember data...")

with open(REMEMBER_FILE, 'r', encoding='utf-8') as f:
    remember_data = json.load(f)

print(f"    Remember jobs: {len(remember_data)}")

# ===== 2단계: 원티드 데이터 로드 =====
print("\n[2] Loading Wanted data...")

wanted_files = list(Path(WANTED_DIR).glob("*.json"))
wanted_data = []

for file_path in wanted_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        jobs = json.load(f)
        wanted_data.extend(jobs)

print(f"    Wanted jobs: {len(wanted_data)}")

# ===== 3단계: 통일된 형식으로 변환 =====
print("\n[3] Normalizing data format...")

"""
목표: 두 사이트의 다른 필드명을 통일된 스키마로 변환

통일된 스키마:
{
    'id': 고유 ID,
    'source': '리멤버' or '원티드',
    'title': 포지션명,
    'company': 회사명,
    'location': 위치,
    'experience': 경력,
    'skills': [스킬 리스트],
    'description': 전체 설명,
    'url': 원본 링크,
    'salary': 연봉 (있으면),
    ...
}
"""
def normalize_skill(skill):
    skill_lower = skill.lower().strip()
    if skill_lower in skill_map:
        return skill_map[skill_lower]
    return skill_lower

def normalize_location(location):
    """위치 표기 통일"""
    if not location:
        return ""
    
    # "서울특별시" → "서울"
    location = location.replace('특별시', '').replace('광역시', '')
    # "경기도" → "경기"
    location = location.replace('도', '')
    # 공백 정리
    location = ' '.join(location.split())
    
    return location

def normalize_deadline(deadline_str):
    """마감일 ISO 형식"""
    if not deadline_str:
        return None
    
    # "2025년 12월 03일기업의..." → "2025-12-03"
    match = re.search(r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일', deadline_str)
    if match:
        year, month, day = match.groups()
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    
    if "상시" in deadline_str:
        return "상시채용"
    
    return None  # 파싱 실패

def normalize_remember(job):
    """리멤버 데이터를 통일 형식으로"""
    
    # 스킬 추출
    skills = []
    if job.get('이 포지션에 필요한 전문분야/기술'):
        skills = [s['text'] for s in job['이 포지션에 필요한 전문분야/기술']]
    
    # ID 생성 (URL 해시)
    job_id = hashlib.md5(job.get('url', '').encode()).hexdigest()[:12]
    
    return {
        'id': job_id,
        'source': '리멤버',
        'title': job.get('title', ''),
        'company': job.get('url', '').split('/company/')[-1] if 'company' in job.get('url', '') else '',
        'location': job.get('근무지', ''),
        'experience': job.get('경력', ''),
        'skills': skills,
        'description': {
            'main_tasks': job.get('주요업무', ''),
            'requirements': job.get('자격 요건', ''),
            'preferred': job.get('우대사항', ''),
            'benefits': job.get('기타안내', '')
        },
        'url': job.get('url', ''),
        'salary': job.get('연봉', ''),
        'deadline': normalize_deadline(job.get('마감일', '')),
        'raw_data': job  # 원본 보존
    }

def normalize_wanted(job):
    """원티드 데이터를 통일 형식으로"""

    job_desc = job.get('job_description', {})

    # 스킬 (예측된 것)
    skills = job.get('predicted_skills_final', [])
    skill_confidences = job.get('skill_confidences_stacking', {})

    # 스킬이 있는데 confidence 없으면 raw_data에서 가져오기
    if skills and not skill_confidences:
        skill_confidences = job.get('skill_confidences_stacking', {})

    # ID 생성
    job_id = hashlib.md5(job.get('url', '').encode()).hexdigest()[:12]
    
    return {
        'id': job_id,
        'source': '원티드',
        'title': job.get('position', ''),
        'company': job.get('company', ''),
        'location': job.get('location', ''),
        'experience': job.get('experience', ''),
        'skills': skills,
        'skill_confidences': skill_confidences,  # AI 신뢰도
        'description': {
            'main_tasks': job_desc.get('main_tasks', ''),
            'requirements': job_desc.get('requirements', ''),
            'preferred': job_desc.get('preferred', ''),
            'benefits': job_desc.get('benefits', '')
        },
        'url': job.get('url', ''),
        'deadline': normalize_deadline(job_desc.get('deadline', '')),
        'tags': job_desc.get('tags', []),
        'raw_data': job  # 원본 보존
    }

def normalize_experience(exp_str):
    """
    경력 정보 정규화
    
    Returns:
        {
            "career_type": "신입" | "경력" | "경력무관",
            "experience": "5년~10년",
            "experience_years": {"min": 5, "max": 10}
        }
    """
    if not exp_str:
        return {
            "career_type": "경력무관",
            "experience": "경력무관",
            "experience_years": {"min": 0, "max": None}
        }
    
    exp_lower = exp_str.lower()
    
    # 신입
    if "신입" in exp_lower:
        return {
            "career_type": "신입",
            "experience": "신입",
            "experience_years": {"min": 0, "max": 0}
        }
    
    # 경력무관
    if "무관" in exp_lower:
        return {
            "career_type": "경력무관",
            "experience": "경력무관",
            "experience_years": {"min": 0, "max": None}
        }
    
    # 숫자 추출: "10년~20년 차", "5-10년" 등
    numbers = re.findall(r'\d+', exp_str)
    
    if len(numbers) >= 2:
        min_year = int(numbers[0])
        max_year = int(numbers[1])
        return {
            "career_type": "경력",
            "experience": f"{min_year}년~{max_year}년",
            "experience_years": {"min": min_year, "max": max_year}
        }
    elif len(numbers) == 1:
        year = int(numbers[0])
        return {
            "career_type": "경력",
            "experience": f"{year}년 이상",
            "experience_years": {"min": year, "max": None}
        }
    
    # 파싱 실패 시 원본
    return {
        "career_type": "경력",
        "experience": exp_str,
        "experience_years": {"min": None, "max": None}
    }

# 변환 실행
integrated_data = []

for job in remember_data:
    try:
        integrated_data.append(normalize_remember(job))
    except Exception as e:
        print(f"    WARNING: Remember conversion error: {e}")

for job in wanted_data:
    try:
        integrated_data.append(normalize_wanted(job))
    except Exception as e:
        print(f"    WARNING: Wanted conversion error: {e}")

print(f"    Integration complete: {len(integrated_data)} jobs")

# ===== 4단계: 중복 제거 =====
print("\n[4] Removing duplicates...")

"""
같은 회사의 같은 포지션이 여러 사이트에 있을 수 있음
URL 기반으로 중복 제거
"""

seen_ids = set()
unique_data = []

for job in integrated_data:
    if job['id'] not in seen_ids:
        seen_ids.add(job['id'])
        unique_data.append(job)

removed = len(integrated_data) - len(unique_data)
print(f"    Duplicates removed: {removed}")
print(f"    Final jobs: {len(unique_data)}")

# ===== Normalization =====
print("\n[5] Normalizing experience/skills/location...")
for job in unique_data:
    # Experience normalization
    job['experience_normalized'] = normalize_experience(job.get('experience'))

    # Skill normalization
    job['skills'] = [normalize_skill(s) for s in job.get('skills', [])]

    # Location normalization
    job['location'] = normalize_location(job.get('location', ''))
print("    Normalization complete!")

# ===== 5단계: 통계 계산 =====
print("\n[6] Calculating statistics...")

# 스킬 분포
all_skills = []
for job in unique_data:
    all_skills.extend(job['skills'])

skill_counter = Counter(all_skills)

# 사이트별 분포
source_counter = Counter(job['source'] for job in unique_data)

# 위치별 분포
location_counter = Counter(job['location'] for job in unique_data if job['location'])

# 경력별 분포
experience_counter = Counter(
    job['experience_normalized']['experience']
    for job in unique_data
    if job['experience_normalized'])

# ===== 6단계: 최종 저장 =====
print("\n[7] Saving final data...")

final_output = {
    'metadata': {
        'total_jobs': len(unique_data),
        'sources': dict(source_counter),
        'total_skills': len(set(all_skills)),
        'generation_date': '2025-11-26'
    },
    'statistics': {
        'top_skills': dict(skill_counter.most_common(50)),
        'locations': dict(location_counter.most_common(20)),
        'experiences': dict(experience_counter)
    },
    'jobs': unique_data
}

# 1. 전체 버전 (raw 포함)
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(final_output, f, ensure_ascii=False, indent=2)
print(f"    Full version saved: {OUTPUT_FILE}")

# 2. 경량 버전 (raw 제외)
jobs_without_raw = []
for job in unique_data:
    job_copy = job.copy()
    job_copy.pop('raw_data', None)  # raw_data 제거
    jobs_without_raw.append(job_copy)

final_output_light = {
    'metadata': final_output['metadata'],
    'statistics': final_output['statistics'],
    'jobs': jobs_without_raw
}

OUTPUT_FILE_LIGHT = "./results/final_integrated_jobs_light.json"
with open(OUTPUT_FILE_LIGHT, 'w', encoding='utf-8') as f:
    json.dump(final_output_light, f, ensure_ascii=False, indent=2)
print(f"    Light version saved: {OUTPUT_FILE_LIGHT}")

# ===== 7단계: 최종 보고서 =====
print("\n" + "=" * 70)
print("INTEGRATION RESULTS")
print("=" * 70)

print(f"\nTotal jobs: {len(unique_data):,}")
print(f"\nBy source:")
for source, count in source_counter.items():
    print(f"   - {source}: {count:,} ({count/len(unique_data)*100:.1f}%)")

print(f"\nSkill statistics:")
print(f"   - Total unique skills: {len(set(all_skills))}")
print(f"   - Avg skills per job: {len(all_skills)/len(unique_data):.2f}")

print(f"\nTop 10 Skills:")
for rank, (skill, count) in enumerate(skill_counter.most_common(10), 1):
    print(f"   {rank:2d}. {skill}: {count} times")

print(f"\nTop 5 Locations:")
for location, count in location_counter.most_common(5):
    print(f"   - {location}: {count}")

print("\n" + "=" * 70)

# ===== 8단계: DB 준비 샘플 =====
print("\n[8] Creating DB sample...")

"""
PostgreSQL에 넣기 좋은 형태로 샘플 생성
"""

db_sample = []
for job in unique_data[:5]:
    db_sample.append({
        'id': job['id'],
        'source': job['source'],
        'title': job['title'],
        'company': job['company'],
        'location': job['location'],
        'experience': job['experience'],
        'skills': job['skills'],  # JSON 배열로 저장
        'description_main_tasks': job['description']['main_tasks'],
        'description_requirements': job['description']['requirements'],
        'description_preferred': job['description']['preferred'],
        'url': job['url']
    })

with open('./db_sample.json', 'w', encoding='utf-8') as f:
    json.dump(db_sample, f, ensure_ascii=False, indent=2)

print(f"    DB sample saved: ./db_sample.json")

# ===== 완료! =====
print("\n" + "=" * 70)
print("INTEGRATION COMPLETE!")
print("=" * 70)
print(f"\nFinal files:")
print(f"   1. {OUTPUT_FILE}")
print(f"      - Full integrated data (with raw)")
print(f"   2. {OUTPUT_FILE_LIGHT}")
print(f"      - Light version (without raw)")
print(f"   3. ./db_sample.json")
print(f"      - DB schema reference")
print(f"\nNext steps:")
print(f"   1. Validate results")
print(f"   2. PostgreSQL DB design (optional)")
print(f"   3. FastAPI backend (optional)")
print(f"   4. React frontend (optional)")
print("=" * 70)