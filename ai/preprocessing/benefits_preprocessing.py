import json
import re
from collections import defaultdict

# ============================================
# 1단계: 노이즈 필터링
# ============================================

# 복지가 아닌 내용을 식별하는 키워드
NOISE_KEYWORDS = [
    # 채용/전형 관련
    "결격사유", "합격이 취소", "합격 취소", "전형", "지원서", "채용",
    "부정한", "거짓", "제출서류", "불합격", "평판", "경력조회", "신용조회",
    "SMS로 안내", "휴대전화 번호", "보험업법", "금융관계 법률",
    # 지원자격/안내
    "병역", "여행에 적격", "해외 여행",
    # 기타 노이즈
    "전문계약직", "계약 연장",
    # 단순 안내
    "배우고자 하는 의지", "열정만 있으시면",
]

# 짧지만 유용한 고용형태 키워드
USEFUL_SHORT_KEYWORDS = [
    '정규직', '계약직', '인턴', '파견직', '프리랜서',
    '정규', '비정규', '무기계약', '전일제', '시간제',
]

# 짧지만 유용한 복지 키워드
USEFUL_BENEFIT_KEYWORDS = [
    '채용축하금', '입사축하금', '추천채용',
]


# 2단계에서 필터링할 노이즈 패턴 (개별 항목 수준)
ITEM_NOISE_PATTERNS = [
    r'^근무지\s*[:：]',
    r'^Location\s*[:：]',
    r'^Full\s*time',
    # 정규직, 계약직은 제거하지 않음
    r'기업 홈페이지 참고',
    r'^Huge Opportunity$',
    r'^Competitive Salary$',
    r'^A Focused Work Environment$',
    r'^Great Team',
]

# 근무지/위치만 있는 패턴
LOCATION_ONLY_PATTERNS = [
    r"^기타안내[•\s]*근무지\s*[:：]",
    r"^기타안내[•\s]*Location",
    r"^기타안내※?\s*고용형태\s*[:：]?\s*$",  # "고용형태" 단독
]

def is_noise(text: str) -> bool:
    """노이즈 여부 판단"""
    if not text or not text.strip():
        return True
    
    text = text.strip()
    clean_text = re.sub(r'^기타안내\s*', '', text).strip()
    
    # ⭐ 1단계: 유용한 고용형태 키워드 체크
    all_useful_keywords = USEFUL_SHORT_KEYWORDS + USEFUL_BENEFIT_KEYWORDS
    for keyword in all_useful_keywords:
        if keyword in clean_text:
            return False  # 무조건 유지!
    
    # ⭐ 2단계: 특정 복지 패턴 체크 (길이 체크 전에!)
        if "채용축하금" in clean_text or "입사축하금" in clean_text:
            return False

    # 3단계: 너무 짧은 텍스트
    if len(clean_text) < 15:
        return True
    
    # 4단계: URL만 있는 경우
    if re.match(r'\[.*\]\.?https?://', clean_text):
        return True
    
    # 5단계: 노이즈 키워드 포함
    for keyword in NOISE_KEYWORDS:
        if keyword in text:
            # 고용형태 키워드와 함께 있으면 유지
            has_useful_keyword = any(uk in clean_text for uk in USEFUL_SHORT_KEYWORDS)
            if has_useful_keyword:
                continue
            
            return True
    
    # 6단계: 근무지/위치만 있는 패턴
    for pattern in LOCATION_ONLY_PATTERNS:
        if re.match(pattern, text):
            return True
    
    return False

def filter_noise(data: dict) -> dict:
    """노이즈 필터링"""
    return {k: v for k, v in data.items() if not is_noise(v)}


# ============================================
# 2단계: 개별 항목 파싱
# ============================================

# 불릿/번호 패턴들
BULLET_PATTERNS = [
    r'\n(?=[-•·ㆍ]\s)',           # - • · ㆍ 불릿
    r'\n(?=\d+[.)]\s)',           # 1) 1. 번호
    r'\n(?=[①-⑳])',               # 원문자 번호
    r'\n(?=→)',                   # 화살표 (하위 설명)
    r'(?<=[^\n])(?=\n[-•·ㆍ])',   # 줄바꿈 없이 불릿 시작
]

def clean_prefix(text: str) -> str:
    """기타안내 prefix 및 불필요한 공백 제거"""
    text = re.sub(r'^기타안내\s*', '', text.strip())
    return text.strip()

def split_into_items(text: str) -> list:
    """텍스트를 개별 복지 항목으로 분리"""
    text = clean_prefix(text)
    
    # 카테고리 헤더 제거 (예: [복지], 【근무환경】)
    text = re.sub(r'[\[【\(].*?[\]】\)]', '\n', text)
    
    # 이모지 카테고리 헤더 제거
    text = re.sub(r'[🏢🎯🌈💰🎁✨]\s*[^\n]*\n', '\n', text)
    text = re.sub(r'[🌟🧘💉🔖🖥️🤝🌿👍🤩💸📖⏰🏄‍♀️🏠🍚🍰😌🤵👰🎶👍🤩📖🏠😌]\s*[^\n]*\n', '\n', text)
    # 불릿 기준으로 분리
    # 먼저 통일된 구분자로 변경
    text = re.sub(r'\n\s*[-•·ㆍ]\s*', '\n@@SPLIT@@', text)
    text = re.sub(r'\n\s*\d+[.)]\s*', '\n@@SPLIT@@', text)
    text = re.sub(r'\n\s*[①-⑳]\s*', '\n@@SPLIT@@', text)
    
    # 첫 항목도 처리
    text = re.sub(r'^[-•·ㆍ]\s*', '@@SPLIT@@', text)
    text = re.sub(r'^\d+[.)]\s*', '@@SPLIT@@', text)
    
    items = text.split('@@SPLIT@@')
    
    # 정제
    result = []
    for item in items:
        item = item.strip()
        # 하위 설명(→)은 이전 항목에 병합하거나 독립 항목으로
        item = re.sub(r'\s*→\s*', ': ', item)
        # 여러 줄 공백 정리
        item = re.sub(r'\n\s*\n', ' ', item)
        item = re.sub(r'\n', ' ', item)
        item = item.strip()
        
        if item and len(item) >= 5:  # 너무 짧은 항목 제외
            result.append(item)
    
    return result

def parse_all_items(data: dict) -> list:
    """전체 데이터에서 개별 항목 추출"""
    all_items = []
    for idx, text in data.items():
        items = split_into_items(text)
        for item in items:
            # 개별 항목 노이즈 필터링
            is_noise_item = False
            for pattern in ITEM_NOISE_PATTERNS:
                if re.search(pattern, item, re.IGNORECASE):
                    is_noise_item = True
                    break
            
            if not is_noise_item:
                all_items.append({
                    'original_idx': idx,
                    'text': item
                })
    return all_items


# ============================================
# 3단계: 카테고리 분류
# ============================================

CATEGORY_KEYWORDS = {
    '식사지원': [
        '식대', '중식', '석식', '조식', '점심', '저녁', '식당', '구내식당',
        '식사', '간식', '스낵', '커피', '음료', '카페', '과일',
        # 영어
        'meal', 'lunch', 'dinner', 'breakfast', 'snack', 'food', 'coffee'
    ],
    '휴가제도': [
        '연차', '반차', '반반차', '리프레시', '휴가', '휴무', 
        '여름휴가', '경조휴가', '출산휴가', '육아휴직', '돌봄휴가',
        'Family Day', '조기퇴근', '정시퇴근',
        # 영어
        'vacation', 'leave', 'holiday', 'day off', 'pto', 'refresh'
    ],
    '건강/의료': [
        '건강검진', '종합검진', '단체보험', '상해보험', '의료비',
        '예방접종', '스케일링', '멘탈케어', '심리상담', 'EAP',
        '체력단련', '운동', '헬스', '피트니스', '웰니스',
        # 영어
        'health check', 'medical', 'insurance', 'wellness', 'gym', 'fitness'
    ],
    '근무환경': [
        '유연근무', '재택', '시차', '탄력', '자율출퇴근', '선택근로',
        '코어타임', '셔틀', '주차', '통근', '교통비',
        '사무실', '오피스', '장비', '모니터', '노트북', '맥북',
        '자율 출퇴근', '유연 근무', '자율출근', '시차출퇴근', '시차출근',
        '택시비', '야근', '선택적', '자율과', '재택근무',
        # 영어
        'remote', 'wfh', 'work from home', 'flexible', 'home office',
        'hybrid', 'equipment', 'macbook', 'laptop'
    ],
    '고용 형태': [
        '정규직', '계약직', '인턴', '파견직', '프리랜서',
        '전일제', '시간제', 'Full time', 'Part time',
        '정규', '비정규', '무기계약',
    ],    
    '가족지원': [
        '출산', '육아', '자녀', '학자금', '어린이집', '보육',
        '배우자', '가족', '부모님', '난임', '임신',
        # 영어
        'parental', 'child', 'family', 'maternity', 'paternity'
    ],
    '자기개발': [
        '교육비', '도서', '어학', '외국어', '자격증', '세미나',
        '컨퍼런스', '강좌', '스터디', '성장',
        # 영어
        'education', 'training', 'book', 'course', 'learning', 'english lesson'
    ],
    '경조사': [
        '경조금', '경조사', '결혼', '축의금', '조의금', '화환'
    ],
    '휴양시설': [
        '리조트', '콘도', '휴양', '호텔', '숙박', '휴양시설',
        # 영어
        'resort', 'travel', 'accommodation'
    ],
    '금전보상': [
        '성과급', '인센티브', '보너스', '스톡옵션', '복지포인트',
        '포인트', '상품권', '지원금', '수당', '명절', '생일',
        '장기근속', '근속', '포상', '우수사원',
        # 영어
        'bonus', 'incentive', 'stock option', 'equity', 'salary', 'compensation'
    ],
    '4대보험/퇴직': [
        '4대보험', '퇴직연금', '퇴직금', '국민연금'
    ],
    '주거지원': [
        '주택', '기숙사', '주거', '대출', '이자지원',
        # 영어
        'housing', 'dormitory'
    ],
    '조직문화': [
        '수평', '호칭', '님', '존댓말', '동호회', '타운홀',
        '워크샵', '회식', '팀빌딩',
        # 영어
        'culture', 'team'
    ],
    '임직원할인': [
        '할인', '사원판매', '직원할인', '임직원할인', '특별가', '임직원가',
        '사원 판매', '직원 할인', '임직원 할인',
        # 영어
        'discount', 'employee price'
    ]
}

def classify_item(text: str) -> list:
    text_lower = text.lower()
    text_normalized = text_lower.replace(' ', '')  # ⭐ 공백 제거해서 비교
    categories = []
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            keyword_normalized = keyword.lower().replace(' ', '')
            if keyword_normalized in text_normalized:
                categories.append(category)
                break
    
    if not categories:
        categories.append('기타')
    
    return categories

def classify_all_items(items: list) -> list:
    """전체 항목 분류"""
    for item in items:
        item['categories'] = classify_item(item['text'])
    return items


# ============================================
# 메인 파이프라인
# ============================================

def run_pipeline(input_path: str, output_path: str = None):
    """전처리 파이프라인 실행"""
    
    # 데이터 로드
    with open(input_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    print(f"원본 데이터: {len(raw_data)}개")
    
    # 1단계: 노이즈 필터링
    filtered_data = filter_noise(raw_data)
    print(f"1단계 (노이즈 필터링): {len(filtered_data)}개 남음")
    
    # 2단계: 개별 항목 파싱
    parsed_items = parse_all_items(filtered_data)
    print(f"2단계 (항목 분리): {len(parsed_items)}개 항목 추출")
    
    # 3단계: 카테고리 분류
    classified_items = classify_all_items(parsed_items)
    
    # 카테고리별 통계
    category_counts = defaultdict(int)
    for item in classified_items:
        for cat in item['categories']:
            category_counts[cat] += 1
    
    print(f"\n3단계 (카테고리 분류) 결과:")
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}개")
    
    # 결과 저장
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(classified_items, f, ensure_ascii=False, indent=2)
        print(f"\n결과 저장: {output_path}")
    
    return classified_items


# ============================================
# 실행
# ============================================

# if __name__ == "__main__":
#     results = run_pipeline(
#         input_path = "./results/benefits.json",
#         output_path ="./benefits_processed.json"
#     )
    
#     # 샘플 출력
#     print("\n" + "="*50)
#     print("샘플 결과 (처음 10개):")
#     print("="*50)
#     for item in results[:10]:
#         print(f"\n[{', '.join(item['categories'])}]")
#         print(f"  {item['text'][:80]}...")

# 파일 로드
with open("./results/final_integrated_jobs_light.json", 'r', encoding='utf-8') as f:
    data = json.load(f)

# benefits만 추출해서 딕셔너리로 만들기 (기존 benefits.json 형태로)
benefits_dict = {}
for idx, job in enumerate(data['jobs']):
    benefits_text = job['description']['benefits']
    if benefits_text:  # 빈 문자열 아닐 때만
        benefits_dict[str(idx)] = benefits_text

print(f"추출된 benefits: {len(benefits_dict)}개")

# 기존 run_pipeline 함수 사용 (딕셔너리를 직접 전달)
# run_pipeline의 input_path 대신 딕셔너리를 받도록 수정 필요

# 또는 임시 파일로 저장 후 처리
temp_benefits_path = './results/temp_benefits.json'
with open(temp_benefits_path, 'w', encoding='utf-8') as f:
    json.dump(benefits_dict, f, ensure_ascii=False, indent=2)

# 기존 run_pipeline 실행
processed_items = run_pipeline(
    input_path=temp_benefits_path,
    output_path='./results/benefits_preprocessed.json'
)

# 결과를 원본 파일에 다시 매핑
for item in processed_items:
    job_idx = int(item['original_idx'])
    if job_idx < len(data['jobs']):
        # 기존 benefits를 처리된 항목들로 교체
        if 'processed_benefits' not in data['jobs'][job_idx]['description']:
            data['jobs'][job_idx]['description']['processed_benefits'] = [] # 새로운 column 추가
        data['jobs'][job_idx]['description']['processed_benefits'].append(item)

# 최종 저장
with open('./results/final_integrated_jobs_processed.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("처리 완료!")