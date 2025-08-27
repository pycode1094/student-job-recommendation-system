import pandas as pd
from sqlalchemy import create_engine
import os

def insert_excel_to_db():
    """리코더 베타테스트(응답).xlsx 파일을 바로 DB에 삽입"""
    
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
        
        # 자동 컬럼 매핑 (Excel 파일 구조에 맞게)
        print("\n🔍 자동 컬럼 매핑을 시작합니다...")
        
        # 데이터 변환
        transformed_data = {}
        
        # 1. 타임스탬프를 survey_date로
        transformed_data['survey_date'] = pd.to_datetime(df.iloc[:, 0], errors='coerce').dt.date
        
        # 2. 이름을 student_name으로 (2번째 컬럼)
        transformed_data['student_name'] = df.iloc[:, 1]
        
        # 3. student_id (타임스탬프에서 추출)
        transformed_data['student_id'] = pd.to_datetime(df.iloc[:, 0], errors='coerce').dt.strftime('%Y%m%d%H%M%S')
        
        # 4. 기본값 설정
        transformed_data['satisfaction_score'] = 4
        transformed_data['feature_rating'] = 4
        transformed_data['ui_rating'] = 4
        transformed_data['recommendation_likelihood'] = 4
        
        # 5. 과정명을 favorite_features로 (3번째 컬럼)
        transformed_data['favorite_features'] = df.iloc[:, 2]
        
        # 6. 희망 분야를 improvement_suggestions로 (4번째 컬럼)
        transformed_data['improvement_suggestions'] = df.iloc[:, 3]
        
        # 7. 특기/장점을 additional_comments로 (마지막 컬럼)
        transformed_data['additional_comments'] = df.iloc[:, -1]
        
        # DataFrame 생성
        transformed_df = pd.DataFrame(transformed_data)
        
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

if __name__ == "__main__":
    print("🚀 Excel 파일을 바로 DB에 삽입합니다...")
    insert_excel_to_db()
    print("\n🎉 완료!")
