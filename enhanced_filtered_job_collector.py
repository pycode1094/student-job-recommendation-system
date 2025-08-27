import requests
import pandas as pd
from sqlalchemy import create_engine
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
        logging.FileHandler('enhanced_filtered_job_collector.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def is_target_industry(title, industry, keyword_code):
    """IT, 전기, 기계, 반도체, 로봇, 해양, AI 관련 채용인지 확인"""
    
    # 검색 키워드 정의 (AI 분야 추가)
    target_keywords = {
        'IT': ['개발자', '프로그래머', '소프트웨어', '웹개발', '앱개발', '프론트엔드', '백엔드', 
               '풀스택', '데이터', '클라우드', 'DevOps', '시스템', '네트워크', '보안', '블록체인', 
               '모바일', '게임', 'UI', 'UX', '디자이너', '기획자', 'PM', '프로덕트', 'QA', '테스터', 
               '인프라', '서버', 'DB', '데이터베이스'],
        
        'AI': ['AI', '인공지능', '머신러닝', '딥러닝', '머신비전', '컴퓨터비전', '자연어처리', 'NLP',
               '강화학습', '데이터사이언스', '데이터분석', '빅데이터', 'AI엔지니어', 'AI개발자',
               'AI연구원', 'AI과학자', 'AI알고리즘', 'AI플랫폼', 'AI솔루션', 'AI서비스', 'AI모델',
               'AI시스템', 'AI기술', 'AI프로젝트', 'AI제품', 'AI서비스', 'AI플랫폼', 'AI인프라'],
        
        '전기': ['전기', '전자', '전력', '전기공학', '전자공학', '전기설비', '전기시스템', 
                '전기제어', '전기설계', '전기시공', '전기안전', '전기기술', '전기장비', '전기회로',
                '전기공사', '전기기사', '전기기술자', '전기엔지니어', '전기기기', '전기설비관리'],
        
        '기계': ['기계', '기계공학', '기계설계', '기계제작', '기계가공', '기계조립', '기계정비',
                '기계설비', '기계시스템', '기계제어', '기계기술', '기계장비', '기계공사', '기계기사',
                '기계기술자', '기계엔지니어', '기계기기', '기계설비관리', 'CAD', 'CAM', 'CNC'],
        
        '반도체': ['반도체', '반도체공학', '반도체설계', '반도체제작', '반도체공정', '반도체장비',
                   '반도체기술', '반도체엔지니어', '반도체기사', '반도체기술자', '반도체설비',
                   '반도체시스템', '반도체제어', '반도체공사', '반도체기기', '반도체설비관리',
                   '웨이퍼', '패키징', '테스트', '검사', '품질관리'],
        
        '로봇': ['로봇', '로봇공학', '로봇설계', '로봇제작', '로봇제어', '로봇시스템', '로봇기술',
                '로봇엔지니어', '로봇기사', '로봇기술자', '로봇설비', '로봇공사', '로봇기기',
                '로봇설비관리', '자동화', '제어', '센서', '액추에이터', 'PLC', 'HMI'],
        
        '해양': ['해양', '해양공학', '해양설계', '해양제작', '해양시스템', '해양기술', '해양엔지니어',
                '해양기사', '해양기술자', '해양설비', '해양공사', '해양기기', '해양설비관리',
                '조선', '조선공학', '조선설계', '조선제작', '조선시스템', '조선기술', '조선엔지니어',
                '조선기사', '조선기술자', '조선설비', '조선공사', '조선기기', '조선설비관리',
                '선박', '선박공학', '선박설계', '선박제작', '선박시스템', '선박기술', '선박엔지니어',
                '선박기사', '선박기술자', '선박설비', '선박공사', '선박기기', '선박설비관리']
    }
    
    # 검색할 텍스트 조합
    search_text = f"{title} {industry} {keyword_code}".lower()
    
    # 각 카테고리별 키워드 검색
    for category, keywords in target_keywords.items():
        for keyword in keywords:
            if keyword.lower() in search_text:
                logging.info(f"✅ 매칭: {category} - {keyword} in '{title}'")
                return True
    
    return False

def get_enhanced_filtered_job_data():
    """3주 전부터 지금까지의 IT, AI, 전기, 기계, 반도체, 로봇, 해양 관련 채용 데이터 수집"""
    try:
        access_key = "VOT7qjrkXGwLGfkT0obOaOk7Hb8Wf9pEB75RgvZKNTNd08Ky7a"
        
        # 3주 전 타임스탬프 계산
        three_weeks_ago = datetime.now() - timedelta(weeks=3)
        three_weeks_ago_ts = int(three_weeks_ago.timestamp())
        
        logging.info(f"3주 전 타임스탬프: {three_weeks_ago_ts} ({three_weeks_ago.strftime('%Y-%m-%d %H:%M:%S')})")
        
        # 페이지네이션을 위한 변수
        start = 0
        count = 100
        all_records = []
        filtered_count = 0
        seen_job_ids = set()  # 중복 제거를 위한 set
        
        # 향상된 API 파라미터
        base_params = {
            'access-key': access_key,
            'count': count,
            'fields': 'posting-date,expiration-date,keyword-code,count',
            'sort': 'pd',  # 게시일 역순
            'sr': 'directhire'  # 헤드헌팅/파견업체 제외
        }
        
        page_count = 0
        while True:
            page_count += 1
            params = base_params.copy()
            params['start'] = start
            
            url = "https://oapi.saramin.co.kr/job-search"
            response = requests.get(url, params=params, headers={"Accept": "application/json"})
            data = response.json()
            
            job_data = data.get("jobs", {}).get("job", [])
            
            if not job_data:
                logging.info("더 이상 데이터가 없습니다.")
                break
                
            if isinstance(job_data, dict):
                job_data = [job_data]
            
            # 3주 이내 데이터만 필터링
            filtered_jobs = []
            for job in job_data:
                posting_ts = job.get("posting-timestamp")
                if posting_ts and int(posting_ts) >= three_weeks_ago_ts:
                    filtered_jobs.append(job)
                else:
                    logging.info("3주 이전 데이터 도달, 수집 중단")
                    break
            
            if not filtered_jobs:
                logging.info("필터링된 데이터가 없습니다.")
                break
            
            # 타겟 산업 필터링 및 중복 제거
            target_jobs = []
            for job in filtered_jobs:
                job_id = job.get("id")
                
                # 중복 체크
                if job_id in seen_job_ids:
                    continue
                
                title = job.get("position", {}).get("title", "")
                industry = job.get("position", {}).get("industry", {}).get("name", "")
                keyword_code = job.get("keyword-code", "")
                
                if is_target_industry(title, industry, keyword_code):
                    target_jobs.append(job)
                    seen_job_ids.add(job_id)  # 중복 방지를 위해 job_id 추가
                    filtered_count += 1
            
            # 향상된 파싱
            for job in target_jobs:
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
                }
                all_records.append(record)
            
            logging.info(f"페이지 {page_count}: {len(filtered_jobs)}개 중 {len(target_jobs)}개 필터링 (총 {len(all_records)}개, 중복제거: {len(seen_job_ids)}개)")
            
            # 다음 페이지로
            start += count
            
            # API 호출 제한을 위한 딜레이
            time.sleep(0.2)  # 더 빠른 수집을 위해 딜레이 단축
            
            # 최대 100페이지까지만 수집 (10,000개)
            if page_count >= 100:
                logging.info("최대 페이지 수에 도달했습니다.")
                break
        
        logging.info(f"✅ 총 {filtered_count}개의 타겟 채용 수집 완료 (중복 제거 후 {len(all_records)}개)")
        return all_records
        
    except Exception as e:
        logging.error(f"API 데이터 수집 오류: {e}")
        return []

def clear_enhanced_job_table():
    """enhanced_job_postings 테이블 비우기"""
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
        
        # 테이블 비우기
        truncate_sql = "TRUNCATE TABLE enhanced_job_postings"
        cursor.execute(truncate_sql)
        connection.commit()
        
        logging.info("✅ enhanced_job_postings 테이블 비우기 완료")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        logging.error(f"❌ 테이블 비우기 오류: {e}")

def insert_enhanced_filtered_job_data(records):
    """필터링된 채용 데이터 삽입"""
    try:
        if not records:
            logging.info("삽입할 데이터가 없습니다.")
            return
        
        df = pd.DataFrame(records)
        
        # SQLAlchemy 엔진 생성
        engine = create_engine(
            'mysql+pymysql://root:15861@127.0.0.1:3306/job_recoder?charset=utf8mb4'
        )
        
        # 데이터 삽입
        df.to_sql('enhanced_job_postings', engine, if_exists='append', index=False)
        
        logging.info(f"✅ {len(records)}개 데이터 삽입 완료")
        
    except Exception as e:
        logging.error(f"❌ 데이터 삽입 오류: {e}")

def main():
    """메인 실행 함수"""
    print("🚀 향상된 필터링된 채용 데이터 수집 시작...")
    
    # 1. 테이블 비우기
    print("🗑️ 기존 데이터 삭제 중...")
    clear_enhanced_job_table()
    
    # 2. 필터링된 데이터 수집
    print("📊 IT, AI, 전기, 기계, 반도체, 로봇, 해양 관련 채용 수집 중...")
    print("📅 3주 전부터 지금까지의 모든 공고 수집...")
    records = get_enhanced_filtered_job_data()
    
    if not records:
        print("❌ 수집된 데이터가 없습니다.")
        return
    
    # 3. 데이터 삽입
    print(f"💾 {len(records)}개 데이터 삽입 중...")
    insert_enhanced_filtered_job_data(records)
    
    print("✅ 향상된 필터링된 채용 데이터 수집 완료!")
    
    # 4. 통계 출력
    print(f"\n📈 수집 통계:")
    print(f"   - 총 수집된 채용: {len(records)}개")
    
    # 산업별 통계
    df = pd.DataFrame(records)
    if not df.empty:
        industry_stats = df['industry'].value_counts().head(10)
        print(f"   - 상위 산업:")
        for industry, count in industry_stats.items():
            print(f"     • {industry}: {count}개")
        
        # AI 관련 채용 통계
        ai_jobs = df[df['title'].str.contains('AI|인공지능|머신러닝|딥러닝', case=False, na=False)]
        print(f"   - AI 관련 채용: {len(ai_jobs)}개")

if __name__ == "__main__":
    main()
