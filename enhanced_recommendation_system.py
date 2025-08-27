import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import logging
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import warnings
from datetime import datetime
import random
warnings.filterwarnings('ignore')

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_recommendation_system.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class EnhancedRecommendationSystem:
    def __init__(self):
        """향상된 추천 시스템 초기화"""
        try:
            # SBERT 모델 로드
            print("🤖 SBERT 모델을 로드하는 중...")
            self.model = SentenceTransformer('xlm-r-100langs-bert-base-nli-stsb-mean-tokens')
            print("✅ SBERT 모델 로드 완료!")
        except Exception as e:
            print(f"❌ SBERT 모델 로드 실패: {e}")
            print("💡 sentence-transformers 패키지를 설치해주세요: pip install sentence-transformers")
            return None
        
        # 데이터베이스 연결
        self.engine = create_engine(
            'mysql+pymysql://root:15861@127.0.0.1:3306/job_recoder?charset=utf8mb4'
        )
        
        # 정교한 가중치 시스템
        self.weights = {
            'semantic_similarity': 0.35,    # SBERT 의미적 유사도 (가장 중요)
            'course_industry_match': 0.25,  # 과정-산업 매칭
            'location_preference': 0.20,    # 지역 선호도
            'company_diversity': 0.15,      # 회사 다양성
            'freshness_bonus': 0.05         # 최신성 보너스
        }
        
        # 지역별 가중치 (부산 지역 우선)
        self.location_weights = {
            '부산': 1.2,      # 부산 지역 가중치 증가
            '울산': 1.1,      # 울산 지역 가중치 증가
            '경남': 1.05,     # 경남 지역 가중치 증가
            '서울': 0.95,     # 서울 지역 가중치 감소
            '경기': 0.9       # 경기 지역 가중치 감소
        }
        
        # 산업별 가중치 (반도체/IT 우선)
        self.industry_weights = {
            '반도체·광학·LCD': 1.3,
            'AI·인공지능': 1.25,
            '전기·전자·제어': 1.2,
            '기계·설비·자동차': 1.1,
            '솔루션·SI·ERP·CRM': 1.15,
            '기타': 0.8
        }
        
        self.logger = logging.getLogger(__name__)
        
        # 다양성 확보를 위한 변수
        self.used_companies = set()
        self.used_locations = set()
        self.used_industries = set()
    
    def create_enhanced_testresult_table(self):
        """향상된 testresult 테이블 생성"""
        try:
            print("🔧 향상된 testresult 테이블을 생성합니다...")
            
            with self.engine.connect() as connection:
                # 기존 테이블 삭제
                connection.execute(text("DROP TABLE IF EXISTS enhanced_testresult"))
                connection.commit()
                print("✅ 기존 enhanced_testresult 테이블 삭제 완료")
                
                # 새 테이블 생성
                create_table_sql = """
                CREATE TABLE enhanced_testresult (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id VARCHAR(20),
                    student_name VARCHAR(50),
                    course_name VARCHAR(100),
                    survey_responses TEXT,
                    recommended_job_id VARCHAR(50),
                    recommended_company VARCHAR(200),
                    recommended_title VARCHAR(300),
                    recommended_industry VARCHAR(100),
                    recommended_location VARCHAR(200),
                    recommended_job_type VARCHAR(100),
                    semantic_similarity DECIMAL(5,4),
                    course_industry_score DECIMAL(5,4),
                    location_score DECIMAL(5,4),
                    diversity_score DECIMAL(5,4),
                    freshness_score DECIMAL(5,4),
                    final_score DECIMAL(5,4),
                    recommendation_rank INT,
                    diversity_penalty DECIMAL(5,4),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                COMMENT='향상된 학생별 추천 결과 테이블'
                """
                connection.execute(text(create_table_sql))
                connection.commit()
                print("✅ 새로운 enhanced_testresult 테이블 생성 완료")
            
            return True
            
        except Exception as e:
            print(f"❌ 테이블 생성 오류: {e}")
            return False
    
    def load_and_merge_job_data(self):
        """모든 채용 데이터 로드 및 통합"""
        try:
            print("📊 채용 데이터를 로드하고 통합합니다...")
            
            # 1. 기존 job_postings 데이터
            try:
                job_postings_df = pd.read_sql("SELECT * FROM job_postings", self.engine)
                print(f"   📋 job_postings: {len(job_postings_df)}개")
            except Exception as e:
                print(f"   ⚠️ job_postings 테이블이 없습니다: {e}")
                job_postings_df = pd.DataFrame()
            
            # 2. extended_job_postings 데이터
            try:
                extended_df = pd.read_sql("SELECT * FROM extended_job_postings", self.engine)
                print(f"   📋 extended_job_postings: {len(extended_df)}개")
            except Exception as e:
                print(f"   ⚠️ extended_job_postings 테이블이 없습니다: {e}")
                extended_df = pd.DataFrame()
            
            # 3. 데이터 통합
            if not job_postings_df.empty and not extended_df.empty:
                # 중복 제거 (job_id 기준)
                all_jobs = pd.concat([job_postings_df, extended_df], ignore_index=True)
                all_jobs = all_jobs.drop_duplicates(subset=['job_id'], keep='first')
                print(f"   🔗 통합 후 중복 제거: {len(all_jobs)}개")
            elif not job_postings_df.empty:
                all_jobs = job_postings_df
            elif not extended_df.empty:
                all_jobs = extended_df
            else:
                print("❌ 사용 가능한 채용 데이터가 없습니다.")
                return None
            
            # 4. 데이터 정리
            all_jobs = all_jobs.fillna('')
            
            # 5. 만료된 공고 제거
            current_ts = int(datetime.now().timestamp())
            if 'expiration_ts' in all_jobs.columns:
                all_jobs['expiration_ts'] = pd.to_numeric(all_jobs['expiration_ts'], errors='coerce')
                active_jobs = all_jobs[all_jobs['expiration_ts'] > current_ts]
                print(f"   🗑️ 만료된 공고 제거: {len(all_jobs) - len(active_jobs)}개")
                all_jobs = active_jobs
            
            print(f"✅ 최종 사용 가능한 채용 공고: {len(all_jobs)}개")
            return all_jobs
            
        except Exception as e:
            print(f"❌ 데이터 로드 오류: {e}")
            return None
    
    def prepare_student_profiles(self):
        """학생 프로필 준비 및 향상"""
        try:
            print("\n👥 학생 프로필을 준비합니다...")
            
            beta_test_df = pd.read_sql("SELECT * FROM RecoderBetaTest", self.engine)
            student_profiles = []
            
            for idx, row in beta_test_df.iterrows():
                # 학생 기본 정보
                student_id = row.get('student_id', f'student_{idx}')
                student_name = row.get('이름을_입력해주세요', 'Unknown')
                course_name = row.get('과정명을_확인해주세요맞으면_선택', 'Unknown')
                
                # 설문 응답 내용을 하나의 텍스트로 결합
                survey_texts = []
                for col in beta_test_df.columns:
                    if col not in ['id', 'student_id', '이름을_입력해주세요', '과정명을_확인해주세요맞으면_선택']:
                        value = row.get(col, '')
                        if pd.notna(value) and str(value).strip():
                            survey_texts.append(f"{col}: {value}")
                
                survey_responses = " | ".join(survey_texts)
                
                # 과정명에서 주요 키워드 추출
                course_keywords = self.extract_enhanced_course_keywords(course_name)
                
                # 지역 선호도 추출 (설문에서)
                location_preference = self.extract_location_preference(survey_responses)
                
                profile = {
                    'student_id': student_id,
                    'student_name': student_name,
                    'course_name': course_name,
                    'survey_responses': survey_responses,
                    'course_keywords': course_keywords,
                    'location_preference': location_preference,
                    'semantic_embedding': None  # 나중에 계산
                }
                
                student_profiles.append(profile)
            
            print(f"✅ {len(student_profiles)}명의 학생 프로필 준비 완료")
            return student_profiles
            
        except Exception as e:
            print(f"❌ 학생 프로필 준비 오류: {e}")
            return None
    
    def extract_enhanced_course_keywords(self, course_name):
        """향상된 과정명 키워드 추출"""
        if pd.isna(course_name):
            return ""
        
        course_name = str(course_name).lower()
        
        # 더 정교한 키워드 매핑
        keyword_mapping = {
            'ai': ['ai', '인공지능', '머신러닝', '딥러닝', 'neural', 'algorithm'],
            'iot': ['iot', '사물인터넷', '인터넷', '센서', 'sensor', 'network'],
            '반도체': ['반도체', 'semiconductor', '웨이퍼', 'wafer', '패키징', 'packaging', 'fab'],
            '전기': ['전기', '전자', '전력', 'electric', 'electronic', 'power', 'circuit'],
            '기계': ['기계', 'mechanical', '설계', 'design', '제작', 'manufacturing', 'cad'],
            '로봇': ['로봇', 'robot', '자동화', 'automation', '제어', 'control', 'motion'],
            '해양': ['해양', 'marine', '조선', 'shipbuilding', '선박', 'vessel', 'offshore'],
            'it': ['it', '개발', 'development', '프로그래밍', 'programming', '소프트웨어', 'software'],
            '데이터': ['데이터', 'data', '분석', 'analysis', '빅데이터', 'bigdata', 'mining'],
            '시스템': ['시스템', 'system', '아키텍처', 'architecture', '인프라', 'infrastructure']
        }
        
        extracted_keywords = []
        for category, keywords in keyword_mapping.items():
            for keyword in keywords:
                if keyword in course_name:
                    extracted_keywords.append(category)
                    break
        
        return " ".join(extracted_keywords)
    
    def extract_location_preference(self, survey_responses):
        """설문에서 지역 선호도 추출"""
        if pd.isna(survey_responses):
            return []
        
        responses = str(survey_responses).lower()
        
        # 지역 키워드 매핑
        location_keywords = {
            '부산': ['부산', 'busan', '해운대', '동래', '서면', '남포동'],
            '서울': ['서울', 'seoul', '강남', '홍대', '강북', '종로'],
            '울산': ['울산', 'ulsan', '울주', '남구', '동구', '북구'],
            '경남': ['경남', '경상남도', '김해', '양산', '창원', '진주'],
            '경기': ['경기', '경기도', '성남', '수원', '안양', '화성'],
            '인천': ['인천', 'incheon', '송도', '연수', '남동', '부평']
        }
        
        preferred_locations = []
        for location, keywords in location_keywords.items():
            for keyword in keywords:
                if keyword in responses:
                    preferred_locations.append(location)
                    break
        
        return preferred_locations
    
    def calculate_semantic_similarity(self, student_profile, job_data):
        """SBERT를 사용한 의미적 유사도 계산"""
        try:
            if not student_profile['course_keywords'] or not job_data.get('title'):
                return 0.0
            
            # 학생 과정 키워드와 채용 제목 간의 의미적 유사도
            course_text = student_profile['course_keywords']
            job_text = f"{job_data.get('title', '')} {job_data.get('industry', '')}"
            
            # SBERT 임베딩 생성
            course_embedding = self.model.encode([course_text])
            job_embedding = self.model.encode([job_text])
            
            # 코사인 유사도 계산
            similarity = cosine_similarity(course_embedding, job_embedding)[0][0]
            
            return float(similarity)
            
        except Exception as e:
            self.logger.error(f"의미적 유사도 계산 오류: {e}")
            return 0.0
    
    def calculate_course_industry_match(self, student_profile, job_data):
        """과정-산업 매칭 점수 계산"""
        try:
            course_keywords = student_profile['course_keywords'].lower()
            industry = str(job_data.get('industry', '')).lower()
            title = str(job_data.get('title', '')).lower()
            
            # 키워드 매칭 점수
            match_score = 0.0
            
            # 반도체 관련
            if any(keyword in course_keywords for keyword in ['반도체', 'semiconductor']):
                if any(keyword in industry + ' ' + title for keyword in ['반도체', 'semiconductor', 'wafer', 'fab']):
                    match_score += 0.8
            
            # AI 관련
            if any(keyword in course_keywords for keyword in ['ai', '인공지능', '머신러닝']):
                if any(keyword in industry + ' ' + title for keyword in ['ai', '인공지능', '머신러닝', '딥러닝']):
                    match_score += 0.8
            
            # 전기/전자 관련
            if any(keyword in course_keywords for keyword in ['전기', '전자', 'electric']):
                if any(keyword in industry + ' ' + title for keyword in ['전기', '전자', 'electric', 'electronic']):
                    match_score += 0.7
            
            # 기계 관련
            if any(keyword in course_keywords for keyword in ['기계', 'mechanical']):
                if any(keyword in industry + ' ' + title for keyword in ['기계', 'mechanical', '설계', 'design']):
                    match_score += 0.7
            
            # IoT 관련
            if any(keyword in course_keywords for keyword in ['iot', '사물인터넷']):
                if any(keyword in industry + ' ' + title for keyword in ['iot', '사물인터넷', '센서', 'sensor']):
                    match_score += 0.7
            
            return min(match_score, 1.0)
            
        except Exception as e:
            self.logger.error(f"과정-산업 매칭 계산 오류: {e}")
            return 0.0
    
    def calculate_location_score(self, student_profile, job_data):
        """지역 점수 계산"""
        try:
            location = str(job_data.get('location', '')).lower()
            preferred_locations = student_profile['location_preference']
            
            # 기본 지역 점수
            base_score = 0.5
            
            # 선호 지역과 일치하는 경우
            for preferred in preferred_locations:
                if preferred.lower() in location:
                    base_score += 0.3
                    break
            
            # 지역별 가중치 적용
            for region, weight in self.location_weights.items():
                if region in location:
                    base_score *= weight
                    break
            
            return min(base_score, 1.0)
            
        except Exception as e:
            self.logger.error(f"지역 점수 계산 오류: {e}")
            return 0.5
    
    def calculate_diversity_score(self, student_profile, job_data, current_recommendations):
        """다양성 점수 계산 (중복 회사/지역/산업 페널티)"""
        try:
            diversity_score = 1.0
            
            # 회사 중복 페널티
            company = job_data.get('company_name', '')
            if company in self.used_companies:
                diversity_score -= 0.3
            
            # 지역 중복 페널티
            location = job_data.get('location', '')
            if location in self.used_locations:
                diversity_score -= 0.2
            
            # 산업 중복 페널티
            industry = job_data.get('industry', '')
            if industry in self.used_industries:
                diversity_score -= 0.2
            
            # 현재 학생의 기존 추천과 중복 체크
            student_id = student_profile['student_id']
            if student_id in current_recommendations:
                existing_companies = set()
                existing_locations = set()
                existing_industries = set()
                
                for rec in current_recommendations[student_id]:
                    existing_companies.add(rec.get('company', ''))
                    existing_locations.add(rec.get('location', ''))
                    existing_industries.add(rec.get('industry', ''))
                
                if company in existing_companies:
                    diversity_score -= 0.4
                if location in existing_locations:
                    diversity_score -= 0.3
                if industry in existing_industries:
                    diversity_score -= 0.3
            
            return max(diversity_score, 0.1)  # 최소 0.1점 보장
            
        except Exception as e:
            self.logger.error(f"다양성 점수 계산 오류: {e}")
            return 0.5
    
    def calculate_freshness_score(self, job_data):
        """최신성 점수 계산"""
        try:
            posting_ts = job_data.get('posting_ts')
            if not posting_ts:
                return 0.5
            
            posting_ts = int(posting_ts)
            current_ts = int(datetime.now().timestamp())
            
            # 게시된 지 얼마나 되었는지 계산 (일 단위)
            days_ago = (current_ts - posting_ts) / (24 * 3600)
            
            # 최신성 점수 (최근일수록 높은 점수)
            if days_ago <= 7:      # 1주일 이내
                return 1.0
            elif days_ago <= 30:   # 1개월 이내
                return 0.8
            elif days_ago <= 90:   # 3개월 이내
                return 0.6
            else:                   # 3개월 이상
                return 0.4
                
        except Exception as e:
            self.logger.error(f"최신성 점수 계산 오류: {e}")
            return 0.5
    
    def calculate_final_score(self, scores):
        """최종 점수 계산 (가중 평균)"""
        try:
            final_score = (
                scores['semantic_similarity'] * self.weights['semantic_similarity'] +
                scores['course_industry_match'] * self.weights['course_industry_match'] +
                scores['location_score'] * self.weights['location_preference'] +
                scores['diversity_score'] * self.weights['company_diversity'] +
                scores['freshness_score'] * self.weights['freshness_bonus']
            )
            
            return round(final_score, 4)
            
        except Exception as e:
            self.logger.error(f"최종 점수 계산 오류: {e}")
            return 0.0
    
    def generate_enhanced_recommendations(self, student_profiles, job_data_df):
        """향상된 추천 생성"""
        print("\n🎯 향상된 추천을 생성합니다...")
        
        all_recommendations = []
        current_recommendations = {}  # 학생별 현재 추천 추적
        
        for student in student_profiles:
            print(f"📋 {student['student_name']} ({student['course_name']}) 향상된 추천 생성 중...")
            
            # 학생별 추천 초기화
            current_recommendations[student['student_id']] = []
            
            # 모든 채용 공고와의 점수 계산
            job_scores = []
            
            for idx, job in job_data_df.iterrows():
                try:
                    # 각 항목별 점수 계산
                    semantic_score = self.calculate_semantic_similarity(student, job)
                    course_industry_score = self.calculate_course_industry_match(student, job)
                    location_score = self.calculate_location_score(student, job)
                    diversity_score = self.calculate_diversity_score(student, job, current_recommendations)
                    freshness_score = self.calculate_freshness_score(job)
                    
                    # 최종 점수 계산
                    final_score = self.calculate_final_score({
                        'semantic_similarity': semantic_score,
                        'course_industry_match': course_industry_score,
                        'location_score': location_score,
                        'diversity_score': diversity_score,
                        'freshness_score': freshness_score
                    })
                    
                    job_scores.append({
                        'job_id': job.get('job_id'),
                        'company': job.get('company_name'),
                        'title': job.get('title'),
                        'industry': job.get('industry'),
                        'location': job.get('location'),
                        'job_type': job.get('job_type'),
                        'semantic_similarity': semantic_score,
                        'course_industry_score': course_industry_score,
                        'location_score': location_score,
                        'diversity_score': diversity_score,
                        'freshness_score': freshness_score,
                        'final_score': final_score
                    })
                    
                except Exception as e:
                    self.logger.error(f"점수 계산 오류: {e}")
                    continue
            
            # 최종 점수 순으로 정렬하고 상위 5개 선택
            job_scores.sort(key=lambda x: x['final_score'], reverse=True)
            top_5_recommendations = job_scores[:5]
            
            # 추천 결과를 데이터베이스 형식으로 변환
            for rank, rec in enumerate(top_5_recommendations, 1):
                recommendation = {
                    'student_id': student['student_id'],
                    'student_name': student['student_name'],
                    'course_name': student['course_name'],
                    'survey_responses': student['survey_responses'],
                    'recommended_job_id': rec['job_id'],
                    'recommended_company': rec['company'],
                    'recommended_title': rec['title'],
                    'recommended_industry': rec['industry'],
                    'recommended_location': rec['location'],
                    'recommended_job_type': rec['job_type'],
                    'semantic_similarity': rec['semantic_similarity'],
                    'course_industry_score': rec['course_industry_score'],
                    'location_score': rec['location_score'],
                    'diversity_score': rec['diversity_score'],
                    'freshness_score': rec['freshness_score'],
                    'final_score': rec['final_score'],
                    'recommendation_rank': rank,
                    'diversity_penalty': 1.0 - rec['diversity_score']
                }
                
                all_recommendations.append(recommendation)
                current_recommendations[student['student_id']].append({
                    'company': rec['company'],
                    'location': rec['location'],
                    'industry': rec['industry']
                })
                
                # 다양성 추적 업데이트
                self.used_companies.add(rec['company'])
                self.used_locations.add(rec['location'])
                self.used_industries.add(rec['industry'])
            
            print(f"   ✅ {len(top_5_recommendations)}개 향상된 추천 완료")
        
        print(f"\n🎉 총 {len(all_recommendations)}개의 향상된 추천 결과 생성 완료!")
        return all_recommendations
    
    def save_enhanced_recommendations(self, recommendations):
        """향상된 추천 결과를 enhanced_testresult 테이블에 저장"""
        try:
            print("\n💾 향상된 추천 결과를 데이터베이스에 저장합니다...")
            
            df = pd.DataFrame(recommendations)
            
            # 데이터 삽입
            df.to_sql('enhanced_testresult', self.engine, if_exists='append', index=False)
            
            print(f"✅ {len(recommendations)}개 향상된 추천 결과 저장 완료!")
            return True
            
        except Exception as e:
            print(f"❌ 향상된 추천 결과 저장 오류: {e}")
            return False
    
    def show_enhanced_summary(self):
        """향상된 추천 결과 요약 출력"""
        try:
            print("\n📊 향상된 추천 결과 요약:")
            
            # 전체 추천 수
            total_count = pd.read_sql("SELECT COUNT(*) as total FROM enhanced_testresult", self.engine)
            print(f"   - 총 추천 수: {total_count.iloc[0]['total']}개")
            
            # 학생별 추천 수
            student_count = pd.read_sql("SELECT COUNT(DISTINCT student_id) as students FROM enhanced_testresult", self.engine)
            print(f"   - 추천 대상 학생: {student_count.iloc[0]['students']}명")
            
            # 점수 통계
            score_stats = pd.read_sql("""
                SELECT 
                    AVG(final_score) as avg_final_score,
                    AVG(semantic_similarity) as avg_semantic,
                    AVG(course_industry_score) as avg_course_industry,
                    AVG(location_score) as avg_location,
                    AVG(diversity_score) as avg_diversity,
                    AVG(freshness_score) as avg_freshness
                FROM enhanced_testresult
            """, self.engine)
            
            print(f"\n📈 점수 통계:")
            print(f"   • 최종 점수 평균: {score_stats.iloc[0]['avg_final_score']:.4f}")
            print(f"   • 의미적 유사도 평균: {score_stats.iloc[0]['avg_semantic']:.4f}")
            print(f"   • 과정-산업 매칭 평균: {score_stats.iloc[0]['avg_course_industry']:.4f}")
            print(f"   • 지역 점수 평균: {score_stats.iloc[0]['avg_location']:.4f}")
            print(f"   • 다양성 점수 평균: {score_stats.iloc[0]['avg_diversity']:.4f}")
            print(f"   • 최신성 점수 평균: {score_stats.iloc[0]['avg_freshness']:.4f}")
            
            # 상위 추천 회사 (다양성 고려)
            top_companies = pd.read_sql("""
                SELECT recommended_company, COUNT(*) as count 
                FROM enhanced_testresult 
                WHERE recommendation_rank = 1 
                GROUP BY recommended_company 
                ORDER BY count DESC 
                LIMIT 10
            """, self.engine)
            
            print(f"\n🏆 상위 추천 회사 (다양성 고려):")
            for idx, row in top_companies.iterrows():
                print(f"   • {row['recommended_company']}: {row['count']}회")
            
            # 지역별 분포
            location_dist = pd.read_sql("""
                SELECT recommended_location, COUNT(*) as count 
                FROM enhanced_testresult 
                GROUP BY recommended_location 
                ORDER BY count DESC 
                LIMIT 10
            """, self.engine)
            
            print(f"\n📍 추천 지역별 분포:")
            for idx, row in location_dist.iterrows():
                print(f"   • {row['recommended_location']}: {row['count']}회")
            
            # 부산 지역 추천 확인
            busan_recommendations = pd.read_sql("""
                SELECT COUNT(*) as count 
                FROM enhanced_testresult 
                WHERE recommended_location LIKE '%부산%'
            """, self.engine)
            
            print(f"\n🌊 부산 지역 추천: {busan_recommendations.iloc[0]['count']}회")
            
        except Exception as e:
            print(f"❌ 향상된 요약 출력 오류: {e}")
    
    def run_enhanced_system(self):
        """향상된 추천 시스템 실행"""
        print("🚀 향상된 추천 시스템을 시작합니다...")
        print(f"📅 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. 향상된 테이블 생성
        if not self.create_enhanced_testresult_table():
            return False
        
        # 2. 채용 데이터 로드 및 통합
        job_data_df = self.load_and_merge_job_data()
        if job_data_df is None:
            return False
        
        # 3. 학생 프로필 준비
        student_profiles = self.prepare_student_profiles()
        if not student_profiles:
            return False
        
        # 4. 향상된 추천 생성
        recommendations = self.generate_enhanced_recommendations(student_profiles, job_data_df)
        
        # 5. 향상된 추천 결과 저장
        if self.save_enhanced_recommendations(recommendations):
            # 6. 향상된 결과 요약 출력
            self.show_enhanced_summary()
            
            print("\n🎉 향상된 추천 시스템 실행 완료!")
            print("📊 enhanced_testresult 테이블에서 향상된 추천 결과를 확인할 수 있습니다.")
            return True
        else:
            print("\n❌ 향상된 추천 시스템 실행 실패!")
            return False

def main():
    """메인 실행 함수"""
    print("🚀 향상된 SBERT 기반 학생 추천 시스템 시작...")
    
    # 향상된 추천 시스템 초기화
    enhanced_system = EnhancedRecommendationSystem()
    
    if enhanced_system is None:
        print("❌ 향상된 추천 시스템 초기화 실패!")
        return
    
    # 향상된 추천 시스템 실행
    success = enhanced_system.run_enhanced_system()
    
    if success:
        print("\n✅ 모든 작업이 완료되었습니다!")
    else:
        print("\n❌ 작업 중 오류가 발생했습니다.")

if __name__ == "__main__":
    main()
