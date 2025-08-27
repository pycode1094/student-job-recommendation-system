import pandas as pd
from sqlalchemy import create_engine, text
import os

def insert_real_excel_data():
    """Excel 파일의 실제 데이터를 그대로 DB에 삽입"""
    
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
        print("\n📋 실제 Excel 컬럼 목록:")
        for i, col in enumerate(df.columns):
            print(f"  {i+1}. {col}")
        
        # 데이터 미리보기
        print("\n👀 데이터 미리보기 (처음 3행):")
        print(df.head(3))
        
        # 기존 테이블 삭제하고 Excel 구조에 맞는 새 테이블 생성
        print("\n🔧 Excel 구조에 맞는 새 테이블을 생성합니다...")
        
        engine = create_engine(
            f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}",
            connect_args={"charset": "utf8mb4"} 
        )
        
        with engine.connect() as connection:
            # 기존 테이블 삭제
            connection.execute(text("DROP TABLE IF EXISTS RecoderBetaTest"))
            connection.commit()
            
            # Excel 컬럼에 맞는 테이블 생성
            columns_sql = []
            for col in df.columns:
                # 컬럼명 정리 (특수문자 제거)
                clean_col = col.replace(' ', '_').replace('.', '').replace('(', '').replace(')', '').replace('\n', '').replace('ex)', '').replace('등', '')
                clean_col = clean_col[:50]  # 컬럼명 길이 제한
                
                # 데이터 타입 결정
                if '타임스탬프' in col or '날짜' in col or '일' in col:
                    columns_sql.append(f"`{clean_col}` DATETIME")
                elif '연봉' in col or '만원' in col or '점수' in col:
                    columns_sql.append(f"`{clean_col}` VARCHAR(100)")
                else:
                    columns_sql.append(f"`{clean_col}` TEXT")
            
            create_table_sql = f"""
            CREATE TABLE RecoderBetaTest (
                id INT AUTO_INCREMENT PRIMARY KEY,
                {', '.join(columns_sql)},
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            COMMENT='Excel 데이터 그대로 저장'
            """
            
            connection.execute(text(create_table_sql))
            connection.commit()
            print("✅ Excel 구조에 맞는 새 테이블 생성 완료!")
            
            # 테이블 구조 확인
            result = connection.execute(text("DESCRIBE RecoderBetaTest"))
            columns = result.fetchall()
            
            print("\n📋 새로 생성된 테이블 구조:")
            print("-" * 80)
            for column in columns:
                print(f"{column[0]:<30} {column[1]:<15} {column[2]:<10} {column[3]:<10} {column[4]}")
        
        # Excel 데이터를 그대로 삽입
        print("\n📥 Excel 데이터를 DB에 삽입합니다...")
        
        # 컬럼명 정리
        clean_columns = []
        for col in df.columns:
            clean_col = col.replace(' ', '_').replace('.', '').replace('(', '').replace(')', '').replace('\n', '').replace('ex)', '').replace('등', '')
            clean_col = clean_col[:50]
            clean_columns.append(clean_col)
        
        # DataFrame 컬럼명 변경
        df_clean = df.copy()
        df_clean.columns = clean_columns
        
        # 데이터베이스에 삽입
        df_clean.to_sql(name='RecoderBetaTest', con=engine, if_exists='append', index=False)
        
        print(f"✅ Excel 데이터가 성공적으로 삽입되었습니다!")
        print(f"📊 삽입된 데이터: {len(df)}행")
        
        # 삽입된 데이터 확인
        result_df = pd.read_sql("SELECT * FROM RecoderBetaTest", engine)
        print(f"📊 DB에 저장된 데이터: {len(result_df)}행")
        
        print("\n👀 삽입된 데이터 미리보기:")
        print(result_df.head())
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    print("🚀 Excel 파일의 실제 데이터를 그대로 DB에 삽입합니다...")
    insert_real_excel_data()
    print("\n🎉 완료!")
