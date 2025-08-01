import pandas as pd
from sqlalchemy import create_engine

# 데이터베이스 연결
engine = create_engine(
    'mysql+pymysql://root:15861@127.0.0.1:3306/job_recoder?charset=utf8mb4'
)

# 향상된 추천 결과 확인
recommendation_query = """
SELECT 
    trainee_id,
    trainee_name,
    rank,
    job_title,
    company_name,
    industry,
    location,
    salary,
    job_type,
    experience,
    education,
    similarity_score
FROM enhanced_job_recommendations 
ORDER BY trainee_name, rank
LIMIT 30
"""

recommendations_df = pd.read_sql(recommendation_query, engine)

print("=== 향상된 SBERT 기반 채용 추천 결과 ===")
print(f"총 추천 개수: {len(recommendations_df)}")
print(f"훈련생 수: {recommendations_df['trainee_name'].nunique()}명")
print(f"평균 유사도 점수: {recommendations_df['similarity_score'].mean():.4f}")
print(f"최고 유사도 점수: {recommendations_df['similarity_score'].max():.4f}")

print("\n=== 향상된 추천 결과 샘플 ===")
print(recommendations_df)

# 특정 훈련생의 향상된 추천 결과 확인
print("\n=== 특정 훈련생 향상된 추천 결과 ===")
sample_trainee = recommendations_df['trainee_name'].iloc[0]
trainee_recommendations = recommendations_df[recommendations_df['trainee_name'] == sample_trainee]

print(f"\n👤 {sample_trainee}님의 향상된 추천 채용:")
for _, row in trainee_recommendations.iterrows():
    print(f"{row['rank']}. {row['job_title']} - {row['company_name']}")
    print(f"   산업: {row['industry']}, 지역: {row['location']}")
    print(f"   고용형태: {row['job_type']}, 경력: {row['experience']}")
    print(f"   급여: {row['salary']}, 유사도: {row['similarity_score']:.4f}")
    print()

# 산업별 추천 분포 확인
print("\n=== 산업별 추천 분포 ===")
industry_counts = recommendations_df['industry'].value_counts().head(10)
print(industry_counts)

# 유사도 점수 분포 확인
print("\n=== 유사도 점수 분포 ===")
print(f"0.9 이상: {len(recommendations_df[recommendations_df['similarity_score'] >= 0.9])}개")
print(f"0.8-0.9: {len(recommendations_df[(recommendations_df['similarity_score'] >= 0.8) & (recommendations_df['similarity_score'] < 0.9)])}개")
print(f"0.7-0.8: {len(recommendations_df[(recommendations_df['similarity_score'] >= 0.7) & (recommendations_df['similarity_score'] < 0.8)])}개")
print(f"0.7 미만: {len(recommendations_df[recommendations_df['similarity_score'] < 0.7])}개") 