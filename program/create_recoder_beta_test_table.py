import pandas as pd
from sqlalchemy import create_engine, text
import mysql.connector
from mysql.connector import Error

def create_recoder_beta_test_table():
    """RecoderBetaTest 테이블을 생성하는 함수"""
    
    # DB 연결 정보
    user = 'root'             
    password = '15861'      
    host = '127.0.0.1'           
    port = 3306
    db_name = 'job_recoder'
    
    connection = None
    try:
        # MySQL 연결
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
            charset='utf8mb4'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # RecoderBetaTest 테이블 생성 SQL
            create_table_query = """
            CREATE TABLE IF NOT EXISTS RecoderBetaTest (
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
            COMMENT='학생 서베이 응답 데이터 테이블';
            """
            
            cursor.execute(create_table_query)
            connection.commit()
            
            print("✅ RecoderBetaTest 테이블이 성공적으로 생성되었습니다!")
            
            # 테이블 구조 확인
            cursor.execute("DESCRIBE RecoderBetaTest")
            columns = cursor.fetchall()
            
            print("\n📋 테이블 구조:")
            print("-" * 80)
            for column in columns:
                print(f"{column[0]:<20} {column[1]:<15} {column[2]:<10} {column[3]:<10} {column[4]}")
            
    except Error as e:
        print(f"❌ MySQL 연결 오류: {e}")
        print("🔍 MariaDB 서비스가 실행 중인지 확인해주세요.")
        return False
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        return False
    
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n🔌 데이터베이스 연결이 종료되었습니다.")
    
    return True

def insert_sample_survey_data():
    """샘플 서베이 데이터를 삽입하는 함수"""
    
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
        
        # 샘플 서베이 데이터
        sample_data = [
            {
                'student_id': '2024001',
                'student_name': '김철수',
                'survey_date': '2024-01-15',
                'satisfaction_score': 4,
                'feature_rating': 4,
                'ui_rating': 5,
                'recommendation_likelihood': 4,
                'favorite_features': '직업 추천 알고리즘, 맞춤형 필터링',
                'improvement_suggestions': '더 많은 직업 정보 추가',
                'additional_comments': '전반적으로 만족스러운 서비스입니다.'
            },
            {
                'student_id': '2024002',
                'student_name': '이영희',
                'survey_date': '2024-01-15',
                'satisfaction_score': 5,
                'feature_rating': 5,
                'ui_rating': 4,
                'recommendation_likelihood': 5,
                'favorite_features': '사용자 친화적 인터페이스, 빠른 검색',
                'improvement_suggestions': '모바일 앱 버전 개발',
                'additional_comments': '친구들에게 추천하고 싶습니다!'
            },
            {
                'student_id': '2024003',
                'student_name': '박민수',
                'survey_date': '2024-01-15',
                'satisfaction_score': 3,
                'feature_rating': 4,
                'ui_rating': 3,
                'recommendation_likelihood': 3,
                'favorite_features': '데이터 시각화',
                'improvement_suggestions': '더 직관적인 네비게이션',
                'additional_comments': '좋은 아이디어지만 개선 여지가 있습니다.'
            }
        ]
        
        # DataFrame 생성
        df = pd.DataFrame(sample_data)
        
        # 데이터베이스에 삽입
        df.to_sql(name='RecoderBetaTest', con=engine, if_exists='append', index=False)
        
        print("✅ 샘플 서베이 데이터가 성공적으로 삽입되었습니다!")
        print(f"📊 총 {len(sample_data)}개의 응답이 추가되었습니다.")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    print("🚀 RecoderBetaTest 테이블 생성 및 샘플 데이터 삽입을 시작합니다...\n")
    
    # 1. 테이블 생성
    if create_recoder_beta_test_table():
        print("\n" + "="*80 + "\n")
        
        # 2. 샘플 데이터 삽입
        insert_sample_survey_data()
        
        print("\n🎉 모든 작업이 완료되었습니다!")
    else:
        print("\n❌ 테이블 생성에 실패했습니다. DB 연결을 확인해주세요.")
