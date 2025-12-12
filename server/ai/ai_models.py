from sentence_transformers import SentenceTransformer

class ModelManager:
    """ML 모델을 관리하는 클래스"""

    def __init__(self): 
        self.embedding_model = None

    def load_models(self):
        """서버 시작 시 모델 로드"""
        print("📦 임베딩 모델 로딩 중...")
        self.embedding_model = SentenceTransformer('jhgan/ko-sbert-nli')
        print("✅ 임베딩 모델 로드 완료!")

    def unload_models(self):
        """서버 종료 시 모델 언로드"""
        if self.embedding_model is not None:
            print("🗑️ 임베딩 모델 언로드 중...")
            del self.embedding_model
            self.embedding_model = None
            print("✅ 임베딩 모델 언로드 완료!")
            
# 전역 모델 매니저 인스턴스
model_manager = ModelManager()

def get_embedding_model() -> SentenceTransformer:
    """
    FastAPI Dependency로 사용할 임베딩 모델 getter

    Usage:
        @router.post("/endpoint")
        def endpoint(model: SentenceTransformer = Depends(get_embedding_model)):
            embedding = model.encode("text")
    """
    if model_manager.embedding_model is None:
        raise RuntimeError("임베딩 모델이 로드되지 않았습니다.")
    return model_manager.embedding_model