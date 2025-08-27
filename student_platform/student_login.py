import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import hashlib

# 페이지 설정
st.set_page_config(
    page_title="학생 로그인",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS 스타일링
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .login-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .login-form {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    }
    
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e9ecef;
        padding: 0.75rem;
        font-size: 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
    }
    
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
    
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# CSV 파일에서 학생 데이터 가져오기
@st.cache_data(ttl=300)
def get_student_data():
    try:
        # CSV 파일에서 학생 정보 가져오기
        df = pd.read_csv('student_recommendations.csv')
        # student_id를 기준으로 unique한 학생 정보 추출
        student_info = df[['student_id']].drop_duplicates()
        # student_id를 학번으로, 임시로 이름 생성 (실제로는 이름 정보가 없으므로)
        student_info['이름'] = student_info['student_id'].apply(lambda x: f"학생_{x[-4:]}")
        return student_info
    except Exception as e:
        st.error(f"데이터베이스 연결 오류: {e}")
        return pd.DataFrame()

# 학생 추천 데이터 가져오기 함수
@st.cache_data(ttl=300)
def get_student_recommendations(student_id):
    try:
        engine = create_engine(
            'mysql+pymysql://root:15861@127.0.0.1:3306/job_recoder?charset=utf8mb4'
        )
        
        # 해당 학생의 추천 결과 가져오기 (improved_recommendations 테이블만 사용)
        query = f"""
        SELECT * FROM improved_recommendations 
        WHERE trainee_id = {student_id}
        ORDER BY rank
        LIMIT 5
        """
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"추천 데이터 로드 오류: {e}")
        return pd.DataFrame()

# 세션 상태 초기화
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'student_id' not in st.session_state:
    st.session_state.student_id = None
if 'student_name' not in st.session_state:
    st.session_state.student_name = None

def main():
    # 메인 헤더
    st.markdown("""
    <div class="login-container">
        <h1>🎓 학생 로그인</h1>
        <p>대한상공회의소 취업지원 플랫폼</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 로그인되지 않은 경우 로그인 폼 표시
    if not st.session_state.logged_in:
        st.markdown("""
        <div class="login-form">
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("### 🔐 로그인")
            
            # 학번 입력
            student_id = st.text_input(
                "학번",
                placeholder="학번을 입력하세요",
                help="등록된 학번을 입력해주세요"
            )
            
            # 비밀번호 입력
            password = st.text_input(
                "비밀번호",
                type="password",
                placeholder="비밀번호를 입력하세요",
                help="기본 비밀번호: 0000"
            )
            
            # 로그인 버튼
            submit_button = st.form_submit_button("로그인", use_container_width=True)
            
            if submit_button:
                if student_id and password:
                    # DB에서 학번 확인
                    student_data = get_student_data()
                    
                    if not student_data.empty:
                        # 학번이 존재하는지 확인 (데이터 타입 맞춤)
                        try:
                            # 입력된 학번을 정수로 변환
                            student_id_int = int(student_id)
                            student_info = student_data[student_data['학번'] == student_id_int]
                        except ValueError:
                            # 학번이 숫자가 아닌 경우 빈 결과
                            student_info = pd.DataFrame()
                        
                        if not student_info.empty and password == "0000":
                            # 로그인 성공
                            st.session_state.logged_in = True
                            st.session_state.student_id = student_id
                            st.session_state.student_name = student_info.iloc[0]['이름']
                            
                            st.markdown("""
                            <div class="success-message">
                                ✅ 로그인 성공! 잠시 후 메인 페이지로 이동합니다.
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.rerun()
                        else:
                            st.markdown("""
                            <div class="error-message">
                                ❌ 학번 또는 비밀번호가 올바르지 않습니다.
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="error-message">
                            ❌ 데이터베이스 연결에 실패했습니다.
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="error-message">
                        ❌ 학번과 비밀번호를 모두 입력해주세요.
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 도움말
        st.markdown("""
        <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin-top: 2rem;">
            <h4>💡 로그인 안내</h4>
            <ul style="text-align: left; margin: 0; padding-left: 1.5rem;">
                <li><strong>아이디:</strong> 등록된 학번</li>
                <li><strong>비밀번호:</strong> 0000 (기본값)</li>
                <li>로그인 후 취업 추천 서비스를 이용할 수 있습니다.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # 로그인된 경우 메인 페이지 표시
    else:
        # 메인 페이지 내용을 여기에 직접 포함
        import plotly.express as px
        import plotly.graph_objects as go
        import numpy as np
        from datetime import datetime, timedelta
        import random
        
        # 메인 페이지 CSS 추가
        st.markdown("""
        <style>
            .main-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2rem;
                border-radius: 20px;
                color: white;
                text-align: center;
                margin-bottom: 2rem;
                box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
            }
            
                         .metric-card {
                 background: white;
                 padding: 1.2rem;
                 border-radius: 15px;
                 box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                 border: 1px solid rgba(255, 255, 255, 0.2);
                 transition: all 0.3s ease;
                 min-width: 180px;
             }
             
             .metric-card h3 {
                 font-size: 0.9rem;
                 margin-bottom: 0.5rem;
                 color: #495057;
                 white-space: nowrap;
                 overflow: hidden;
                 text-overflow: ellipsis;
             }
             
             .metric-card h2 {
                 font-size: 2rem;
                 margin: 0.3rem 0;
                 color: #667eea;
                 font-weight: 700;
             }
             
             .metric-card p {
                 font-size: 0.75rem;
                 color: #6c757d;
                 margin: 0;
                 line-height: 1.2;
                 white-space: nowrap;
                 overflow: hidden;
                 text-overflow: ellipsis;
             }
            
            .metric-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
            }
            
            .job-card {
                background: white;
                padding: 1.5rem;
                border-radius: 15px;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
                border-left: 4px solid #667eea;
                margin-bottom: 1rem;
                transition: all 0.3s ease;
            }
            
            .job-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
            }
        </style>
        """, unsafe_allow_html=True)
        
        # 메인 헤더
        st.markdown(f"""
        <div class="main-header">
            <h1>🎓 {st.session_state.student_name}님의 학습 대시보드</h1>
            <p>학번: {st.session_state.student_id} | 오늘 날짜: {datetime.now().strftime('%Y년 %m월 %d일')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 로그아웃 버튼 (사이드바)
        with st.sidebar:
            st.markdown("### 👤 사용자 정보")
            st.info(f"**이름**: {st.session_state.student_name}\n\n**학번**: {st.session_state.student_id}")
            
            if st.button("로그아웃", key="logout"):
                st.session_state.logged_in = False
                st.session_state.student_id = None
                st.session_state.student_name = None
                st.rerun()
        
        # 1. 주요 지표 (메트릭 카드)
        st.markdown("### 📊 주요 지표")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # 가상의 출석 데이터
            total_days = 120
            present_days = random.randint(100, 115)
            attendance_rate = (present_days / total_days) * 100
            st.markdown(f"""
            <div class="metric-card">
                <h3>출석률</h3>
                <h2>{attendance_rate:.1f}%</h2>
                <p>총 {total_days}일 중 {present_days}일 출석</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # 가상의 시험 점수
            subjects = ['전문기초', '전문실무', '프로젝트', '포트폴리오', '최종평가']
            scores = [random.randint(70, 95) for _ in range(len(subjects))]
            avg_score = sum(scores) / len(scores)
            st.markdown(f"""
            <div class="metric-card">
                <h3>평균 점수</h3>
                <h2>{avg_score:.1f}점</h2>
                <p>전체 과목 평균</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # 추천 기업 수 (실제 데이터 기반)
            recommendations = get_student_recommendations(st.session_state.student_id)
            rec_count = len(recommendations) if not recommendations.empty else 0
            st.markdown(f"""
            <div class="metric-card">
                <h3>추천 기업</h3>
                <h2>{rec_count}개</h2>
                <p>맞춤 추천 기업 수</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3>학습 진행률</h3>
                <h2>85%</h2>
                <p>전체 과정 진행률</p>
            </div>
            """, unsafe_allow_html=True)
        
        # 2. 출석 현황 (파이 차트)
        st.markdown("### 📅 출석 현황")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            attendance_data = pd.DataFrame({
                '상태': ['출석', '결석'],
                '일수': [present_days, total_days - present_days]
            })
            
            fig_pie = px.pie(
                attendance_data, 
                values='일수', 
                names='상태',
                color='상태',
                color_discrete_map={'출석': '#28a745', '결석': '#dc3545'},
                title="출석률 분포"
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px;">
                <h4>📋 출석 통계</h4>
                <ul style="text-align: left;">
                    <li><strong>총 수업일:</strong> {total_days}일</li>
                    <li><strong>출석일:</strong> {present_days}일</li>
                    <li><strong>결석일:</strong> {total_days - present_days}일</li>
                    <li><strong>출석률:</strong> {attendance_rate:.1f}%</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # 3. 시험 점수 (방사형 차트)
        st.markdown("### 📈 시험 점수 현황")
        
        # 방사형 차트 데이터 준비
        fig_radar = go.Figure()
        
        fig_radar.add_trace(go.Scatterpolar(
            r=scores,
            theta=subjects,
            fill='toself',
            name='현재 점수',
            line_color='#667eea',
            fillcolor='rgba(102, 126, 234, 0.3)'
        ))
        
        # 평균 점수 라인 추가
        avg_score = sum(scores) / len(scores)
        fig_radar.add_trace(go.Scatterpolar(
            r=[avg_score] * len(subjects),
            theta=subjects,
            fill='toself',
            name=f'평균 점수 ({avg_score:.1f}점)',
            line_color='#28a745',
            fillcolor='rgba(40, 167, 69, 0.1)',
            line=dict(dash='dash')
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title="과목별 시험 점수",
            height=500
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
        
        # 점수 상세 정보
        col1, col2 = st.columns(2)
        
        with col1:
            # 과목별 점수 리스트 생성
            subject_list = ""
            for subject, score in zip(subjects, scores):
                subject_list += f"<li><strong>{subject}:</strong> {score}점</li>"
            
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px;">
                <h4>📊 과목별 점수</h4>
                <ul style="text-align: left;">
                    {subject_list}
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px;">
                <h4>📈 성적 분석</h4>
                <ul style="text-align: left;">
                    <li><strong>평균 점수:</strong> {avg_score:.1f}점</li>
                    <li><strong>최고 점수:</strong> {max(scores)}점 ({subjects[scores.index(max(scores))]})</li>
                    <li><strong>최저 점수:</strong> {min(scores)}점 ({subjects[scores.index(min(scores))]})</li>
                    <li><strong>점수 범위:</strong> {max(scores) - min(scores)}점</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # 4. 추천 취업처 목록
        st.markdown("### 🎯 맞춤 추천 취업처")
        
        # 추천 데이터 가져오기
        recommendations = get_student_recommendations(st.session_state.student_id)
        
        if not recommendations.empty:
            # 실제 추천 데이터 표시
            for idx, row in recommendations.iterrows():
                with st.container():
                    # 기업명과 직무 정보 (improved_recommendations 테이블에서 직접 가져오기)
                    company_name = row.get('company_name', '기업명 미상')
                    job_title = row.get('job_title', '직무명 미상')
                    location = row.get('location', '지역 미상')
                    salary = row.get('salary', '급여 정보 미상')
                    job_url = row.get('job_url', '')
                    similarity_score = row.get('weighted_similarity_score', 0.0)
                    rank = row.get('rank', idx + 1)
                    
                    # 카드 생성
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"""
                        <div class="job-card">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <h4>🏢 {company_name}</h4>
                                    <p><strong>직무:</strong> {job_title}</p>
                                    <p><strong>지역:</strong> {location}</p>
                                    <p><strong>급여:</strong> {salary}</p>
                                </div>
                                <div style="text-align: right;">
                                    <h3 style="color: #667eea;">#{rank}</h3>
                                    <p style="color: #28a745; font-weight: bold;">
                                        적합도: {similarity_score:.2f}
                                    </p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        if job_url and job_url != '':
                            st.markdown(f"""
                            <div style="margin-top: 1rem;">
                                <a href="{job_url}" target="_blank" style="text-decoration: none;">
                                    <button style="
                                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                        color: white;
                                        border: none;
                                        border-radius: 10px;
                                        padding: 0.5rem 1rem;
                                        font-weight: 600;
                                        cursor: pointer;
                                        transition: all 0.3s ease;
                                    ">
                                        🔗 지원하기
                                    </button>
                                </a>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div style="margin-top: 1rem;">
                                <button style="
                                    background: #6c757d;
                                    color: white;
                                    border: none;
                                    border-radius: 10px;
                                    padding: 0.5rem 1rem;
                                    font-weight: 600;
                                    cursor: not-allowed;
                                " disabled>
                                    링크 없음
                                </button>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            # DB에 데이터가 없는 경우 가상 데이터 표시
            st.info("현재 추천 데이터가 없습니다. 가상의 추천 기업을 보여드립니다.")
            
            virtual_jobs = [
                {
                    'company': '삼성전자',
                    'job': '소프트웨어 개발자',
                    'location': '서울 강남구',
                    'salary': '연 4,000만원',
                    'score': 0.92,
                    'url': 'https://www.samsung.com/careers'
                },
                {
                    'company': 'LG전자',
                    'job': 'AI 엔지니어',
                    'location': '서울 영등포구',
                    'salary': '연 3,800만원',
                    'score': 0.88,
                    'url': 'https://www.lg.com/global/careers'
                },
                {
                    'company': '네이버',
                    'job': '웹 개발자',
                    'location': '경기 성남시',
                    'salary': '연 4,500만원',
                    'score': 0.85,
                    'url': 'https://recruit.navercorp.com'
                },
                {
                    'company': '카카오',
                    'job': '백엔드 개발자',
                    'location': '제주 제주시',
                    'salary': '연 4,200만원',
                    'score': 0.83,
                    'url': 'https://careers.kakao.com'
                },
                {
                    'company': '쿠팡',
                    'job': '데이터 엔지니어',
                    'location': '서울 송파구',
                    'salary': '연 4,300만원',
                    'score': 0.81,
                    'url': 'https://careers.coupang.com'
                }
            ]
            
            for idx, job in enumerate(virtual_jobs, 1):
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"""
                        <div class="job-card">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <h4>🏢 {job['company']}</h4>
                                    <p><strong>직무:</strong> {job['job']}</p>
                                    <p><strong>지역:</strong> {job['location']}</p>
                                    <p><strong>급여:</strong> {job['salary']}</p>
                                </div>
                                <div style="text-align: right;">
                                    <h3 style="color: #667eea;">#{idx}</h3>
                                    <p style="color: #28a745; font-weight: bold;">
                                        적합도: {job['score']:.2f}
                                    </p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div style="margin-top: 1rem;">
                            <a href="{job['url']}" target="_blank" style="text-decoration: none;">
                                <button style="
                                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                    color: white;
                                    border: none;
                                    border-radius: 10px;
                                    padding: 0.5rem 1rem;
                                    font-weight: 600;
                                    cursor: pointer;
                                    transition: all 0.3s ease;
                                ">
                                    🔗 지원하기
                                </button>
                            </a>
                        </div>
                        """, unsafe_allow_html=True)
        
        # 5. 추가 정보
        st.markdown("### 📚 학습 현황")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px;">
                <h4>🎯 학습 목표</h4>
                <ul style="text-align: left;">
                    <li>프로그래밍 언어 마스터</li>
                    <li>프로젝트 포트폴리오 완성</li>
                    <li>자격증 취득 (정보처리기사)</li>
                    <li>취업 준비 완료</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px;">
                <h4>📅 다음 일정</h4>
                <ul style="text-align: left;">
                    <li>내일: 프로젝트 발표</li>
                    <li>다음주: 기업 설명회</li>
                    <li>다음달: 최종 평가</li>
                    <li>2개월 후: 수료식</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
