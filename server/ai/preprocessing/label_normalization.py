from sklearn.preprocessing import MultiLabelBinarizer
import json
from typing import List

def normalize_skills(skills: List,
                     skill_map = None):
    '''
    스킬 텍스트를 정규화하는 함수
    - 매핑 테이블(skill_map) 적용
    - AI 및 후처리 mapping으로 걸러지지 않은 skill stack은 추가 필요함
    '''

    normalized = []
    for s in skills:
        s_norm = s.lower().strip()  # 1. 소문자 변환 + 공백 제거
        if skill_map and s_norm in skill_map:
            s_norm = skill_map[s_norm]  # 2. 매핑 테이블 적용
        normalized.append(s_norm)
    return sorted(set(normalized))  # 3. 중복 제거 + 정렬


# ===== 매핑 테이블 정의 =====
skill_map = {
    # 언어
    "파이썬": "python", "python": "python", "py": "python",
    "자바": "java", "java": "java",
    "c": "c", "c++": "cpp", "c#": "csharp", "cpp": "cpp",
    "javascript": "javascript", "js": "javascript",
    "typescript": "typescript",

    # 프레임워크/라이브러리
    "spring": "spring", "springboot": "spring", "스프링": "spring",
    "springboot": "spring", "springframework": "spring",
    "react": "react", "react.js": "react", "react-query": "react",
    "reactnative": "react", "react-native": "react", "리액트": "react",
    "fastapi": "fastapi", "fast api": "fastapi",
    "django": "django", "장고": "django",
    "vue": "vue", "vue.js": "vue",
    "node.js": "nodejs", "next.js": "nextjs", "nestjs": "nestjs", "nest.js": "nestjs",
    "restfulapi": "rest_api", "restapi": "rest_api", "restful": "rest_api",

    # 데이터/AI
    "머신러닝": "machine_learning", "ml": "machine_learning", 
    "ai": "ai", "인공지능(ai)": "ai",
    "자연어처리": "nlp", "nlp": "nlp",
    "딥러닝": "deep_learning", "keras": "deep_learning", "deep-learning": "deep_learning",
    "deeplearning": "deep_learning", "dl": "deep_learning",
    "pytorch": "deep_learning", "tensorflow": "deep_learning", "tensor-flow": "deep_learning",
    "langchain": "langchain", "langgraph": "langgraph", "langsmith": "langsmith",
    "langgraphstudio": "langgraph_studio",

    # 클라우드
    "aws": "aws", "azure": "azure", "gcp": "gcp", "ncp": "ncp",
    "클라우드": "cloud", "cloud": "cloud", "cloud운영": "cloud",

    # DevOps/Infra
    "docker": "docker", "kubernetes": "kubernetes", "k8s": "kubernetes",
    "ci/cd": "cicd", "devops": "devops",
    "linux": "linux", "windows": "windows",

    # 데이터베이스
    "mysql": "database", "postgresql": "database", "oracle": "database",
    "mongodb": "database", "몽고": "database",
    "nosql": "database", "sql": "database", "ms sql": "database",

    # 대분류
    "백엔드 개발": "backend", "백엔드 개발자": "backend", "backend": "backend", "backend개발": "backend",
    "back-end": "backend",
    "프론트엔드 개발": "frontend", "프론트엔드 개발자": "frontend", "frontend": "frontend",
    "풀스택 개발자": "full_stack", "fullstack": "full_stack", "fullstack": "full_stack",

    # 기타
    "3d모델링": "3d_모델링",
    "aspice": "a-spice",
    "ai모델개발": "ai_모델개발",
    "angularjs": "angular",
    "chatgpt": "chatgpt",
    "css3": "css",
    "data analytics": "data_analytic",
    "dms": "dbms",
    "rdbms": "dbms",
    "elasticsearch": "elastic_search",
    "golang": "go", "go": "go", "go-lang": "go",
    "html5": "html",
    "itinfrastructure": "in_frastructure",
    "ismsp": "isms-p",
    "iso26262": "iso 26262",
    "iso27701": "iso 27001",
    "java8": "java",
    "llms": "llm",
    "llvm": "llm",
    "sllm": "llm",
}

# 