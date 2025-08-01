import requests
import pandas as pd
from sqlalchemy import create_engine
import warnings
import time
from datetime import datetime, timedelta
import logging
warnings.filterwarnings('ignore')

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_job_collector.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def get_enhanced_job_data():
    """향상된 API 파라미터를 사용한 채용 데이터 수집"""
    try:
        access_key = "VOT7qjrkXGwLGfkT0obOaOk7Hb8Wf9pEB75RgvZKNTNd08Ky7a"
        
        # 2주 전 타임스탬프 계산
        two_weeks_ago = datetime.now() - timedelta(weeks=2)
        two_weeks_ago_ts = int(two_weeks_ago.timestamp())
        
        logging.info(f"2주 전 타임스탬프: {two_weeks_ago_ts} ({two_weeks_ago.strftime('%Y-%m-%d %H:%M:%S')})")
        
        # 페이지네이션을 위한 변수
        start = 0
        count = 100
        all_records = []
        
        # 향상된 API 파라미터
        base_params = {
            'access-key': access_key,
            'count': count,
            'fields': 'posting-date,expiration-date,keyword-code,count',  # 추가 필드 요청
            'sort': 'pd',  # 게시일 역순
            'sr': 'directhire'  # 헤드헌팅/파견업체 제외
        }
        
        while True:
            params = base_params.copy()
            params['start'] = start
            
            url = "https://oapi.saramin.co.kr/job-search"
            response = requests.get(url, params=params, headers={"Accept": "application/json"})
            data = response.json()
            
            job_data = data.get("jobs", {}).get("job", [])
            
            if not job_data:
                break
                
            if isinstance(job_data, dict):
                job_data = [job_data]
            
            # 2주 이내 데이터만 필터링
            filtered_jobs = []
            for job in job_data:
                posting_ts = job.get("posting-timestamp")
                if posting_ts and int(posting_ts) >= two_weeks_ago_ts:
                    filtered_jobs.append(job)
                else:
                    break
            
            if not filtered_jobs:
                break
                
            # 향상된 파싱
            for job in filtered_jobs:
                record = {
                    "job_id": job.get("id"),
                    "url": job.get("url"),
                    "active": job.get("active"),
                    "company_name": job.get("company", {}).get("detail", {}).get("name"),
                    "company_type": job.get("company", {}).get("detail", {}).get("type", {}).get("name"),  # 회사 유형
                    "company_size": job.get("company", {}).get("detail", {}).get("size", {}).get("name"),  # 회사 규모
                    "title": job.get("position", {}).get("title"),
                    "industry": job.get("position", {}).get("industry", {}).get("name"),
                    "industry_code": job.get("position", {}).get("industry", {}).get("code"),  # 산업 코드
                    "job_type": job.get("position", {}).get("job-type", {}).get("name"),
                    "job_type_code": job.get("position", {}).get("job-type", {}).get("code"),  # 직무 유형 코드
                    "location": job.get("position", {}).get("location", {}).get("name"),
                    "location_code": job.get("position", {}).get("location", {}).get("code"),  # 지역 코드
                    "experience": job.get("position", {}).get("experience-level", {}).get("name"),
                    "experience_code": job.get("position", {}).get("experience-level", {}).get("code"),  # 경력 코드
                    "education": job.get("position", {}).get("required-education-level", {}).get("name"),
                    "education_code": job.get("position", {}).get("required-education-level", {}).get("code"),  # 학력 코드
                    "salary": job.get("salary", {}).get("name"),
                    "salary_code": job.get("salary", {}).get("code"),  # 급여 코드
                    "posting_ts": job.get("posting-timestamp"),
                    "expiration_ts": job.get("expiration-timestamp"),
                    "keyword_code": job.get("keyword-code"),  # 키워드 코드
                    "view_count": job.get("count", {}).get("view"),  # 조회수
                    "apply_count": job.get("count", {}).get("apply"),  # 지원자수
                    "posting_date": job.get("posting-date"),  # 게시일
                    "expiration_date": job.get("expiration-date"),  # 마감일
                }
                all_records.append(record)
            
            logging.info(f"페이지 {start//count + 1}: {len(filtered_jobs)}개 수집 (총 {len(all_records)}개)")
            
            # 다음 페이지로
            start += count
            
            # API 호출 제한을 위한 딜레이
            time.sleep(0.5)
        
        return all_records
        
    except Exception as e:
        logging.error(f"API 데이터 수집 오류: {e}")
        return []

def create_enhanced_job_table():
    """향상된 채용 정보 테이블 생성"""
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
        
        # 향상된 테이블 생성 SQL
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS enhanced_job_postings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            job_id VARCHAR(50) UNIQUE,
            url TEXT,
            active TINYINT,
            company_name VARCHAR(200),
            company_type VARCHAR(100),
            company_size VARCHAR(100),
            title VARCHAR(500),
            industry VARCHAR(100),
            industry_code VARCHAR(20),
            job_type VARCHAR(100),
            job_type_code VARCHAR(20),
            location VARCHAR(200),
            location_code VARCHAR(100),
            experience VARCHAR(100),
            experience_code VARCHAR(20),
            education VARCHAR(100),
            education_code VARCHAR(20),
            salary VARCHAR(200),
            salary_code VARCHAR(20),
            posting_ts VARCHAR(50),
            expiration_ts VARCHAR(50),
            keyword_code VARCHAR(500),
            view_count INT,
            apply_count INT,
            posting_date VARCHAR(50),
            expiration_date VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_job_id (job_id),
            INDEX idx_company_name (company_name),
            INDEX idx_industry (industry),
            INDEX idx_industry_code (industry_code),
            INDEX idx_job_type (job_type),
            INDEX idx_location (location),
            INDEX idx_experience (experience),
            INDEX idx_education (education),
            INDEX idx_keyword_code (keyword_code(100))
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        cursor.execute(create_table_sql)
        connection.commit()
        print("✅ 향상된 테이블 생성 완료: enhanced_job_postings")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ 테이블 생성 오류: {e}")

def insert_enhanced_job_data(records):
    """향상된 채용 데이터 삽입"""
    try:
        if not records:
            logging.info("삽입할 데이터가 없습니다.")
            return
        
        df = pd.DataFrame(records)
        
        # SQLAlchemy 엔진 생성
        engine = create_engine(
            'mysql+pymysql://root:15861@127.0.0.1:3306/job_recoder?charset=utf8mb4'
        )
        
        # 중복 제거를 위해 기존 데이터 확인
        existing_jobs_query = "SELECT job_id FROM enhanced_job_postings"
        existing_jobs = pd.read_sql(existing_jobs_query, engine)
        existing_job_ids = set(existing_jobs['job_id'].tolist())
        
        # 새로운 데이터만 필터링
        new_df = df[~df['job_id'].isin(existing_job_ids)]
        
        if new_df.empty:
            logging.info("새로운 데이터가 없습니다.")
            return
        
        # 데이터 삽입
        new_df.to_sql(
            name='enhanced_job_postings',
            con=engine,
            if_exists='append',
            index=False,
            method='multi',
            chunksize=100
        )
        
        logging.info(f"✅ 향상된 데이터 삽입 완료: {len(new_df)}개 레코드 (총 수집: {len(df)}개)")
        
    except Exception as e:
        logging.error(f"❌ 데이터 삽입 오류: {e}")

def main():
    """메인 실행 함수"""
    print("🚀 향상된 채용 데이터 수집 시스템 시작")
    
    # 1. 향상된 테이블 생성
    create_enhanced_job_table()
    
    # 2. 향상된 데이터 수집
    records = get_enhanced_job_data()
    
    # 3. 데이터 삽입
    insert_enhanced_job_data(records)
    
    print("🎉 향상된 채용 데이터 수집 완료!")

if __name__ == "__main__":
    main() 