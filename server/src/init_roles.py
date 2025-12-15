"""
역할(Role) 초기 데이터 생성 스크립트
"""
from src.database import SessionLocal
from src.models import Role
from sqlalchemy.exc import IntegrityError

def init_roles():
    """기본 역할 데이터 추가"""
    db = SessionLocal()
    try:
        # 기존 역할이 있는지 확인
        existing_roles = db.query(Role).all()
        if existing_roles:
            print(f"역할이 이미 존재합니다: {[r.Name for r in existing_roles]}")
            return

        # 기본 역할 생성
        roles = [
            Role(Name="user"),
            Role(Name="admin")
        ]
        
        for role in roles:
            db.add(role)
        
        db.commit()
        print("역할 생성 완료:")
        for role in roles:
            print(f"  - {role.Name} (ID: {role.RoleID})")
    
    except IntegrityError as e:
        db.rollback()
        print(f"무결성 오류: {e}")
    except Exception as e:
        db.rollback()
        print(f"오류 발생: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_roles()
