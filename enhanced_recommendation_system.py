import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore')

class EnhancedJobRecommendationSystem:
    def __init__(self):
        """초기화"""
        self.engine = create_engine(
            'mysql+pymysql://root:15861@127.0.0.1:3306/job_recoder?charset=utf8mb4'
        )
        # 한국어 SBERT 모델 로드
        self.model = SentenceTransformer('sentence-transformers/xlm-r-100langs-bert-base-nli-stsb-mean-tokens')
        
    def load_data(self):
        """데이터 로드"""
        print("📊 향상된 데이터 로딩 중...")
        
        # 훈련생 데이터 로드
        trainee_query = "SELECT * FROM merged_trainee_data"
        self.trainee_df = pd.read_sql(trainee_query, self.engine)
        print(f"✅ 훈련생 데이터: {len(self.trainee_df)}명")
        
        # 향상된 채용 데이터 로드
        job_query = "SELECT * FROM enhanced_job_postings WHERE active = 1"
        self.job_df = pd.read_sql(job_query, self.engine)
        print(f"✅ 향상된 채용 데이터: {len(self.job_df)}개")
        
        # 데이터 구조 확인
        print(f"\n📋 훈련생 데이터 컬럼: {list(self.trainee_df.columns)}")
        print(f"📋 향상된 채용 데이터 컬럼: {list(self.job_df.columns)}")
        
    def create_enhanced_trainee_profile(self, trainee_row):
        """향상된 훈련생 프로필 텍스트 생성"""
        profile_parts = []
        
        # 기본 정보
        if pd.notna(trainee_row.get('이름')):
            profile_parts.append(f"이름: {trainee_row['이름']}")
        
        if pd.notna(trainee_row.get('학번')):
            profile_parts.append(f"학번: {trainee_row['학번']}")
        
        # 훈련 과정 정보
        if pd.notna(trainee_row.get('과정명')):
            profile_parts.append(f"훈련과정: {trainee_row['과정명']}")
        
        if pd.notna(trainee_row.get('훈련구분')):
            profile_parts.append(f"훈련구분: {trainee_row['훈련구분']}")
            
        # 희망 정보 (가장 중요한 매칭 요소)
        if pd.notna(trainee_row.get('희망직종')):
            profile_parts.append(f"희망직종: {trainee_row['희망직종']}")
            
        if pd.notna(trainee_row.get('희망업종')):
            profile_parts.append(f"희망업종: {trainee_row['희망업종']}")
            
        if pd.notna(trainee_row.get('희망지역')):
            profile_parts.append(f"희망지역: {trainee_row['희망지역']}")
            
        if pd.notna(trainee_row.get('희망보수')):
            profile_parts.append(f"희망보수: {trainee_row['희망보수']}")
            
        # 장래계획
        if pd.notna(trainee_row.get('장래계획')):
            profile_parts.append(f"장래계획: {trainee_row['장래계획']}")
        
        return " ".join(profile_parts)
    
    def create_enhanced_job_profile(self, job_row):
        """향상된 채용 정보 프로필 텍스트 생성"""
        profile_parts = []
        
        # 회사 정보
        if pd.notna(job_row.get('company_name')):
            profile_parts.append(f"회사: {job_row['company_name']}")
            
        if pd.notna(job_row.get('company_type')):
            profile_parts.append(f"회사유형: {job_row['company_type']}")
            
        if pd.notna(job_row.get('company_size')):
            profile_parts.append(f"회사규모: {job_row['company_size']}")
            
        # 직무 정보 (가장 중요한 매칭 요소)
        if pd.notna(job_row.get('title')):
            profile_parts.append(f"직무: {job_row['title']}")
            
        if pd.notna(job_row.get('industry')):
            profile_parts.append(f"산업: {job_row['industry']}")
            
        if pd.notna(job_row.get('industry_code')):
            profile_parts.append(f"산업코드: {job_row['industry_code']}")
            
        if pd.notna(job_row.get('job_type')):
            profile_parts.append(f"고용형태: {job_row['job_type']}")
            
        # 지역
        if pd.notna(job_row.get('location')):
            profile_parts.append(f"근무지: {job_row['location']}")
            
        # 요구사항
        if pd.notna(job_row.get('experience')):
            profile_parts.append(f"요구경력: {job_row['experience']}")
            
        if pd.notna(job_row.get('education')):
            profile_parts.append(f"요구학력: {job_row['education']}")
            
        if pd.notna(job_row.get('salary')):
            profile_parts.append(f"급여: {job_row['salary']}")
            
        # 키워드 코드 (추가 매칭 요소)
        if pd.notna(job_row.get('keyword_code')):
            profile_parts.append(f"키워드: {job_row['keyword_code']}")
        
        return " ".join(profile_parts)
    
    def calculate_enhanced_similarity(self, trainee_profiles, job_profiles):
        """향상된 SBERT를 사용한 유사도 계산"""
        print("🔍 향상된 유사도 계산 중...")
        
        # 임베딩 생성
        trainee_embeddings = self.model.encode(trainee_profiles, show_progress_bar=True)
        job_embeddings = self.model.encode(job_profiles, show_progress_bar=True)
        
        # 코사인 유사도 계산
        similarity_matrix = cosine_similarity(trainee_embeddings, job_embeddings)
        
        return similarity_matrix
    
    def get_enhanced_recommendations(self, trainee_id=None, top_k=5):
        """향상된 추천 결과 생성"""
        print("🎯 향상된 추천 시스템 시작...")
        
        # 훈련생 프로필 생성
        trainee_profiles = []
        for _, row in self.trainee_df.iterrows():
            profile = self.create_enhanced_trainee_profile(row)
            trainee_profiles.append(profile)
        
        # 채용 프로필 생성
        job_profiles = []
        for _, row in self.job_df.iterrows():
            profile = self.create_enhanced_job_profile(row)
            job_profiles.append(profile)
        
        # 유사도 계산
        similarity_matrix = self.calculate_enhanced_similarity(trainee_profiles, job_profiles)
        
        # 추천 결과 생성
        recommendations = []
        
        if trainee_id is not None:
            # 특정 훈련생에 대한 추천
            trainee_idx = self.trainee_df[self.trainee_df['학번'] == trainee_id].index[0]
            similarities = similarity_matrix[trainee_idx]
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            trainee_info = self.trainee_df.iloc[trainee_idx]
            print(f"\n👤 {trainee_info.get('이름', 'Unknown')}님의 향상된 추천 채용")
            
            for i, job_idx in enumerate(top_indices):
                job_info = self.job_df.iloc[job_idx]
                similarity_score = similarities[job_idx]
                
                recommendation = {
                    'rank': i + 1,
                    'trainee_name': trainee_info.get('이름', 'Unknown'),
                    'job_title': job_info.get('title', 'Unknown'),
                    'company_name': job_info.get('company_name', 'Unknown'),
                    'industry': job_info.get('industry', 'Unknown'),
                    'location': job_info.get('location', 'Unknown'),
                    'salary': job_info.get('salary', 'Unknown'),
                    'job_type': job_info.get('job_type', 'Unknown'),
                    'experience': job_info.get('experience', 'Unknown'),
                    'education': job_info.get('education', 'Unknown'),
                    'similarity_score': round(similarity_score, 4),
                    'job_url': job_info.get('url', '')
                }
                recommendations.append(recommendation)
                
                print(f"{i+1}. {job_info.get('title', 'Unknown')} - {job_info.get('company_name', 'Unknown')}")
                print(f"   산업: {job_info.get('industry', 'Unknown')}, 지역: {job_info.get('location', 'Unknown')}")
                print(f"   유사도: {similarity_score:.4f}")
        else:
            # 모든 훈련생에 대한 추천
            for trainee_idx, trainee_row in self.trainee_df.iterrows():
                similarities = similarity_matrix[trainee_idx]
                top_indices = np.argsort(similarities)[::-1][:top_k]
                
                trainee_recommendations = []
                for i, job_idx in enumerate(top_indices):
                    job_info = self.job_df.iloc[job_idx]
                    similarity_score = similarities[job_idx]
                    
                    recommendation = {
                        'trainee_id': trainee_row.get('학번'),
                        'trainee_name': trainee_row.get('이름', 'Unknown'),
                        'rank': i + 1,
                        'job_id': job_info.get('job_id'),
                        'job_title': job_info.get('title', 'Unknown'),
                        'company_name': job_info.get('company_name', 'Unknown'),
                        'industry': job_info.get('industry', 'Unknown'),
                        'location': job_info.get('location', 'Unknown'),
                        'salary': job_info.get('salary', 'Unknown'),
                        'job_type': job_info.get('job_type', 'Unknown'),
                        'experience': job_info.get('experience', 'Unknown'),
                        'education': job_info.get('education', 'Unknown'),
                        'similarity_score': round(similarity_score, 4),
                        'job_url': job_info.get('url', '')
                    }
                    trainee_recommendations.append(recommendation)
                
                recommendations.extend(trainee_recommendations)
        
        return recommendations
    
    def save_enhanced_recommendations_to_db(self, recommendations):
        """향상된 추천 결과를 데이터베이스에 저장"""
        try:
            import pymysql
            connection = pymysql.connect(
                host='127.0.0.1',
                user='root',
                password='15861',
                port=3306,
                database='job_recoder',
                charset='utf8mb4'
            )
            
            cursor = connection.cursor()
            
            # 향상된 추천 결과 테이블 생성
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS enhanced_job_recommendations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                trainee_id VARCHAR(50),
                trainee_name VARCHAR(100),
                job_id VARCHAR(50),
                job_title VARCHAR(500),
                company_name VARCHAR(200),
                industry VARCHAR(100),
                location VARCHAR(200),
                salary VARCHAR(200),
                job_type VARCHAR(100),
                experience VARCHAR(100),
                education VARCHAR(100),
                similarity_score DECIMAL(5,4),
                rank INT,
                job_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_trainee_id (trainee_id),
                INDEX idx_job_id (job_id),
                INDEX idx_similarity_score (similarity_score),
                INDEX idx_industry (industry)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
            
            cursor.execute(create_table_sql)
            connection.commit()
            
            # 기존 추천 결과 삭제
            cursor.execute("DELETE FROM enhanced_job_recommendations")
            connection.commit()
            
            # 새로운 추천 결과 삽입
            for recommendation in recommendations:
                insert_sql = """
                INSERT INTO enhanced_job_recommendations 
                (trainee_id, trainee_name, job_id, job_title, company_name, industry, location, salary, job_type, experience, education, similarity_score, rank, job_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_sql, (
                    recommendation['trainee_id'],
                    recommendation['trainee_name'],
                    recommendation['job_id'],
                    recommendation['job_title'],
                    recommendation['company_name'],
                    recommendation['industry'],
                    recommendation['location'],
                    recommendation['salary'],
                    recommendation['job_type'],
                    recommendation['experience'],
                    recommendation['education'],
                    recommendation['similarity_score'],
                    recommendation['rank'],
                    recommendation['job_url']
                ))
            
            connection.commit()
            cursor.close()
            connection.close()
            
            print(f"✅ 향상된 추천 결과 저장 완료: {len(recommendations)}개")
            
        except Exception as e:
            print(f"❌ 향상된 추천 결과 저장 오류: {e}")

def main():
    """메인 실행 함수"""
    print("🚀 향상된 SBERT 기반 채용 추천 시스템 시작")
    
    # 향상된 추천 시스템 초기화
    recommender = EnhancedJobRecommendationSystem()
    
    # 데이터 로드
    recommender.load_data()
    
    # 향상된 추천 결과 생성 (모든 훈련생에 대해)
    recommendations = recommender.get_enhanced_recommendations(top_k=5)
    
    # 데이터베이스에 저장
    recommender.save_enhanced_recommendations_to_db(recommendations)
    
    print("\n🎉 향상된 추천 시스템 완료!")
    print("📊 enhanced_job_recommendations 테이블에서 결과를 확인하세요.")

if __name__ == "__main__":
    main() 