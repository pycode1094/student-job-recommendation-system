import pandas as pd
from sqlalchemy import create_engine, text
import pymysql
import logging
from datetime import datetime
import random

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class StudentDataUpdater:
    def __init__(self):
        """학생 데이터 업데이트 초기화"""
        self.engine = create_engine(
            'mysql+pymysql://root:15861@127.0.0.1:3306/job_recoder?charset=utf8mb4'
        )
        self.logger = logging.getLogger(__name__)
        
        # 과정명별 희망직종 매핑 (간단한 버전)
        self.course_job_mapping = {
            # IT/개발 과정
            '웹': ['웹개발자', '프론트엔드 개발자', '백엔드 개발자'],
            '앱': ['앱개발자', '모바일 개발자', 'iOS 개발자', 'Android 개발자'],
            'Python': ['Python 개발자', '백엔드 개발자', '데이터 엔지니어'],
            'Java': ['Java 개발자', '백엔드 개발자', '소프트웨어 개발자'],
            'AI': ['AI 개발자', '머신러닝 엔지니어', '데이터 사이언티스트'],
            '데이터': ['데이터 엔지니어', '데이터 분석가', '빅데이터 엔지니어'],
            'DevOps': ['DevOps 엔지니어', '시스템 엔지니어', '클라우드 엔지니어'],
            '보안': ['보안 엔지니어', '정보보안 전문가', '시스템 보안 관리자'],
            '게임': ['게임 개발자', '게임 프로그래머', 'Unity 개발자'],
            'UI': ['UI/UX 디자이너', '웹 디자이너', '그래픽 디자이너'],
            '클라우드': ['클라우드 엔지니어', 'AWS 엔지니어', 'Azure 엔지니어'],
            
            # 기계/전기 과정
            '기계': ['기계설계기술자', '기계제작기술자', '기계조립기술자', '기계정비기술자'],
            '전기': ['전기기술자', '전기설비기술자', '전기제어기술자', '전기정비기술자'],
            '전자': ['전자기술자', '전자제품개발자', '전자정비기술자'],
            '자동화': ['자동화기술자', '제어기술자', 'PLC기술자'],
            '건설': ['건설기술자', '토목기술자', '건축기술자'],
            '화학': ['화학기술자', '화학공정기술자', '품질관리기술자'],
            
            # 기본 매핑
            'default': ['소프트웨어 개발자', '기술자', '엔지니어']
        }
        
        # 과정명별 희망업종 매핑 (간단한 버전)
        self.course_industry_mapping = {
            # IT/개발 과정
            '웹': ['IT/웹/통신업', '소프트웨어', '인터넷'],
            '앱': ['IT/웹/통신업', '소프트웨어', '모바일'],
            'Python': ['IT/웹/통신업', '소프트웨어', 'AI/빅데이터'],
            'Java': ['IT/웹/통신업', '소프트웨어', 'IT서비스'],
            'AI': ['IT/웹/통신업', '소프트웨어', 'AI/빅데이터', '연구개발'],
            '데이터': ['IT/웹/통신업', '소프트웨어', 'AI/빅데이터', '금융'],
            'DevOps': ['IT/웹/통신업', '소프트웨어', '클라우드'],
            '보안': ['IT/웹/통신업', '소프트웨어', '보안', '금융'],
            '게임': ['게임', '소프트웨어', '엔터테인먼트'],
            'UI': ['IT/웹/통신업', '소프트웨어', '디자인'],
            '클라우드': ['IT/웹/통신업', '소프트웨어', '클라우드'],
            
            # 기계/전기 과정
            '기계': ['제조업', '자동차', '조선', '철강'],
            '전기': ['전기/가스업', '제조업', '건설업'],
            '전자': ['전기/가스업', '제조업', 'IT/웹/통신업'],
            '자동화': ['제조업', 'IT/웹/통신업', '자동차'],
            '건설': ['건설업', '토목', '건축'],
            '화학': ['화학', '제조업', '석유/화학'],
            
            # 기본 매핑
            'default': ['IT/웹/통신업', '제조업', '서비스업']
        }
        
        # 상담내용 템플릿 (간단한 버전)
        self.counseling_templates = [
            "{course} 과정을 수료하여 {job} 분야로 진출하고 싶습니다. {skill} 스킬을 습득했으며, {industry} 업계에서 일하고 싶습니다.",
            "{course}에서 배운 {skill}을 활용하여 {job}로 취업하고 싶습니다. {location} 지역을 선호하며 {salary}만원 수준의 보수를 희망합니다.",
            "{course} 수료 후 {job} 분야에서 성장하고 싶습니다. 실무 경험을 쌓아 {industry} 업계의 전문가가 되고 싶습니다."
        ]
    
    def load_current_data(self):
        """현재 학생 데이터 로드"""
        try:
            query = "SELECT * FROM merged_trainee_data"
            self.students_df = pd.read_sql(query, self.engine)
            self.logger.info(f"✅ 현재 학생 데이터 로드 완료: {len(self.students_df)}명")
            return True
        except Exception as e:
            self.logger.error(f"❌ 데이터 로드 오류: {e}")
            return False
    
    def get_job_by_course(self, course_name):
        """과정명에 따른 희망직종 반환"""
        if pd.isna(course_name):
            return random.choice(self.course_job_mapping['default'])
        
        course_name = str(course_name).lower()
        
        for keyword, jobs in self.course_job_mapping.items():
            if keyword.lower() in course_name:
                return random.choice(jobs)
        
        return random.choice(self.course_job_mapping['default'])
    
    def get_industry_by_course(self, course_name):
        """과정명에 따른 희망업종 반환"""
        if pd.isna(course_name):
            return random.choice(self.course_industry_mapping['default'])
        
        course_name = str(course_name).lower()
        
        for keyword, industries in self.course_industry_mapping.items():
            if keyword.lower() in course_name:
                return random.choice(industries)
        
        return random.choice(self.course_industry_mapping['default'])
    
    def generate_counseling_content(self, student_row):
        """학생별 맞춤 상담내용 생성 (간단한 버전)"""
        course = student_row.get('과정명', 'IT 과정')
        job = student_row.get('희망직종', '개발자')
        industry = student_row.get('희망업종', 'IT/웹/통신업')
        location = student_row.get('희망지역', '서울')
        salary = student_row.get('희망보수', '3000')
        
        # 간단한 기술 스택 매핑
        skill_mapping = {
            '웹': ['HTML/CSS', 'JavaScript', 'React', 'Node.js'],
            '앱': ['Java', 'Kotlin', 'Swift', 'React Native'],
            'Python': ['Python', 'Django', '데이터 분석'],
            'Java': ['Java', 'Spring', 'JPA'],
            'AI': ['Python', '머신러닝', '딥러닝'],
            '데이터': ['Python', 'SQL', '데이터 분석'],
            'DevOps': ['Docker', 'AWS', 'Linux'],
            '게임': ['Unity', 'C#', '게임 엔진'],
            'UI': ['Figma', 'Adobe XD', '디자인'],
            '클라우드': ['AWS', 'Azure', '클라우드'],
            '기계': ['CAD', '기계설계', '기계제작'],
            '전기': ['전기설비', '전기제어', 'PLC'],
            '전자': ['전자회로', '마이크로프로세서', '임베디드'],
            '자동화': ['PLC', '자동화', '제어'],
            '건설': ['건축설계', '토목', '건설'],
            '화학': ['화학공정', '품질관리', '화학분석'],
            'default': ['전문기술', '문제해결', '팀워크']
        }
        
        # 기술 스택 선택
        skills = skill_mapping.get('default', [])
        for keyword, skill_list in skill_mapping.items():
            if keyword.lower() in str(course).lower():
                skills = skill_list
                break
        
        skill = ', '.join(random.sample(skills, min(2, len(skills))))
        
        # 간단한 상담내용 생성
        template = random.choice(self.counseling_templates)
        counseling_content = template.format(
            course=course,
            job=job,
            skill=skill,
            industry=industry,
            location=location,
            salary=salary
        )
        
        return counseling_content
    
    def update_student_data(self):
        """학생 데이터 업데이트"""
        if not self.load_current_data():
            return False
        
        updated_students = []
        
        for idx, student in self.students_df.iterrows():
            self.logger.info(f"🔄 {student['이름']} 학생 데이터 업데이트 중...")
            
            # 1. 희망직종 업데이트 (과정명 기반)
            course_name = student.get('과정명', '')
            new_job = self.get_job_by_course(course_name)
            
            # 2. 희망업종 업데이트 (과정명 기반)
            new_industry = self.get_industry_by_course(course_name)
            
            # 3. 상담내용 생성
            counseling_content = self.generate_counseling_content(student)
            
            # 4. 업데이트된 데이터 생성
            updated_student = student.copy()
            updated_student['희망직종'] = new_job
            updated_student['희망업종'] = new_industry
            updated_student['상담내용'] = counseling_content
            updated_student['업데이트일시'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            updated_students.append(updated_student)
        
        # 업데이트된 데이터프레임 생성
        self.updated_df = pd.DataFrame(updated_students)
        
        self.logger.info(f"✅ 학생 데이터 업데이트 완료: {len(self.updated_df)}명")
        return True
    
    def save_to_database(self):
        """업데이트된 데이터를 데이터베이스에 저장"""
        try:
            # 기존 테이블 백업
            backup_query = text("CREATE TABLE IF NOT EXISTS merged_trainee_data_backup AS SELECT * FROM merged_trainee_data")
            with self.engine.connect() as conn:
                conn.execute(backup_query)
                conn.commit()
            
            # 상담내용 컬럼 추가 (없는 경우)
            try:
                alter_query = text("ALTER TABLE merged_trainee_data ADD COLUMN 상담내용 TEXT")
                with self.engine.connect() as conn:
                    conn.execute(alter_query)
                    conn.commit()
            except:
                pass  # 이미 존재하는 경우
            
            try:
                alter_query2 = text("ALTER TABLE merged_trainee_data ADD COLUMN 업데이트일시 DATETIME")
                with self.engine.connect() as conn:
                    conn.execute(alter_query2)
                    conn.commit()
            except:
                pass  # 이미 존재하는 경우
            
            # 데이터 업데이트
            for idx, row in self.updated_df.iterrows():
                update_query = text("""
                UPDATE merged_trainee_data 
                SET 희망직종 = :희망직종, 희망업종 = :희망업종, 상담내용 = :상담내용, 업데이트일시 = :업데이트일시
                WHERE 학번 = :학번
                """)
                with self.engine.connect() as conn:
                    conn.execute(update_query, {
                        '희망직종': row['희망직종'],
                        '희망업종': row['희망업종'],
                        '상담내용': row['상담내용'],
                        '업데이트일시': row['업데이트일시'],
                        '학번': row['학번']
                    })
                    conn.commit()
            
            self.logger.info("✅ 데이터베이스 업데이트 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 데이터베이스 저장 오류: {e}")
            return False
    
    def generate_summary_report(self):
        """업데이트 결과 요약 리포트 생성"""
        if not hasattr(self, 'updated_df'):
            return
        
        # 과정별 희망직종 분포
        course_job_dist = self.updated_df.groupby(['과정명', '희망직종']).size().reset_index(name='count')
        
        # 과정별 희망업종 분포
        course_industry_dist = self.updated_df.groupby(['과정명', '희망업종']).size().reset_index(name='count')
        
        # 상담내용 길이 통계
        counseling_lengths = self.updated_df['상담내용'].str.len()
        
        report = f"""
📊 학생 데이터 업데이트 완료 리포트
=====================================
📈 전체 학생 수: {len(self.updated_df)}명
📝 평균 상담내용 길이: {counseling_lengths.mean():.0f}자
📏 상담내용 길이 범위: {counseling_lengths.min():.0f}자 ~ {counseling_lengths.max():.0f}자

🎯 과정별 희망직종 분포:
{course_job_dist.to_string(index=False)}

🏢 과정별 희망업종 분포:
{course_industry_dist.to_string(index=False)}

✅ 업데이트 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        self.logger.info(report)
        return report

def main():
    """메인 실행 함수"""
    logging.info("🚀 학생 데이터 업데이트 시작")
    
    updater = StudentDataUpdater()
    
    # 1. 학생 데이터 업데이트
    if updater.update_student_data():
        # 2. 데이터베이스에 저장
        if updater.save_to_database():
            # 3. 요약 리포트 생성
            report = updater.generate_summary_report()
            print(report)
            logging.info("🎉 학생 데이터 업데이트 완료!")
        else:
            logging.error("❌ 데이터베이스 저장 실패")
    else:
        logging.error("❌ 학생 데이터 업데이트 실패")

if __name__ == "__main__":
    main() 