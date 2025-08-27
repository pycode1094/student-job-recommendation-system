import pandas as pd
from sqlalchemy import create_engine
import warnings
warnings.filterwarnings('ignore')

def export_recommendations():
    """enhanced_testresult 테이블의 데이터를 파일로 내보냅니다."""
    
    try:
        # 데이터베이스 연결
        engine = create_engine('mysql+pymysql://root:15861@127.0.0.1:3306/job_recoder?charset=utf8mb4')
        
        # enhanced_testresult 테이블에서 데이터 가져오기
        query = """
        SELECT 
            student_id,
            recommendation_rank,
            recommended_title,
            recommended_company,
            recommended_industry,
            recommended_location,
            recommended_job_type,
            recommended_job_id,
            semantic_similarity,
            course_industry_score,
            location_score,
            diversity_score,
            freshness_score,
            final_score
        FROM enhanced_testresult
        ORDER BY student_id, recommendation_rank
        """
        
        df = pd.read_sql(query, engine)
        
        if df.empty:
            print("❌ enhanced_testresult 테이블에 데이터가 없습니다.")
            return None
        
        print(f"✅ 총 {len(df)}개의 추천 결과를 가져왔습니다.")
        print(f"📊 학생 수: {df['student_id'].nunique()}명")
        print(f"🏢 회사 수: {df['recommended_company'].nunique()}개")
        
        # 데이터 전처리
        # NaN 값 처리
        df = df.fillna({
            'semantic_similarity': 0.0,
            'course_industry_score': 0.0,
            'location_score': 0.0,
            'diversity_score': 0.0,
            'freshness_score': 0.0,
            'final_score': 0.0
        })
        
        # 점수 컬럼을 소수점 4자리로 반올림
        score_columns = ['semantic_similarity', 'course_industry_score', 'location_score', 
                        'diversity_score', 'freshness_score', 'final_score']
        for col in score_columns:
            if col in df.columns:
                df[col] = df[col].round(4)
        
        # CSV 파일로 저장
        csv_filename = 'student_recommendations.csv'
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        print(f"💾 CSV 파일 저장 완료: {csv_filename}")
        
        # Excel 파일로 저장
        excel_filename = 'student_recommendations.xlsx'
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='추천결과', index=False)
            
            # 통계 시트 추가
            stats_data = {
                '통계 항목': [
                    '총 추천 결과 수',
                    '학생 수',
                    '회사 수',
                    '산업 분야 수',
                    '지역 수',
                    '평균 최종 점수',
                    '최고 최종 점수',
                    '최저 최종 점수'
                ],
                '값': [
                    len(df),
                    df['student_id'].nunique(),
                    df['recommended_company'].nunique(),
                    df['recommended_industry'].nunique(),
                    df['recommended_location'].nunique(),
                    f"{df['final_score'].mean():.4f}",
                    f"{df['final_score'].max():.4f}",
                    f"{df['final_score'].min():.4f}"
                ]
            }
            
            stats_df = pd.DataFrame(stats_data)
            stats_df.to_excel(writer, sheet_name='통계', index=False)
            
            # 학생별 요약 시트 추가
            student_summary = df.groupby('student_id').agg({
                'recommendation_rank': 'count',
                'final_score': ['mean', 'max', 'min'],
                'recommended_company': 'nunique',
                'recommended_industry': 'nunique',
                'recommended_location': 'nunique'
            }).round(4)
            
            student_summary.columns = ['추천수', '평균점수', '최고점수', '최저점수', '회사수', '산업수', '지역수']
            student_summary.to_excel(writer, sheet_name='학생별요약')
        
        print(f"💾 Excel 파일 저장 완료: {excel_filename}")
        
        # 샘플 데이터 확인
        print("\n📋 샘플 데이터 (처음 5개):")
        print(df.head().to_string())
        
        return df
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return None

if __name__ == "__main__":
    print("🚀 추천 결과 내보내기 시작...")
    result = export_recommendations()
    
    if result is not None:
        print("\n✅ 모든 작업이 완료되었습니다!")
        print("📁 생성된 파일:")
        print("   - student_recommendations.csv")
        print("   - student_recommendations.xlsx")
    else:
        print("\n❌ 작업 실패")
