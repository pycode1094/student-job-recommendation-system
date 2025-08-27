import pandas as pd
from sqlalchemy import create_engine, text
import re

def normalize_course_name(course_name):
    """과정명을 정규화하여 매칭하기 쉽게 만듦"""
    if pd.isna(course_name):
        return ""
    
    # 소문자로 변환
    normalized = str(course_name).lower()
    
    # 공백, 특수문자 제거
    normalized = re.sub(r'[^\w\s]', '', normalized)
    normalized = re.sub(r'\s+', '', normalized)
    
    # 아카데미/아카데미 관련 정규화
    normalized = normalized.replace('아카데미', 'academy')
    normalized = normalized.replace('academy', 'academy')
    
    return normalized

def get_student_ids():
    """RecoderBetaTest와 merged_trainee_data 테이블을 조인해서 학번 가져오기"""
    
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
        
        print("🔍 두 테이블의 데이터를 확인하고 학번을 매칭합니다...\n")
        
        # 1. RecoderBetaTest 테이블 데이터 확인
        print("📊 RecoderBetaTest 테이블 데이터:")
        beta_test_df = pd.read_sql("SELECT * FROM RecoderBetaTest", engine)
        print(f"총 {len(beta_test_df)}행")
        print("\n처음 5행:")
        print(beta_test_df[['이름을_입력해주세요', '과정명을_확인해주세요맞으면_선택']].head())
        
        # 2. merged_trainee_data 테이블 데이터 확인
        print("\n📊 merged_trainee_data 테이블 데이터:")
        trainee_df = pd.read_sql("SELECT * FROM merged_trainee_data", engine)
        print(f"총 {len(trainee_df)}행")
        print("\n처음 5행:")
        print(trainee_df[['이름', '과정명']].head())
        
        # 3. 과정명 정규화
        print("\n🔧 과정명 정규화를 시작합니다...")
        
        # 컬럼명 확인 및 매칭
        beta_name_col = '이름을_입력해주세요'
        beta_course_col = '과정명을_확인해주세요맞으면_선택'
        
        trainee_name_col = '이름'
        trainee_course_col = '과정명'
        trainee_id_col = '학번'
        
        # 과정명 정규화
        beta_test_df['normalized_course'] = beta_test_df[beta_course_col].apply(normalize_course_name)
        trainee_df['normalized_course'] = trainee_df[trainee_course_col].apply(normalize_course_name)
        
        print("\n📋 정규화된 과정명 비교:")
        print("Excel 과정명 (정규화):", beta_test_df['normalized_course'].iloc[0])
        print("DB 과정명 (정규화):", trainee_df['normalized_course'].iloc[0])
        
        # 4. 이름과 정규화된 과정명으로 매칭하여 학번 가져오기
        print("\n🔍 이름과 정규화된 과정명으로 학번 매칭을 시작합니다...")
        
        # 매칭 결과를 저장할 리스트
        matched_results = []
        
        for idx, beta_row in beta_test_df.iterrows():
            beta_name = beta_row[beta_name_col]
            beta_course = beta_row[beta_course_col]
            beta_normalized_course = beta_row['normalized_course']
            
            # 이름과 정규화된 과정명이 모두 일치하는 학생 찾기
            matches = trainee_df[
                (trainee_df[trainee_name_col] == beta_name) & 
                (trainee_df['normalized_course'] == beta_normalized_course)
            ]
            
            if len(matches) > 0:
                student_id = matches.iloc[0][trainee_id_col]
                matched_results.append({
                    'beta_id': beta_row['id'],
                    'beta_name': beta_name,
                    'beta_course': beta_course,
                    'student_id': student_id,
                    'status': '매칭 성공'
                })
                print(f"✅ 매칭 성공: {beta_name} ({beta_course}) → 학번: {student_id}")
            else:
                # 이름만 일치하는 경우
                name_matches = trainee_df[trainee_df[trainee_name_col] == beta_name]
                if len(name_matches) > 0:
                    print(f"⚠️ 이름만 일치: {beta_name} - 과정명 불일치")
                    print(f"   Excel 과정명: {beta_course}")
                    print(f"   Excel 정규화: {beta_normalized_course}")
                    print(f"   DB 과정명들: {name_matches[trainee_course_col].tolist()}")
                    print(f"   DB 정규화: {name_matches['normalized_course'].tolist()}")
                
                matched_results.append({
                    'beta_id': beta_row['id'],
                    'beta_name': beta_name,
                    'beta_course': beta_course,
                    'student_id': None,
                    'status': '매칭 실패'
                })
                print(f"❌ 매칭 실패: {beta_name} ({beta_course})")
        
        # 5. 매칭 결과를 DataFrame으로 변환
        results_df = pd.DataFrame(matched_results)
        
        print(f"\n📈 매칭 결과 요약:")
        print(f"총 응답: {len(results_df)}개")
        print(f"매칭 성공: {len(results_df[results_df['status'] == '매칭 성공'])}개")
        print(f"매칭 실패: {len(results_df[results_df['status'] == '매칭 실패'])}개")
        
        # 6. 매칭된 학번을 RecoderBetaTest 테이블에 업데이트
        print("\n📝 매칭된 학번을 RecoderBetaTest 테이블에 업데이트합니다...")
        
        # 학번 업데이트
        for _, row in results_df.iterrows():
            if row['student_id'] is not None:
                update_sql = f"""
                UPDATE RecoderBetaTest 
                SET student_id = '{row['student_id']}' 
                WHERE id = {row['beta_id']}
                """
                try:
                    with engine.connect() as connection:
                        connection.execute(text(update_sql))
                        connection.commit()
                except Exception as e:
                    print(f"⚠️ 학번 업데이트 중 오류: {e}")
        
        print("✅ 학번 업데이트가 완료되었습니다!")
        
        # 7. 최종 결과 확인
        print("\n📊 최종 결과 확인:")
        final_df = pd.read_sql("SELECT id, student_id, 이름을_입력해주세요, 과정명을_확인해주세요맞으면_선택 FROM RecoderBetaTest", engine)
        print(final_df)
        
        return results_df
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return None

if __name__ == "__main__":
    print("🚀 학생 학번 매칭을 시작합니다... (과정명 정규화 포함)")
    results = get_student_ids()
    
    if results is not None:
        print("\n🎉 학번 매칭이 완료되었습니다!")
    else:
        print("\n❌ 학번 매칭에 실패했습니다.")
