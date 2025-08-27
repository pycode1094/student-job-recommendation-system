import pandas as pd
from sqlalchemy import create_engine

def check_student_data():
    try:
        # DB 연결
        engine = create_engine(
            'mysql+pymysql://root:15861@127.0.0.1:3306/job_recoder?charset=utf8mb4'
        )
        
        # 훈련생 데이터에서 학번 정보 가져오기
        query = "SELECT 학번, 이름 FROM merged_trainee_data LIMIT 10"
        df = pd.read_sql(query, engine)
        
        print("✅ DB 연결 성공!")
        print(f"총 학생 수: {len(df)}")
        print("\n📋 학번 목록 (상위 10개):")
        print(df)
        
        # 학번 데이터 타입 확인
        print(f"\n📊 학번 데이터 타입: {df['학번'].dtype}")
        print(f"📊 이름 데이터 타입: {df['이름'].dtype}")
        
        # 샘플 학번들
        sample_ids = df['학번'].head(5).tolist()
        print(f"\n🎯 테스트용 학번들: {sample_ids}")
        
        return df
        
    except Exception as e:
        print(f"❌ DB 연결 오류: {e}")
        return None

if __name__ == "__main__":
    check_student_data()





