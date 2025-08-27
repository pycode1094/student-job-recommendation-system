import pandas as pd
from sqlalchemy import create_engine, text

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
        
        # 3. 이름과 과정명으로 매칭하여 학번 가져오기
        print("\n🔍 이름과 과정명으로 학번 매칭을 시작합니다...")
        
        # 컬럼명 확인 및 매칭
        beta_name_col = '이름을_입력해주세요'
        beta_course_col = '과정명을_확인해주세요맞으면_선택'
        
        trainee_name_col = '이름'
        trainee_course_col = '과정명'
        trainee_id_col = '학번'
        
        # 매칭 결과를 저장할 리스트
        matched_results = []
        
        for idx, beta_row in beta_test_df.iterrows():
            beta_name = beta_row[beta_name_col]
            beta_course = beta_row[beta_course_col]
            
            # 이름과 과정명이 모두 일치하는 학생 찾기
            matches = trainee_df[
                (trainee_df[trainee_name_col] == beta_name) & 
                (trainee_df[trainee_course_col] == beta_course)
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
                    print(f"   DB 과정명들: {name_matches[trainee_course_col].tolist()}")
                
                matched_results.append({
                    'beta_id': beta_row['id'],
                    'beta_name': beta_name,
                    'beta_course': beta_course,
                    'student_id': None,
                    'status': '매칭 실패'
                })
                print(f"❌ 매칭 실패: {beta_name} ({beta_course})")
        
        # 4. 매칭 결과를 DataFrame으로 변환
        results_df = pd.DataFrame(matched_results)
        
        print(f"\n📈 매칭 결과 요약:")
        print(f"총 응답: {len(results_df)}개")
        print(f"매칭 성공: {len(results_df[results_df['status'] == '매칭 성공'])}개")
        print(f"매칭 실패: {len(results_df[results_df['status'] == '매칭 실패'])}개")
        
        # 5. 매칭된 학번을 RecoderBetaTest 테이블에 추가
        print("\n📝 매칭된 학번을 RecoderBetaTest 테이블에 추가합니다...")
        
        # student_id 컬럼이 없으면 추가
        try:
            with engine.connect() as connection:
                # student_id 컬럼 존재 여부 확인
                result = connection.execute(text("SHOW COLUMNS FROM RecoderBetaTest LIKE 'student_id'"))
                if not result.fetchone():
                    connection.execute(text("ALTER TABLE RecoderBetaTest ADD COLUMN student_id VARCHAR(20) AFTER id"))
                    connection.commit()
                    print("✅ student_id 컬럼을 추가했습니다.")
                else:
                    print("ℹ️ student_id 컬럼이 이미 존재합니다.")
        except Exception as e:
            print(f"⚠️ 컬럼 추가 중 오류: {e}")
        
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
        
        # 6. 최종 결과 확인
        print("\n📊 최종 결과 확인:")
        final_df = pd.read_sql("SELECT id, student_id, 이름을_입력해주세요, 과정명을_확인해주세요맞으면_선택 FROM RecoderBetaTest", engine)
        print(final_df)
        
        return results_df
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return None

if __name__ == "__main__":
    print("🚀 학생 학번 매칭을 시작합니다...")
    results = get_student_ids()
    
    if results is not None:
        print("\n🎉 학번 매칭이 완료되었습니다!")
    else:
        print("\n❌ 학번 매칭에 실패했습니다.")
