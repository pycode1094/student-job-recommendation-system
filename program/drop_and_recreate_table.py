import pandas as pd
from sqlalchemy import create_engine, text

def drop_and_recreate_table():
    """기존 RecoderBetaTest 테이블을 삭제하고 새로 생성"""
    
    # DB 연결 정보
    user = 'root'             
    password = '15861'      
    host = '127.0.0.1'           
    port = 3306
    db_name = 'job_recoder'
    
    try:
        # SQLAlchemy 엔진 생성
        engine = create_engine(
            f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}",
            connect_args={"charset": "utf8mb4"} 
        )
        
        with engine.connect() as connection:
            print("✅ 데이터베이스 연결 성공!")
            
            # 기존 테이블 삭제
            print("🗑️ 기존 RecoderBetaTest 테이블을 삭제합니다...")
            connection.execute(text("DROP TABLE IF EXISTS RecoderBetaTest"))
            connection.commit()
            print("✅ 기존 테이블 삭제 완료!")
            
            # 새 테이블 생성
            print("🔧 새로운 RecoderBetaTest 테이블을 생성합니다...")
            create_table_sql = """
            CREATE TABLE RecoderBetaTest (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id VARCHAR(20) COMMENT '학번',
                student_name VARCHAR(50) COMMENT '학생이름',
                survey_date DATE COMMENT '서베이 응답일',
                satisfaction_score INT COMMENT '만족도 점수 (1-5)',
                feature_rating INT COMMENT '기능 평가 (1-5)',
                ui_rating INT COMMENT 'UI/UX 평가 (1-5)',
                recommendation_likelihood INT COMMENT '추천 가능성 (1-5)',
                favorite_features TEXT COMMENT '좋아하는 기능들',
                improvement_suggestions TEXT COMMENT '개선 제안사항',
                additional_comments TEXT COMMENT '추가 의견',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            COMMENT='학생 서베이 응답 데이터 테이블'
            """
            
            connection.execute(text(create_table_sql))
            connection.commit()
            print("✅ 새 테이블 생성 완료!")
            
            # 테이블 구조 확인
            result = connection.execute(text("DESCRIBE RecoderBetaTest"))
            columns = result.fetchall()
            
            print("\n📋 새로 생성된 테이블 구조:")
            print("-" * 80)
            for column in columns:
                print(f"{column[0]:<20} {column[1]:<15} {column[2]:<10} {column[3]:<10} {column[4]}")
            
            return True
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

if __name__ == "__main__":
    print("🚀 RecoderBetaTest 테이블 재생성을 시작합니다...\n")
    
    if drop_and_recreate_table():
        print("\n🎉 테이블 재생성이 완료되었습니다!")
        print("이제 Excel 데이터를 삽입할 수 있습니다.")
    else:
        print("\n❌ 테이블 재생성에 실패했습니다.")
