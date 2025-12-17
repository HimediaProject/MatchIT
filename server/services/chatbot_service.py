"""
RAG Chatbot Service (Hybrid Streaming Version)

🔥 Hybrid 방식:
- 채용공고/부트캠프 데이터: 코드로 확실하게 포맷팅
- AI: 인사말 + 코멘트 + 마무리만 담당
- 스트리밍으로 자연스러운 UX
"""
import sys
import io
import os
import re
import torch
import random
import logging
import time
from typing import Dict, List, Optional, Generator
from datetime import datetime
from threading import Thread
from transformers import (
    AutoTokenizer, AutoModelForCausalLM,
    BitsAndBytesConfig, TextIteratorStreamer)
from sentence_transformers import SentenceTransformer
from pgvector.sqlalchemy import Vector
from peft import PeftModel
from sqlalchemy.orm import Session
from sqlalchemy import or_

logging.basicConfig(
    format = '%(asctime)s %(levelname)s:%(message)s',
    level = logging.DEBUG,
    datefmt = '%m/%d/%Y %I:%M:%S %p',
    filename = 'performance.log',
)

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print(f'\n    🛠️ Cuda: {torch.cuda.is_available()} 🛠️')

# ============================================================================
# SBERT 모델 (CPU) - 사용자 query vectorize
# ============================================================================
print(f"\n    📦 Loading SBERT model (CPU)...")
SBERT_MODEL = SentenceTransformer(
    'jhgan/ko-sbert-nli',
    device='cpu'  # VRAM 절약을 위해 CPU 사용
)
print("✅ SBERT model loaded on CPU!")
# ============================================================================
# Conversation History Manager
# ============================================================================
class ConversationHistory:
    def __init__(self,
                 max_history: int = 5):
        self._history: Dict[str, List[Dict]] = {}
        self.max_history = max_history
    
    def add_message(self,
                    user_id: str,
                    role: str,
                    content: str):
        if user_id not in self._history:
            self._history[user_id] = []
        self._history[user_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        if len(self._history[user_id]) > self.max_history * 2:
            self._history[user_id] = self._history[user_id][-self.max_history * 2:]
    
    def get_history(self, user_id: str) -> List[Dict]:
        return self._history.get(user_id, [])
    
    def clear_history(self, user_id: str):
        if user_id in self._history:
            del self._history[user_id]

conversation_manager = ConversationHistory()


# ============================================================================
# RAG Chatbot (Hybrid Streaming Version)
# ============================================================================
class RAGChatbot:
    """
    EXAONE 기반 Hybrid 챗봇
    
    🚀 특징:
        - 데이터: 코드로 확실하게 포맷팅 (채용공고, 부트캠프)
        - AI: 인사말, 코멘트, 마무리만 생성
        - 스트리밍으로 자연스러운 UX
    """
    # ========================================================================
    # 클래스 변수
    # Bootcamps DB 조회 시 사용
    # table: jabcategories
    # column: category_name
    # ========================================================================
    CATEGORY_KEYWORDS = {
        'Backend Developer': [
            'backend', '백엔드', 'server', 'api', 'spring', 'django', 'flask',
            'fastapi', 'node.js', 'express', 'nest.js', 'java', 'python server',
            'go server', 'kotlin server', 'restful', 'graphql'
        ],
        'Frontend Developer': [
            'frontend', '프론트엔드', 'react', 'vue', 'angular', 'next.js',
            'javascript', 'typescript', 'html', 'css', 'sass', 'webpack',
            'web developer', '웹 개발'
        ],
        'Full Stack Developer': [
            'full stack', '풀스택', 'fullstack'
        ],
        'AI/ML Engineer': [
            'ai', 'ml', 'machine learning', 'deep learning', 'nlp', 'computer vision',
            'tensorflow', 'pytorch', 'keras', '딥러닝', '머신러닝', '인공지능',
            'llm', 'gpt', 'model', 'data scientist', 'deep_learning'
        ],
        'Data Engineer': [
            'data engineer', '데이터 엔지니어', 'etl', 'data pipeline', 'airflow',
            'spark', 'hadoop', 'kafka', 'data warehouse', 'bigquery', '데이터분석'
        ],
        'Data Analyst': [
            'data analyst', '데이터 분석', 'bi', 'tableau', 'power bi', 'sql',
            'data visualization', '데이터 시각화', '데이터분석'
        ],
        'DevOps Engineer': [
            'devops', 'sre', 'infrastructure', '인프라', 'kubernetes', 'docker',
            'ci/cd', 'jenkins', 'terraform', 'ansible', 'aws', 'gcp', 'azure',
            'cloud engineer', 'cloud'
        ],
        'Mobile Developer': [
            'mobile', 'android', 'ios', 'react native', 'flutter', 'swift',
            'kotlin', '모바일', 'app developer'
        ],
        'Security Engineer': [
            'security', '보안', 'infosec', '정보보안', 'penetration', 'vulnerability',
            '보안솔루션', 'firewall', 'ids', 'ips'
        ],
        'QA Engineer': [
            'qa', 'quality assurance', 'test', '테스트', 'automation test',
            'selenium', 'cypress'
        ],
        'Product Manager': [
            'product manager', 'pm', 'po', 'product owner', '기획', '서비스 기획'
        ],
        'UI/UX Designer': [
            'ui', 'ux', 'designer', '디자이너', 'figma', 'sketch', 'prototype'
        ],
        'Database Engineer': [
            'dba', 'database', '데이터베이스', 'postgresql', 'mysql', 'oracle',
            'mssql', 'mongodb', 'db admin'
        ],
        'Blockchain Developer': [
            'blockchain', '블록체인', 'solidity', 'ethereum', 'web3', 'defi', 'nft'
        ],
        'Game Developer': [
            'game', '게임', 'unity', 'unreal', 'c++', 'graphics'
        ],
    }

    def __init__(
        self,
        base_model_name: str = "LGAI-EXAONE/EXAONE-3.5-7.8B-Instruct",
        lora_model_path: str = "ai/models/checkpoint-460",
        use_4bit: bool = True
    ):
        print("🚀 Initializing RAG Chatbot (Hybrid Streaming)...")
        
        os.makedirs("./offload",
                    exist_ok = True)
        
        self.tokenizer = AutoTokenizer.from_pretrained(
            base_model_name,
            trust_remote_code = True
        )
        
        bnb_config = None
        if use_4bit:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit = True,
                bnb_4bit_compute_dtype = torch.float16,
                bnb_4bit_quant_type = 'nf4',
                bnb_4bit_use_double_quant = True,
            )
        
        print(f"📥 Loading: {base_model_name}")
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            quantization_config = bnb_config,
            device_map = 'auto',
            trust_remote_code = True,
            low_cpu_mem_usage = True,
            max_memory = {0: "6GiB", "cpu": "16GiB"},
            offload_folder = "./offload",
        )
        print("✅ Base model loaded!\n")
        print(f"📥 Loading: {lora_model_path}")
        
        if lora_model_path and os.path.exists(lora_model_path):
            print(f"📦 Loading LoRA: {lora_model_path}")
            self.model = PeftModel.from_pretrained(base_model, lora_model_path)
        else:
            self.model = base_model
        print("✅ Trained model loaded!\n")
        print("✅ Hybrid Streaming Chatbot ready!\n")


    # ========================================================================
    # model generate 함수
    # ========================================================================
    def generate(self,
                 prompt: str,
                 max_tokens: int = 128) -> str:
        """LLM 호출 메서드"""
        inputs = self.tokenizer(prompt, return_tensors = 'pt').to(self.model.device)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens = max_tokens,
            do_sample = True,
            temperature = 0.7,
            top_p = 0.9
        )
        return self.tokenizer.decode(outputs[0], skip_special_tokens = True)

    # ========================================================================
    # category_name: skills 매칭 함수
    # table: jabcategories
    # column: category_name
    # ========================================================================
    def match_category(self,
                       query: str) -> str:
        """
        사용자 query를 CATEGORY_KEYWORDS 기반으로 카테고리 매칭
        """
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in query.lower():
                    return category
        return None

# 추천 방식을 기존 LLM -> embedding vector 유사도로 변경
#     def score_with_exaone(self,
#                           query: str,
#                           education_content: str):
#         """
#         EXAONE 모델을 호출해 query와 education_content의 매칭 점수를 0~100으로 평가
#         """
#         prompt = f"""[|system|]너는 분석가야.
# 사용자 입력: "{query}"
# 부트캠프 교육 내용: "{education_content}"

# 위 사용자 입력과 부트캠프 교육 내용이 얼마나 잘 맞는지 0~100 사이 점수로 평가해.
# 그리고 그 이유를 1-2문장으로 설명해 줘.

# 출력 형식:
# 점수: <숫자만>
# 이유: <30자 이내 한 문장>[|endofturn|]
# [|assistant|]"""
#         # 1. 문자열(query) -> tokenize -> tensor 변환
#         inputs = self.tokenizer(prompt, return_tensors = 'pt').to(self.model.device)

#         # 2. 모델 generate 호출 (텐서 반환)
#         response = self.model.generate(**inputs, # 토큰화된 텐서 전달
#                                        max_new_tokens = 100, # 새로 생성할 토큰 수 제한
#                                        num_return_sequences = 1, # 생성할 응답 개수
#                                        do_sample = True, # 샘플링 활성화
#                                        temperature = 0.7)  # 샘플링 온도 (창의성 조절) // 0이면 계속 같은 대답
        
#         # 3. 디코딩 (문자열 반환)
#         decoded = self.tokenizer.decode(response[0], skip_special_tokens = False)

#         # 4. 디코딩 -> [|assistant|] 이후 텍스트만 추출
#         if "[|assistant|]" in decoded:
#             decoded = decoded.split("[|assistant|]")[-1]

#         # 5. [|endofturn|] 제거
#         if "[|endofturn|]" in decoded:
#             decoded = decoded.split("[|endofturn|]")[0]

#         # 6. Ai의 점수 및 추천 이유 파싱
#         score, reason = 0, ''

#         for line in decoded.splitlines():  # splitlines: 문자열 사용
#             if line.startswith("점수:"):
#                 # 숫자만 추출 (정규식으로 명시적 지정)
#                 match = re.search(r'\d+', line)

#                 if match:
#                     score = int(match.group())
#             elif line.startswith("이유:"):
#                 reason = line.replace("이유:", "").strip()
        
#         return score, reason

    # def recommend_bootcamps(self,
    #                         query: str,
    #                         db: Session,
    #                         limit: int = 3):
    #     """
    #     사용자 query 기반으로 부트캠프 추천 (카테고리 매칭 + EXAONE 점수 + 랜덤 샘플링)
    #     """
    #     # 1. 카테고리 추출
    #     category = self.match_category(query)

    #     # 2. DB 검색
    #     bootcamps = self.search_bootcamps(db, category_name = category, limit = 10)
    #     if not bootcamps:
    #         return []

    #     # 3. AI 점수 + 추천 이유 생성
    #     scored = []
    #     for bc in bootcamps:
    #         score, reason = self.score_with_exaone(query, bc.get('educationcontent', ''))
    #         scored.append((bc, score, reason))

    #     # 4. 점수 높은 순으로 정렬
    #     scored.sort(key = lambda x: x[1], reverse = True)

    #     # 5. 상위 5개 중 랜덤으로 limit개 뽑기
    #     top_candidates = scored[:5]

    #     # recommended: Tutle #[(bc_dict, score, reason), ...]
    #     recommended = random.sample(top_candidates, k = min(limit, len(top_candidates)))
        
    #     # card 형식으로 변환
    #     cards = []
    #     for bc, score, reason in recommended:
    #         name_display = bc.get('name', '부트캠프')
    #         if bc.get('url'):
    #             name_display = f"[{bc.get('name', '부트캠프')}]({bc['url']})"
    #         card = {
    #             'name': name_display,                  # MarkDown형식 link
    #             'subtitle': f'점수: {score}',          # 점수
    #             'description': f'추천이유: {reason}',  # 추천 이유
    #             'extra': {                            # 부가 항목 모음
    #                 'category': bc.get('category_name', ''),
    #                 'link': bc.get('url', ''), # 원본 url 그대로 저장
    #                 'cost_type': bc.get('cost_type', ''), # 국비 | 본인부담
    #                 'institute': bc.get('institute', ''), # 기관명   
    #                 'online_offline': bc.get('online_offline'), # 온라인 | 오프라인
    #                 'educationcontent': bc.get('educationcontent'), # 수업내용
    #                 'location': bc.get('location', ''), # 주소
    #             }
    #         }
    #         cards.append(card)

    #     return cards
    
    # 'name': bc.Title or '부트캠프명 없음',
    # 'institute': bc.InstituteName or '기관명 없음',
    # 'cost_type': bc.CostSupportType or '본인부담',
    # 'location': bc.Location or '온라인',
    # 'online_offline': bc.OnlineOffline or '온라인',
    # 'url': bc.DetailUrl or '',
    # 'educationcontent': bc.EducationContent or '',
    # 'category_name': bc.job_category.CategoryName if bc.job_category else ''

    # 출력 예: List[Tuple]
    # [
    #     {
    #         "name": "[Django 백엔드 과정](https://example.com/django-bootcamp)",
    #         "subtitle": "점수: 85",
    #         "description": "사용자가 Django를 배우고 싶다고 했기 때문에 이 과정이 적합합니다.",
    #         "extra": {
    #         "category": "Backend Developer",
    #         "link": "https://example.com/django-bootcamp"
    #         }
    #     },
    # ]


    # ========================================================================
    # DB 조회 함수들
    # ========================================================================
    def get_user_skills(self,
                        db: Session,
                        user_id: int) -> List[str]:
        from src.models import User
        try:
            user = db.query(User).filter(User.UserID == user_id).first()
            if user and user.skills:
                return [skill.SkillName for skill in user.skills]
        except Exception as e:
            print(f"Error: {e}")
        return []

    def extract_profile(self,
                        query: str) -> Dict:
        query_lower = query.lower()
        profile = {'skills': [], 'location': None, 'experience': None}
        
        skill_mapping = {
            'python': 'Python', '파이썬': 'Python',
            'java': 'Java', '자바': 'Java',
            'javascript': 'JavaScript', 'js': 'JavaScript',
            'react': 'React', '리액트': 'React',
            'fastapi': 'FastAPI', 'git': 'git',
            'github': 'github', 'ai': 'ai',
            '에이아이': 'ai', 'deep-learning': 'Deep-Learning',
            'Deep-Learning': 'Deep-Learning', 'C': 'C',
            'C++': 'C++', 'C#': 'C#',
            'vue': 'Vue', 'django': 'Django',
            'spring': 'Spring',
            'node': 'Node.js', 'typescript': 'TypeScript',
            'postgresql': 'PostgreSQL', 'mysql': 'MySQL',
            'docker': 'Docker', 'kubernetes': 'Kubernetes',
            'aws': 'AWS', 'machine learning': 'Machine_Learning',
            '머신러닝': 'Machine_Learning', 'ml': 'Machine_Learning',
        }
        
        for key, normalized in skill_mapping.items():
            if key in query_lower and normalized not in profile['skills']:
                profile['skills'].append(normalized)
        
        regions = {'서울': '서울', '부산': '부산', '대구': '대구', '인천': '인천',
                   '경기': '경기', '대전': '대전', '광주': '광주', '제주': '제주'}
        for key, value in regions.items():
            if key in query_lower:
                profile['location'] = value
                break
        
        if any(w in query_lower for w in ['신입', 'junior', '주니어', '초보']):
            profile['experience'] = '신입'
        elif any(w in query_lower for w in ['경력', 'senior', '시니어']):
            profile['experience'] = '경력'
        
        return profile

    def get_query_embedding(self,
                            query: str) -> list:
        '''
        사용자 쿼리를 768차원 벡터로 변환
        
        비유: 사용자의 질문을 "숫자 지문"으로 바꾸는 과정
            이 지문으로 DB에서 비슷한 지문을 가진 공고를 찾음
        
        Args:
            query: 사용자 질문 (예: "Python 백엔드 개발자 채용")
        
        Returns:
            list[float]: 768차원 벡터 (숫자 리스트)
        '''
        embedding = SBERT_MODEL.encode(query)
        return embedding.tolist()

    def preprocess_query_for_embedding(self, query: str) -> str:
        '''
        사용자 쿼리를 임베딩 검색에 최적화된 형태로 변환
        
        비유: 도서관 검색 시스템에 맞게 검색어 다듬기
            "python 신입 채용" → "제목: python 개발자. 경력: 신입."
        
        Args:
            query: 원본 사용자 쿼리
        
        Returns:
            str: 전처리된 쿼리
        '''
        # 프로필 추출 (기존 함수 활용)
        profile = self.extract_profile(query)
        
        # 임베딩 텍스트 형식과 유사하게 구성
        parts = []
        
        if profile['skills']:
            parts.append(f"주요스킬: {', '.join(profile['skills'])}")
        
        if profile['experience']:
            parts.append(f"경력: {profile['experience']}")
        
        if profile['location']:
            parts.append(f"지역: {profile['location']}")
        
        # 원본 쿼리도 포함 (의미 보존)
        parts.append(query)
        
        return '. '.join(parts)

    def search_jobs(self,
                    db: Session,
                    profile: Dict,
                    limit: int = 3) -> List[Dict]:
        from src.models import JobPost, Skill
        query = db.query(JobPost).filter(JobPost.IsActive == True)
        
        if profile['skills']:
            query = query.join(JobPost.skills).filter(
                or_(*[Skill.SkillName.ilike(f"%{s}%") for s in profile['skills']])
            )
        if profile['location']:
            query = query.filter(JobPost.Location.ilike(f"%{profile['location']}%"))
        if profile['experience']:
            query = query.filter(JobPost.ExperienceRequirement.ilike(f"%{profile['experience']}%"))
        
        results = query.limit(limit).all()
        return [{
            'company': job.CompanyName or '회사명 미공개',
            'title': job.Title or '직무명 없음',
            'location': job.Location or '위치 미정',
            'experience': job.ExperienceRequirement or '무관',
            'salary': job.Salary or '협의',
            'skills': [s.SkillName for s in job.skills] if job.skills else [],
            'url': job.Url or '',
        } for job in results]

    def search_jobs_by_vector(self, db: Session,
                              query: str,
                              limit: int = 3) -> List[Dict]:
        '''
        벡터 유사도 기반 채용공고 검색
        
        비유: 도서관에서 책 찾기
            - 기존 방식: 제목에 "Python" 단어가 있는 책 찾기 (키워드)
            - 벡터 방식: "Python 개발" 느낌과 비슷한 책 찾기 (의미)
        
        Args:
            db: SQLAlchemy 세션
            query: 사용자 질문
            limit: 반환할 결과 수 (기본값: 3)
        
        Returns:
            List[Dict]: 채용공고 리스트 (유사도 높은 순)
        '''
        from src.models import JobPost  # 순환 import 방지
        
        # 1. 쿼리를 벡터로 변환
        # query_vector = self.get_query_embedding(query)
        processed_query = self.preprocess_query_for_embedding(query)
        logging.debug(f'[VECTOR] Processed query: {processed_query}') # DEBUG용
        query_vector = self.get_query_embedding(processed_query)
        
        # 2. cosine 유사도로 검색 (pgvector: <=> 연산자 = cosine 거리)
        #    거리가 작을수록 유사도가 높음 → order by 오름차순
        #    임계값 0.5 초과만 추천
        jobs = db.query(JobPost).filter(
            JobPost.Embeded.isnot(None),  # 벡터가 있는 것만
            # JobPost.Embeded.cosine_distance(query_vector) < 0.1 # 임시로 임계값 없앰
        ).order_by(
            JobPost.Embeded.cosine_distance(query_vector)  # 거리 기준 정렬
        ).limit(limit).all()

        # 유사도 debug용 코드
        # for job in jobs:
        #     distance = db.query(
        #         JobPost.Embeded.cosine_distance(query_vector)
        #     ).filter(JobPost.Id == job.Id).scalar()
        #     logging.debug(f"[VECTOR] {job.Title}: distance={distance}")

        for job in jobs:
            logging.debug(f"[VECTOR] Result: {job.Title} | Company: {job.CompanyName}")
        
        # 3. 기존 search_jobs()와 동일한 형식으로 반환
        results = []
        for job in jobs:
            results.append({
                'company': job.CompanyName or '회사명 미공개',
                'title': job.Title or '직무명 없음',
                'location': job.Location or '위치 미정',
                'experience': job.ExperienceRequirement or '무관',
                'salary': job.Salary or '협의',
                'skills': [s.SkillName for s in job.skills] if job.skills else [],
                'url': job.Url or '',
            })

        return results

    def search_bootcamps(self,
                         db: Session,
                         missing_skills: List[str] = None,
                         category_name: str = None,
                         limit: int = 2) -> List[Dict]:
        from src.models import BootcampPost, JobCategory
        query = db.query(BootcampPost)
        
        # 사용자의 부족한 스킬 기반 필터링
        if missing_skills:
            filters = [BootcampPost.EducationContent.ilike(f"%{s}%") for s in missing_skills]
            if filters:
                query = query.filter(or_(*filters))
        
        # 카테고리 이름 기반 필터링 (JobCategory와 조인)
        if category_name:
            query = query.join(BootcampPost.job_category).filter(JobCategory.CategoryName == category_name)

        # 정렬: 국비지원 우선 -> 조회수 순
        query = query.order_by(BootcampPost.CostSupportType.desc(), BootcampPost.ViewCount.desc())
        results = query.limit(limit).all()

        # Dict 형태로 변환
        return [{
            'name': bc.Title or '부트캠프명 없음',
            'institute': bc.InstituteName or '기관명 없음',
            'cost_type': bc.CostSupportType or '본인부담',
            'location': bc.Location or '온라인',
            'online_offline': bc.OnlineOffline or '온라인',
            'url': bc.DetailUrl or '',
            'educationcontent': bc.EducationContent or '',
            'category_name': bc.job_category.CategoryName if bc.job_category else ''
        } for bc in results]

    def search_bootcamps_by_vector(self, db: Session,
                                   query: str,
                                   limit: int = 2) -> List[Dict]:
        '''
        벡터 유사도 기반 부트캠프 검색
        
        Args:
            db: SQLAlchemy 세션
            query: 사용자 질문
            limit: 반환할 결과 수 (기본값: 2)
        
        Returns:
            List[Dict]: 부트캠프 리스트 (_format_bootcamp_card 호환 형식)
        '''
        from src.models import BootcampPost  # 순환 import 방지
        
        # 1. 쿼리를 벡터로 변환
        query_vector = self.get_query_embedding(query)
    
        # 2. cosine 유사도로 검색
        #    임계값 0.5 초과만 추천
        bootcamps = db.query(BootcampPost).filter(
            BootcampPost.Embeded.isnot(None),
            # BootcampPost.Embeded.cosine_distance(query_vector) < 0.1 # 임시로 임계값 없앰
        ).order_by(
            BootcampPost.Embeded.cosine_distance(query_vector)
        ).limit(limit).all()

        # for bc in bootcamps:
        #     logging.debug(f"[VECTOR] Result: {bc.Title} | Company: {bc.CompanyName}")
        
        # 3. _format_bootcamp_card()가 기대하는 형식으로 반환
        results = []
        for bc in bootcamps:
            # 카테고리명 안전하게 가져오기
            category_name = ''
            if bc.job_category:
                category_name = bc.job_category.CategoryName
            
            # 필요없는 old_column 수정
            results.append({
                # _format_bootcamp_card()가 직접 사용하는 키
                'name': bc.Title or '부트캠프명 없음',
                'description': (bc.EducationContent or '').replace('\n', '').replace('\r', ' ')[:40] + '...' if bc.EducationContent and len(bc.EducationContent) > 100 else (bc.EducationContent or '교육 내용 없음'),
                
                # _format_bootcamp_card()가 extra에서 가져오는 키
                'extra': {
                    'institute': bc.InstituteName or '기관명 없음',
                    'cost_type': bc.CostSupportType or '본인부담',
                    'online_offline': bc.OnlineOffline or '온라인',
                    'location': bc.Location or '온라인',
                    'category': category_name,
                    'link': bc.DetailUrl or '',
                }
            })
        
        logging.debug(f"[VECTOR] Found {len(results)} bootcamps")  # 디버깅용
        return results

    def analyze_skill_gap(self,
                          user_skills: List[str],
                          job_skills: List[str]) -> Dict:
        if not job_skills:
            return {
                'match_rate': 100,
                'matched': [],
                'missing': [],
                'gap_level': 'none'
                }
        
        user_lower = [s.lower() for s in user_skills]
        # matched = [s for s in job_skills if s.lower() in user_lower]
        # 사용자 스킬 기준으로 매칭된 것을 반환
        job_lower = [s.lower() for s in job_skills]
        matched = [s for s in user_skills if s.lower() in job_lower]
        missing = [s for s in job_skills if s.lower() not in user_lower]
        rate = len(matched) / len(job_skills) * 100 if job_skills else 100
        
        level = 'minor' if rate >= 80 else 'moderate' if rate >= 50 else 'major'
        
        logging.debug(f"[DEBUG] user_skills: {user_skills}")
        logging.debug(f"[DEBUG] job_skills: {job_skills}")
        logging.debug(f"[DEBUG] matched: {matched}")
        logging.debug(f"[DEBUG] missing: {missing}")
        logging.debug(f"[DEBUG] rate: {rate}")

        return {
            'match_rate': round(rate),
            'matched': matched,
            'missing': missing,
            'gap_level': level
            }

    # ========================================================================
    # 🔥 코드로 확실하게 포맷팅하는 함수들
    # ========================================================================
    def _format_job_card(self, job: Dict, index: int, gap: Dict = None) -> str:
        """채용공고 카드 포맷팅 - 코드로 확실하게!"""
        skills_str = ', '.join(job['skills'][:4]) if job['skills'] else '스킬 미기재'
        
        # # 매칭률 이모지
        # match_emoji = "🟢"
        # if gap:
        #     if gap['match_rate'] >= 70:
        #         match_emoji = "🟢"
        #     elif gap['match_rate'] >= 40:
        #         match_emoji = "🟡"
        #     else:
        #         match_emoji = "🔴"
        
        # URL이 있으면 Markdown 링크
        company_display = job['company']
        if job.get('url'):
            company_display = f"[{job['company']}]({job['url']})"
        
        card = f"""
🏢 **{company_display}**
    📌 {job['title']}
    📍 {job['location']} | 💼 {job['experience']} | 💰 {job['salary']}
    🛠️ {skills_str}"""
        
        # if gap:
        #     card += f"\n│ {match_emoji} 매칭률 {gap['match_rate']}%"
        #     if gap['missing']:
        #         card += f" (부족: {', '.join(gap['missing'][:2])})"

        return card

    # def _format_bootcamp_card(self, bc: Dict) -> str:
    #     """부트캠프 카드 포맷팅 - 코드로 확실하게!"""
    #     cost_emoji = "🆓" if "국비" in bc['cost_support'] else "💳"
        
    #     # URL이 있으면 Markdown 링크
    #     name_display = bc['name']
    #     if bc.get('url'):
    #         name_display = f"[{bc['name']}]({bc['url']})"
        
    #     return f"• 🎓 {name_display}\n  📍 {bc['institute']} | {cost_emoji} {bc['cost_support']} | {bc['online_offline']}"

    def _format_bootcamp_card(self,
                              card: Dict) -> str:
        """부트캠프 추천 카드 포맷팅"""
        cost_emoji = "🆓" if "국비" in card['extra'].get('cost_type', '') else "💳"

        # 이름을 Markdown 링크로 변환
        # URL이 있으면 Markdown 링크
        name_display = card.get('name', '부트캠프명 없음')
        if card['extra'].get('link'):
            name_display = f"[{name_display}]({card['extra']['link']})"

        formatted = f"""\
    🎓 {name_display}
        📍 {card['extra'].get('institute', '기관 미기재')} | {cost_emoji} {card['extra'].get('cost_type', '')} | {card['extra'].get('online_offline', '')}
        📍 {card['extra'].get('location', '온라인')}
        💡 {card.get('description', '')}
    """
        return formatted


    # ========================================================================
    # 🔥 AI 프롬프트 (짧게! 인사/코멘트만)
    # ========================================================================
    def _build_greeting_prompt(self, query: str, user_skills: List[str], job_count: int) -> str:
        """
        인사말 생성용 짧은 프롬프트
        기존: 너무 모호한 지시.
        개선: 명확한 지시.
        """
        skills_str = ', '.join(user_skills) if user_skills else '스킬 미입력'
        
        return f"""[|system|]너는 MatchIT 취업 도우미야. 
정중하고 친근하게 인사해. 2~4문장으로만 답해.[|endofturn|]
[|user|]사용자가 "{query}"라고 검색한 내용을 찾아보고, 안내해 줘.
1. 반갑다는 인사
2. 간단한 안내말
2~4문장으로만 답해![|endofturn|]
[|assistant|]"""

#     def _build_comment_prompt(self, job: Dict, gap: Dict) -> str:
#         """채용공고별 코멘트 생성용 짧은 프롬프트"""
#         return f"""[|system|]너는 취업 도우미야. 이 채용공고에 대해 2~4문장으로 각 공고에 대한 평가와 부족한 스킬별 학습 방법을 코멘트 해줘.[|endofturn|]
# [|user|]회사: {job['company']}
# 직무: {job['title']}
# 매칭률: {gap['match_rate']}%
# 부족 스킬: {', '.join(gap['missing'][:2]) if gap['missing'] else '없음'}
# 이 공고를 추천해 준 이유에 대해서 코멘트 해줘![|endofturn|]
# [|assistant|]"""

#     def _build_closing_prompt(self, missing_skills: List[str], has_bootcamps: bool) -> str:
#         """마무리 멘트 생성용 짧은 프롬프트 - 간결하게"""
        
#         return f"""[|system|]너는 MatchIT 취업 도우미야.
# 반말로 짧게 응원해. 반드시 1문장으로만![|endofturn|]
# [|user|]사용자에게 응원 한마디 해줘.
# 1문장으로만! 이모지 1개만 써![|endofturn|]
# [|assistant|]"""

    def _build_recommendation_reason_prompt(self, 
                                            query: str,
                                            user_skills: List[str],
                                            jobs: List[Dict],
                                            overall_gap: Dict,
                                            bootcamps: List[Dict]) -> str:
        """
        추천 이유 생성용 프롬프트
            - 기존: 부정적인 표현 ("너 이거 부족해")
            - 개선: 긍정적인 표현 ("이거 배우면 더 좋아!")
        """
        # 사용자 스킬
        user_skills_str = ', '.join(user_skills) if user_skills else '아직 입력 안 됨'

        # 배우면 좋은 스킬 (상위 3개)
        missing_skills = overall_gap.get('missing', [])[:3]
        missing_skills_str = ', '.join(missing_skills) if missing_skills else '없음'

        # 회사명 (최대 3개)
        company_names = [job.get('company', '')[:10] for job in jobs[:2]]
        companies_str = ', '.join(company_names) if company_names else "여러 회사"
        
        # 부트캠프 이름
        bootcamp_name = ''
        if bootcamps and len(bootcamps) > 0:
            bootcamp_name = bootcamps[0].get('name', '')[:40]
        
        return f"""[|system|]너는 MatchIT 커리어 전문 코치야 5~7문장 말해줘.[|endofturn|]
[|user|]아래 예시처럼 5~7문장으로 조언해줘.

[정보]
사용자 스킬: {user_skills_str}
추천 회사: {companies_str}
배우면 좋을 스킬: {missing_skills_str}

[예시]
1. 자연스러운 말투로 사용자 스킬 칭찬하기
2. 추천 회사들의 공통된 요구 스킬 언급하기
3. 추천하는 부트캠프의 스킬도 몇개 언급하기
4. 응원의 메시지

"{user_skills_str}" 스킬 좋아! {companies_str} 같은 회사들이 {missing_skills_str}도 원해. 그래서 {missing_skills_str} 중 하나 배우면 선택지가 넓어져! 위 부트캠프도 참고해봐, 화이팅!


회사명이나 스킬만 나열하지 말고 자연스럽게 말해![|endofturn|]
[|assistant|]"""

    # ========================================================================
    # 🔥 AI 텍스트 생성 (짧은 응답용)
    # ========================================================================
    def _generate_short_response(self,
                                 prompt: str,
                                 max_tokens: int = 100) -> str:
        """짧은 AI 응답 생성 (스트리밍 아님)"""
        inputs = self.tokenizer(
            prompt,
            return_tensors = "pt",
            truncation = True,
            max_length = 512
        ).to(self.model.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens = max_tokens,
                temperature = 0.7,
                do_sample = True,
                top_p = 0.9,
                repetition_penalty = 1.1,
                pad_token_id = self.tokenizer.eos_token_id,
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens = False)
        
        # [|assistant|] 이후 텍스트만 추출
        if "[|assistant|]" in response:
            response = response.split("[|assistant|]")[-1]
        
        # 종료 토큰 제거
        if "[|endofturn|]" in response:
            response = response.split("[|endofturn|]")[0]
        
        return response.strip()

    # ========================================================================
    # 🔥 AI 텍스트 생성 (streaming ver.)
    # ========================================================================
    def _generate_stream_response(self, prompt: str, max_tokens: int = 100) -> Generator[str, None, None]:
        """AI 응답을 토큰 단위로 스트리밍"""
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(self.model.device)
        
        # 스트리머 생성
        streamer = TextIteratorStreamer(self.tokenizer, skip_special_tokens=False)
        
        # 별도 스레드에서 생성
        generation_kwargs = {
            **inputs,
            "max_new_tokens": max_tokens,
            "temperature": 0.7,
            "do_sample": True,
            "top_p": 0.9,
            "repetition_penalty": 1.1,
            "pad_token_id": self.tokenizer.eos_token_id,
            "streamer": streamer,
        }
        
        thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
        thread.start()
        
        # 토큰 단위로 yield
        started = False
        for token in streamer:
            # [|assistant|] 이후부터 출력
            if "[|assistant|]" in token:
                started = True
                token = token.split("[|assistant|]")[-1]
            
            if started:
                # 종료 토큰이면 중단
                if "[|endofturn|]" in token:
                    token = token.split("[|endofturn|]")[0]
                    if token:
                        yield token
                    break
                yield token
        
        thread.join()

    # ========================================================================
    # 🔥 Hybrid 스트리밍 Chat (핵심!)
    # ========================================================================
    def chat_stream(self, query: str,
                    db: Session,
                    user_id: str = None) -> Generator[str, None, None]:
        """
        chat_stream() 흐름:

        1. AI 인사말 (LLM 호출 1회)
        2. 채용공고 카드 3개 (코드로 생성, embedding 유사도 길이)
        3. 스킬 분석 (코드로 생성, LLM 없음) -> 삭제
        4. 부트캠프 카드 2개 (코드로 생성, embedding 유사도 길이)
        4.5 추천 이유 (LLM 호출 1회) ← 추가!
        5. AI 마무리 (LLM 호출 1회) -> 삭제

        총 LLM 호출: 2회 (인사말 + 추천이유 1회 = 사실상 비슷)
        """
        try:
            # 0. LangChain 도입 비교를 위해 시간 측정
            start_time = time.perf_counter()

            # 1. 프로필 추출 & 검색
            profile = self.extract_profile(query)
            print(f"[hybrid] Profile: {profile}")
            
            # 2. 사용자 스킬
            user_skills = []
            if user_id:
                try:
                    user_skills = self.get_user_skills(db, int(user_id))
                except:
                    pass
            if profile['skills']:
                for s in profile['skills']:
                    if s not in user_skills:
                        user_skills.append(s)
            
            # 3. 채용공고 검색
            # jobs = self.search_jobs(db, profile, limit=3)
            jobs = self.search_jobs_by_vector(db, query, limit = 20) # 여유있게 6개
            print(f"[hybrid] Found {len(jobs)} jobs")

            # 추가: matched 스킬이 1개 이상인 것만 필터링
            filtered_jobs = []
            for job in jobs:
                job_gap = self.analyze_skill_gap(user_skills, job['skills'])
                if job_gap['matched']:  # matched가 있으면 == 1개 이상이면
                    filtered_jobs.append(job)
                if len(filtered_jobs) >= 3: # 최대 3개
                    break
            jobs = filtered_jobs
            
            if not jobs:
                yield "음... 조건에 맞는 공고를 못 찾았어 😅\n\n다른 스킬이나 지역으로 검색해볼까?"
                return
            
            # 4. 스킬 갭 분석
            all_skills = list(set(s for j in jobs for s in j.get('skills', [])))
            overall_gap = self.analyze_skill_gap(user_skills, all_skills)
            
            # 5. 부트캠프 검색
            bootcamps = []
            if overall_gap['missing']:
                # LLM 직접 확인&추천
                # bootcamps = self.recommend_bootcamps(query, db, limit = 2)

                # Vector cosine 유사도 query 추천(job과 같음)
                # bootcamps = self.search_bootcamps_by_vector(db, query, limit = 2) 
                
                # query에서 부족한 스킬로 부트캠프 검색
                missing_skills_str = ', '.join(overall_gap['missing'][:4])
                missing_skills_query = f'주요스킬: {missing_skills_str}. 개발자 교육 부트캠프'
                logging.debug(f'[DEBUG] Bootcamp search query: {missing_skills_query}') # 디버깅 -> logging
                bootcamps = self.search_bootcamps_by_vector(db, missing_skills_query, limit = 2)
            
            
            # ═══════════════════════════════════════════════════════════════
            # 🔥 Hybrid 응답 시작!
            # ═══════════════════════════════════════════════════════════════
            
            full_response = ""
            
            # ─────────────────────────────────────────────────────────────
            # Part 1: AI 인사말
            # ─────────────────────────────────────────────────────────────
            greeting_prompt = self._build_greeting_prompt(query, user_skills, len(jobs))

            # 한꺼번에 출력
            greeting = self._generate_short_response(greeting_prompt, max_tokens = 100)

            # 인사말
            # 하기 뒤아래 부분을 추가하므로써 프론트에서 해당 부분이 AI 응답 부분인걸 인식!!!
            yield "<!-- AI_GREETING -->\n"
            yield greeting
            # streaming 방식 출력 (token 단위 출력)
            # for token in self._generate_stream_response(greeting_prompt, max_tokens = 80):
            #     yield token
            yield "\n<!-- /AI_GREETING -->\n"
            full_response += greeting + "\n\n"
            
            # ─────────────────────────────────────────────────────────────
            # Part 2: 채용공고 카드 (코드로 확실하게!)
            # ─────────────────────────────────────────────────────────────
            jobs_header = f"\n\n📋 **검색된 채용공고 {len(jobs)}건**\n\n"
            yield "<!-- JOB_CARDS -->\n"
            yield jobs_header
            full_response += jobs_header
            
            for i, job in enumerate(jobs):
                print(f"[DEBUG] Job {i+1}: {job['company']}")
                job_gap = self.analyze_skill_gap(user_skills, job['skills'])
                
                # 🔥 직접 문자열 생성 (함수 호출 대신)
                skills_str = ', '.join(job['skills'][:4]) if job['skills'] else '스킬 미기재'
                # match_emoji = "🟢" if job_gap['match_rate'] >= 70 else "🟡" if job_gap['match_rate'] >= 40 else "🔴"
                
                # URL 링크
                company_display = job['company']
                if job.get('url'):
                    company_display = f"[{job['company']}]({job['url']})"
                
                # 🔥 각 줄을 개별 yield로!
                        # ┌───────────────── 실제로 modal 창에서의 width 한계
                        # ┌─────────────────────────────────────
                yield f"🏢 {company_display}\n"
                yield f"📌 {job['title']}\n"
                yield f"📍 {job['location']} | 💼 {job['experience']} | 💰 {job['salary']}\n"
                yield f"🛠️ {skills_str}\n"
                
                # 부정적인 표현으로 UX 저하. 교체
                # match_line = f"│ {match_emoji} 매칭률 {job_gap['match_rate']}%"
                # if job_gap['missing']:
                #     match_line += f" (부족: {', '.join(job_gap['missing'][:2])})"
                # yield match_line + "\n"

                # 🔥 긍정적 표현으로 변경!
                if job_gap['matched']:
                    matched_str = ', '.join(job_gap['matched'][:3])  # 최대 3개만 표시
                    match_line = f"✅ {matched_str} 활용 가능"
                else:
                    match_line = f"📌 새로운 도전 기회!"
                yield match_line + "\n"

                # 🆕 카드 사이 구분선 추가!
                yield "\n───────────────────\n\n"

                # full_response 업데이트
                card = f"""
🏢 {company_display}
📌 {job['title']}
📍 {job['location']} | 💼 {job['experience']} | 💰 {job['salary']}
🛠️ {skills_str}
"""
                if job_gap['matched']:
                    matched_str = ', '.join(job_gap['matched'][:3])  # 최대 3개만 표시
                    match_line = f"✅ {matched_str} 활용 가능"
                else:
                    match_line = f"📌 새로운 도전 기회!"
                full_response += card
                
                print(f"[DEBUG] Card {i+1} yielded")
            yield"<!-- /JOB_CARDS -->\n"
            
            # ─────────────────────────────────────────────────────────────
            # Part 3: 스킬 분석
            # ─────────────────────────────────────────────────────────────
            # 부정적인 표현 -> UX 저하 -> 주석처리
            # if overall_gap['missing']:
            #     yield f"\n📊 **스킬 분석**\n"
            #     yield f"• 매칭률: {overall_gap['match_rate']}%\n"
            #     yield f"• 부족한 스킬: {', '.join(overall_gap['missing'][:4])}\n"
            #     full_response += f"\n📊 **스킬 분석**\n• 매칭률: {overall_gap['match_rate']}%\n• 부족한 스킬: {', '.join(overall_gap['missing'][:4])}\n"
            
            # ─────────────────────────────────────────────────────────────
            # Part 4: 부트캠프 추천 (있으면)
            # ─────────────────────────────────────────────────────────────
            if bootcamps:
                yield "<!-- BOOTCAMP_CARDS -->\n"
                yield f"\n\n📚 **추천 부트캠프**\n\n"
                full_response += f"\n\n📚 **추천 부트캠프**\n\n"
                
                # recommend_bootcamps == bootcamps에서 (bc, score, reason) 반환
                # cards == List(card, card, ...)
                # card == Dict('name': name_display,
                #              'subtitle': f'점수: {score}',
                #              'description': reason,
                #              'extra': {'category': bc.get('category_name', ''),
                #                        'link': bc.get('detail_url', '')
                #                                원본 url 그대로 저장)
                for card in bootcamps:
                    """부트캠프 추천 카드 포맷팅"""
                    cost_emoji = "🆓" if "국비" in card['extra'].get('cost_type', '') else "💳"

                    # 이름을 Markdown 링크로 변환
                    # URL이 있으면 Markdown 링크
                    name_display = card.get('name', '부트캠프명 없음')
                    if card['extra'].get('link'):
                        name_display = f"[{name_display}]({card['extra']['link']})"

                    logging.debug(f'[DEBUG] {name_display}')

                    bc_card = f"""
🎓 {name_display}
📍 {card['extra'].get('institute', '기관 미기재')} | {cost_emoji} {card['extra'].get('cost_type', '')} | {card['extra'].get('online_offline', '')}
📍 {card['extra'].get('location', '온라인')}
💡 {card.get('description', '')}
"""
                    logging.debug(f'[DEBUG] {bc_card}')

                    # 스트리밍 출력
                    yield bc_card + "\n"
                    yield "\n───────────────────\n\n"

                    # 전체 응답 누적
                    full_response += bc_card + "\n"

                yield "<!-- /BOOTCAMP_CARDS -->\n"
                # ─────────────────────────────────────────────────────────────
                # Part 4.5: 부트캠프 추천 이유
                # ─────────────────────────────────────────────────────────────

                # 개선을 위해 주석
                # reason_prompt = self._build_recommendation_reason_prompt(
                #     query, user_skills, jobs, bootcamps
                # )
                # recommendation_reason = self._generate_short_response(reason_prompt, max_tokens=150)
                reason_prompt = self._build_recommendation_reason_prompt(
                    query, user_skills, jobs, overall_gap, bootcamps  # overall_gap 추가!
                )

                # 한꺼번에 출력
                recommendation_reason = self._generate_short_response(reason_prompt, max_tokens = 350)

                yield "<!-- AI_ROADMAP -->\n"
                yield f"\n💡 **추천 스킬 로드맵**\n"

                # streaming 방식 출력 (token 단위로 출력)
                for token in self._generate_stream_response(reason_prompt, max_tokens = 350):
                    yield token
                # yield f"{recommendation_reason}\n"
                yield "<!-- /AI_ROADMAP -->\n"

                full_response += f"\n💡 **추천 스킬 로드맵**\n{recommendation_reason}\n"

            
            # ─────────────────────────────────────────────────────────────
            # Part 5: AI 마무리
            # ─────────────────────────────────────────────────────────────
            # closing_prompt = self._build_closing_prompt(overall_gap['missing'], bool(bootcamps))
            # closing = self._generate_short_response(closing_prompt, max_tokens=80)
            
            # yield "<!-- AI_CLOSING -->\n"
            # yield "\n" + closing
            # yield "\n<!-- /AI_CLOSING -->\n"
            # full_response += "\n" + closing
            
            # 히스토리 저장
            if user_id:
                conversation_manager.add_message(user_id, "user", query)
                conversation_manager.add_message(user_id, "assistant", full_response[:200])
            
            print(f"[hybrid] Complete! Length: {len(full_response)}")
            
            # 0. 측정 종료 시점
            end_time = time.perf_counter()

            elapsed_time = end_time - start_time
            logging.info(f'[TIME] 총 소요 시간: {elapsed_time:.4f} 초')
            
        except Exception as e:
            print(f"[hybrid] Error: {e}")
            import traceback
            traceback.print_exc()
            yield "앗, 오류가 생겼어 😓 다시 시도해줄래?"

    # ========================================================================
    # 기존 chat 함수 (일괄 응답 - 호환성 유지)
    # ========================================================================
    def chat(self, query: str, db: Session, user_id: str = None) -> str:
        """일괄 응답 방식 (기존 호환)"""
        result = ""
        for token in self.chat_stream(query, db, user_id):
            result += token
        return result


# ============================================================================
# Global Instance
# ============================================================================
chatbot: Optional[RAGChatbot] = None

def initialize_chatbot(
    base_model_name: str = "LGAI-EXAONE/EXAONE-3.5-7.8B-Instruct",
    lora_model_path: str = "ai/models/checkpoint-460"
):
    global chatbot
    try:
        chatbot = RAGChatbot(
            base_model_name=base_model_name,
            lora_model_path=lora_model_path,
            use_4bit=True
        )
        return True
    except Exception as e:
        print(f"❌ Init failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_chatbot() -> Optional[RAGChatbot]:
    return chatbot
