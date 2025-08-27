import requests
import pandas as pd
from sqlalchemy import create_engine, text
import warnings
import time
from datetime import datetime, timedelta
import logging
import re
warnings.filterwarnings('ignore')

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('collect_more_jobs.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def is_target_industry(title, industry, keyword_code):
    """IT, AI, 전기, 기계, 반도체, 로봇, 해양 관련 채용인지 확인"""
    target_keywords = [
        'IT', 'AI', '인공지능', '머신러닝', '딥러닝', '데이터', '빅데이터',
        '전기', '전자', '제어', '전력', '반도체', '웨이퍼', '패키징',
        '기계', '설비', '자동차', '로봇', '자동화', '제어',
        '해양', '조선', '선박', 'marine', 'iot', '사물인터넷',
        '소프트웨어', '개발', '프로그래밍', '시스템', '솔루션'
    ]
    
    # 제목과 산업에서 키워드 검색
    search_text = f"{title} {industry}".lower()
    
    for keyword in target_keywords:
        if keyword.lower() in search_text:
            return True
    
    return False

def get_extended_job_data():
    """확장된 기간의 IT, AI, 전기, 기계, 반도체, 로봇, 해양 관련 채용 데이터 수집"""
    access_key = "VOT7qjrkXGwLGfkT0obOaOk7Hb8Wf9pEB75RgvZKNTNd08Ky7a"
    
    # 날짜 범위 확장 (최근 3개월)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)  # 3개월 전까지
    
    end_ts = int(end_date.timestamp())
    start_ts = int(start_date.timestamp())
    
    print(f"📅 수집 기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
    print(f"⏰ 타임스탬프: {start_ts} ~ {end_ts}")
    
    all_records = []
    page = 1
    count = 100  # 한 번에 가져올 개수
    
    while True:
        try:
            print(f"📄 {page}페이지 수집 중... (현재까지 {len(all_records)}개)")
            
            # Saramin API 호출
            url = "https://oapi.saramin.co.kr/job-search"
            params = {
                'access-key': access_key,
                'start': (page - 1) * count,
                'count': count,
                'fields': 'posting-date,expiration-date,keyword-code,count',
                'sort': 'pd',  # 게시일 역순
                'sr': 'directhire'  # 헤드헌팅/파견업체 제외
            }
            
            response = requests.get(url, params=params, headers={"Accept": "application/json"})
            
            if response.status_code != 200:
                print(f"❌ API 호출 실패: {response.status_code}")
                break
            
            data = response.json()
            job_data = data.get('jobs', {}).get('job', [])
            
            if not job_data:
                print("📭 더 이상 데이터가 없습니다.")
                break
            
            # 타겟 산업 필터링
            target_jobs = []
            for job in job_data:
                posting_ts = job.get("posting-timestamp")
                if posting_ts and start_ts <= int(posting_ts) <= end_ts:
                    title = job.get("position", {}).get("title", "")
                    industry = job.get("position", {}).get("industry", {}).get("name", "")
                    keyword_code = job.get("keyword-code", "")
                    
                    if is_target_industry(title, industry, keyword_code):
                        target_jobs.append(job)
            
            print(f"   ✅ {len(target_jobs)}개 타겟 채용 발견")
            
            # 데이터 파싱 및 저장
            for job in target_jobs:
                try:
                    record = {
                        "job_id": job.get("id"),
                        "url": job.get("url"),
                        "active": job.get("active"),
                        "company_name": job.get("company", {}).get("detail", {}).get("name"),
                        "company_type": job.get("company", {}).get("detail", {}).get("type", {}).get("name"),
                        "company_size": job.get("company", {}).get("detail", {}).get("size", {}).get("name"),
                        "title": job.get("position", {}).get("title"),
                        "industry": job.get("position", {}).get("industry", {}).get("name"),
                        "industry_code": job.get("position", {}).get("industry", {}).get("code"),
                        "job_type": job.get("position", {}).get("job-type", {}).get("name"),
                        "job_type_code": job.get("position", {}).get("job-type", {}).get("code"),
                        "location": job.get("position", {}).get("location", {}).get("name"),
                        "location_code": job.get("position", {}).get("location", {}).get("code"),
                        "experience": job.get("position", {}).get("experience-level", {}).get("name"),
                        "experience_code": job.get("position", {}).get("experience-level", {}).get("code"),
                        "education": job.get("position", {}).get("required-education-level", {}).get("name"),
                        "education_code": job.get("position", {}).get("required-education-level", {}).get("code"),
                        "salary": job.get("salary", {}).get("name"),
                        "salary_code": job.get("salary", {}).get("code"),
                        "posting_ts": job.get("posting-timestamp"),
                        "expiration_ts": job.get("expiration-timestamp"),
                        "keyword_code": job.get("keyword-code"),
                        "view_count": job.get("count", {}).get("view"),
                        "apply_count": job.get("count", {}).get("apply"),
                        "posting_date": job.get("posting-date"),
                        "expiration_date": job.get("expiration-date"),
                        "collected_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    all_records.append(record)
                    
                except Exception as e:
                    logging.error(f"데이터 파싱 오류: {e}")
                    continue
            
            # API 호출 간격 조절
            time.sleep(0.1)
            
            # 다음 페이지로
            page += 1
            
            # 안전장치: 너무 많은 페이지 수집 방지
            if page > 100:  # 최대 100페이지 (10,000개)
                print("⚠️ 최대 페이지 수에 도달했습니다.")
                break
                
        except Exception as e:
            logging.error(f"페이지 {page} 수집 오류: {e}")
            break
    
    print(f"\n🎉 총 {len(all_records)}개의 채용 데이터 수집 완료!")
    return all_records

def create_extended_job_table():
    """extended_job_postings 테이블 생성"""
    try:
        engine = create_engine(
            'mysql+pymysql://root:15861@127.0.0.1:3306/job_recoder?charset=utf8mb4'
        )
        
        with engine.connect() as connection:
            # 테이블 존재 여부 확인
            result = connection.execute(text("SHOW TABLES LIKE 'extended_job_postings'"))
            if result.fetchone():
                print("✅ extended_job_postings 테이블이 이미 존재합니다.")
                return True
            
            # 새 테이블 생성
            create_table_sql = """
            CREATE TABLE extended_job_postings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                job_id VARCHAR(50),
                url TEXT,
                active VARCHAR(10),
                company_name VARCHAR(200),
                company_type VARCHAR(100),
                company_size VARCHAR(100),
                title VARCHAR(300),
                industry VARCHAR(100),
                industry_code VARCHAR(20),
                job_type VARCHAR(100),
                job_type_code VARCHAR(20),
                location VARCHAR(200),
                location_code VARCHAR(50),
                experience VARCHAR(100),
                experience_code VARCHAR(20),
                education VARCHAR(100),
                education_code VARCHAR(20),
                salary VARCHAR(100),
                salary_code VARCHAR(20),
                posting_ts BIGINT,
                expiration_ts BIGINT,
                keyword_code TEXT,
                view_count INT,
                apply_count INT,
                posting_date VARCHAR(50),
                expiration_date VARCHAR(50),
                collected_date DATETIME,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            COMMENT='확장된 기간 채용 데이터'
            """
            
            connection.execute(text(create_table_sql))
            connection.commit()
            print("✅ extended_job_postings 테이블 생성 완료!")
            return True
            
    except Exception as e:
        print(f"❌ 테이블 생성 오류: {e}")
        return False

def clear_extended_job_table():
    """extended_job_postings 테이블 비우기"""
    try:
        import pymysql
        
        connection = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='15861',
            database='job_recoder',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE extended_job_postings")
            connection.commit()
        
        connection.close()
        print("✅ extended_job_postings 테이블 비우기 완료!")
        
    except Exception as e:
        print(f"❌ 테이블 비우기 오류: {e}")

def insert_extended_job_data(records):
    """확장된 채용 데이터 삽입"""
    try:
        if not records:
            print("❌ 삽입할 데이터가 없습니다.")
            return False
        
        # DataFrame 생성
        df = pd.DataFrame(records)
        
        # 데이터 타입 정리
        for col in df.columns:
            if col in ['expiration_ts', 'posting_ts']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            elif col in ['view_count', 'apply_count']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 쉼표로 구분된 값들 정리 (첫 번째 값만 사용)
        for col in ['location_code', 'job_type_code', 'industry_code']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.split(',').str[0].str[:50]
        
        # SQLAlchemy로 데이터 삽입
        engine = create_engine(
            'mysql+pymysql://root:15861@127.0.0.1:3306/job_recoder?charset=utf8mb4'
        )
        
        df.to_sql('extended_job_postings', engine, if_exists='append', index=False)
        
        print(f"✅ {len(records)}개 채용 데이터 삽입 완료!")
        return True
        
    except Exception as e:
        print(f"❌ 데이터 삽입 오류: {e}")
        return False

def show_collection_summary():
    """수집 결과 요약 출력"""
    try:
        engine = create_engine(
            'mysql+pymysql://root:15861@127.0.0.1:3306/job_recoder?charset=utf8mb4'
        )
        
        # 전체 수집 데이터 수
        total_count = pd.read_sql("SELECT COUNT(*) as total FROM extended_job_postings", engine)
        print(f"\n📊 수집 결과 요약:")
        print(f"   - 총 수집된 채용: {total_count.iloc[0]['total']}개")
        
        # 산업별 분포
        industry_stats = pd.read_sql("""
            SELECT industry, COUNT(*) as count 
            FROM extended_job_postings 
            GROUP BY industry 
            ORDER BY count DESC 
            LIMIT 10
        """, engine)
        
        print(f"\n🏭 산업별 분포 (상위 10개):")
        for idx, row in industry_stats.iterrows():
            print(f"   • {row['industry']}: {row['count']}개")
        
        # 지역별 분포
        location_stats = pd.read_sql("""
            SELECT location, COUNT(*) as count 
            FROM extended_job_postings 
            GROUP BY location 
            ORDER BY count DESC 
            LIMIT 10
        """, engine)
        
        print(f"\n📍 지역별 분포 (상위 10개):")
        for idx, row in location_stats.iterrows():
            print(f"   • {row['location']}: {row['count']}개")
        
        # 부산 지역 확인
        busan_jobs = pd.read_sql("""
            SELECT company_name, title, industry 
            FROM extended_job_postings 
            WHERE location LIKE '%부산%'
            LIMIT 10
        """, engine)
        
        print(f"\n🌊 부산 지역 채용 (상위 10개):")
        if len(busan_jobs) > 0:
            for idx, row in busan_jobs.iterrows():
                print(f"   • {row['company_name']} - {row['title']} ({row['industry']})")
        else:
            print("   • 부산 지역 채용이 없습니다.")
        
        # AI 관련 채용
        ai_jobs = pd.read_sql("""
            SELECT COUNT(*) as count 
            FROM extended_job_postings 
            WHERE title LIKE '%AI%' OR title LIKE '%인공지능%' OR title LIKE '%머신러닝%'
        """, engine)
        
        print(f"\n🤖 AI 관련 채용: {ai_jobs.iloc[0]['count']}개")
        
    except Exception as e:
        print(f"❌ 요약 출력 오류: {e}")

def main():
    """메인 실행 함수"""
    print("🚀 확장된 기간 채용 데이터 수집 시작...")
    print(f"📅 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 테이블 생성
    if not create_extended_job_table():
        return
    
    # 2. 기존 데이터 비우기
    clear_extended_job_table()
    
    # 3. 채용 데이터 수집
    records = get_extended_job_data()
    
    if not records:
        print("❌ 수집된 데이터가 없습니다.")
        return
    
    # 4. 데이터 삽입
    if insert_extended_job_data(records):
        # 5. 결과 요약 출력
        show_collection_summary()
        print("\n🎉 확장된 채용 데이터 수집 완료!")
    else:
        print("\n❌ 데이터 수집 실패!")

if __name__ == "__main__":
    main()
