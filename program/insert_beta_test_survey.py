import pandas as pd
from sqlalchemy import create_engine
import os

def insert_beta_test_survey_data():
    """리코더 베타테스트(응답).xlsx 파일을 읽어서 RecoderBetaTest 테이블에 삽입"""
    
    # DB 연결 정보
    user = 'root'             
    password = '15861'      
    host = '127.0.0.1'           
    port = 3306
    db_name = 'job_recoder'
    
    # Excel 파일 경로
    excel_file_path = './data/리코더 베타테스트(응답).xlsx'
    
    try:
        # Excel 파일 존재 확인
        if not os.path.exists(excel_file_path):
            print(f"❌ 파일을 찾을 수 없습니다: {excel_file_path}")
            return
        
        # Excel 파일 읽기
        print(f"📖 Excel 파일을 읽는 중: {excel_file_path}")
        df = pd.read_excel(excel_file_path)
        
        print(f"📊 읽어온 데이터: {len(df)}행, {len(df.columns)}열")
        print("\n📋 컬럼 목록:")
        for i, col in enumerate(df.columns):
            print(f"  {i+1}. {col}")
        
        # 데이터 미리보기
        print("\n👀 데이터 미리보기 (처음 3행):")
        print(df.head(3))
        
        # 컬럼 매핑 (Excel 컬럼명을 테이블 컬럼명에 맞게)
        print("\n🔍 컬럼 매핑을 시작합니다...")
        
        # 사용자 입력으로 컬럼 매핑
        column_mapping = {}
        required_columns = [
            'student_id', 'student_name', 'survey_date', 'satisfaction_score',
            'feature_rating', 'ui_rating', 'recommendation_likelihood',
            'favorite_features', 'improvement_suggestions', 'additional_comments'
        ]
        
        print("\n📝 컬럼 매핑:")
        for required_col in required_columns:
            print(f"\n'{required_col}'에 매핑할 Excel 컬럼을 선택하세요:")
            for i, col in enumerate(df.columns):
                print(f"  {i+1}. {col}")
            
            while True:
                try:
                    choice = input(f"선택 (1-{len(df.columns)}): ").strip()
                    if choice.isdigit() and 1 <= int(choice) <= len(df.columns):
                        column_mapping[required_col] = df.columns[int(choice)-1]
                        break
                    else:
                        print("올바른 번호를 입력해주세요.")
                except ValueError:
                    print("올바른 번호를 입력해주세요.")
        
        # 데이터 변환
        transformed_data = {}
        for required_col, excel_col in column_mapping.items():
            transformed_data[required_col] = df[excel_col]
        
        # DataFrame 생성
        transformed_df = pd.DataFrame(transformed_data)
        
        # 데이터 타입 변환
        if 'survey_date' in transformed_df.columns:
            transformed_df['survey_date'] = pd.to_datetime(transformed_df['survey_date'], errors='coerce').dt.date
        
        # 숫자 컬럼 변환
        numeric_columns = ['satisfaction_score', 'feature_rating', 'ui_rating', 'recommendation_likelihood']
        for col in numeric_columns:
            if col in transformed_df.columns:
                transformed_df[col] = pd.to_numeric(transformed_df[col], errors='coerce')
        
        print("\n✅ 변환된 데이터:")
        print(transformed_df.head())
        
        # 데이터베이스에 삽입
        engine = create_engine(
            f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}",
            connect_args={"charset": "utf8mb4"} 
        )
        
        # 기존 데이터 확인
        existing_count = pd.read_sql("SELECT COUNT(*) as count FROM RecoderBetaTest", engine).iloc[0]['count']
        print(f"\n📊 기존 데이터 수: {existing_count}개")
        
        # 새 데이터 삽입
        transformed_df.to_sql(name='RecoderBetaTest', con=engine, if_exists='append', index=False)
        
        # 삽입 후 데이터 수 확인
        new_count = pd.read_sql("SELECT COUNT(*) as count FROM RecoderBetaTest", engine).iloc[0]['count']
        inserted_count = new_count - existing_count
        
        print(f"✅ 서베이 데이터가 성공적으로 삽입되었습니다!")
        print(f"📊 새로 추가된 데이터: {inserted_count}개")
        print(f"📊 총 데이터 수: {new_count}개")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

def show_table_data():
    """RecoderBetaTest 테이블의 현재 데이터를 보여주는 함수"""
    
    # DB 연결 정보
    user = 'root'             
    password = '15861'      
    host = '127.0.0.1'           
    port = 3306
    db_name = 'job_recoder'
    
    try:
        engine = create_engine(
            f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}",
            connect_args={"charset": "utf8mb4"} 
        )
        
        # 테이블 데이터 조회
        df = pd.read_sql("SELECT * FROM RecoderBetaTest ORDER BY created_at DESC", engine)
        
        print(f"\n📊 RecoderBetaTest 테이블 현재 데이터 ({len(df)}개):")
        print("=" * 100)
        print(df.to_string(index=False))
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    print("🚀 리코더 베타테스트 서베이 데이터 삽입 도구")
    print("=" * 50)
    
    while True:
        print("\n📋 메뉴:")
        print("1. Excel 파일에서 서베이 데이터 삽입")
        print("2. 현재 테이블 데이터 확인")
        print("3. 종료")
        
        choice = input("\n선택하세요 (1-3): ").strip()
        
        if choice == '1':
            insert_beta_test_survey_data()
        elif choice == '2':
            show_table_data()
        elif choice == '3':
            print("👋 프로그램을 종료합니다.")
            break
        else:
            print("❌ 올바른 선택을 해주세요.")
