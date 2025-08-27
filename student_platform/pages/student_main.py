import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import random

# 페이지 설정
st.set_page_config(
    page_title="학생 메인 페이지",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일링
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
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
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
    }
    
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
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
    
    .logout-btn {
        background: #dc3545;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .logout-btn:hover {
        background: #c82333;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# CSV 파일에서 학생 추천 데이터 가져오기
@st.cache_data(ttl=300)
def get_student_recommendations(student_id):
    try:
        # CSV 파일에서 해당 학생의 추천 결과 가져오기
        df = pd.read_csv('student_recommendations.csv')
        student_data = df[df['student_id'] == student_id].sort_values('recommendation_rank')
        return student_data
    except Exception as e:
        st.error(f"데이터베이스 연결 오류: {e}")
        return pd.DataFrame()

# 가상의 출석 데이터 생성
def generate_attendance_data():
    total_days = 120  # 총 수업일
    present_days = random.randint(100, 115)  # 출석일
    absent_days = total_days - present_days  # 결석일
    
    data = {
        '상태': ['출석', '결석'],
        '일수': [present_days, absent_days],
        '색상': ['#28a745', '#dc3545']
    }
    return pd.DataFrame(data)

# 가상의 시험 점수 데이터 생성
def generate_exam_scores():
    subjects = ['전문기초', '전문실무', '프로젝트', '포트폴리오', '최종평가']
    scores = [random.randint(70, 95) for _ in range(len(subjects))]
    
    data = {
        '과목': subjects,
        '점수': scores
    }
    return pd.DataFrame(data)

# 세션 상태 확인
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("로그인이 필요합니다.")
    st.stop()

def main():
    student_id = st.session_state.student_id
    student_name = st.session_state.student_name
    
    # 메인 헤더
    st.markdown(f"""
    <div class="main-header">
        <h1>🎓 {student_name}님의 학습 대시보드</h1>
        <p>학번: {student_id} | 오늘 날짜: {datetime.now().strftime('%Y년 %m월 %d일')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 로그아웃 버튼 (사이드바)
    with st.sidebar:
        st.markdown("### 👤 사용자 정보")
        st.info(f"**이름**: {student_name}\n\n**학번**: {student_id}")
        
        if st.button("로그아웃", key="logout"):
            st.session_state.logged_in = False
            st.session_state.student_id = None
            st.session_state.student_name = None
            st.rerun()
    
    # 1. 주요 지표 (메트릭 카드)
    st.markdown("### 📊 주요 지표")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        attendance_data = generate_attendance_data()
        attendance_rate = (attendance_data.iloc[0]['일수'] / attendance_data['일수'].sum()) * 100
        st.markdown(f"""
        <div class="metric-card">
            <h3>출석률</h3>
            <h2>{attendance_rate:.1f}%</h2>
            <p>총 {attendance_data['일수'].sum()}일 중 {attendance_data.iloc[0]['일수']}일 출석</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        exam_data = generate_exam_scores()
        avg_score = exam_data['점수'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <h3>평균 점수</h3>
            <h2>{avg_score:.1f}점</h2>
            <p>전체 과목 평균</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        recommendations = get_student_recommendations(student_id)
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
        fig_pie = px.pie(
            attendance_data, 
            values='일수', 
            names='상태',
            color='상태',
            color_discrete_map={'출석': '#28a745', '결석': '#dc3545'},
            title="출석률 분포"
        )
        fig_pie.update_traces(hole=.5, textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px;">
            <h4>📋 출석 통계</h4>
            <ul style="text-align: left;">
                <li><strong>총 수업일:</strong> 120일</li>
                <li><strong>출석일:</strong> 108일</li>
                <li><strong>결석일:</strong> 12일</li>
                <li><strong>출석률:</strong> 90.0%</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # 3. 시험 점수 (라인 차트)
    st.markdown("### 📈 시험 점수 현황")
    
    fig_line = px.line(
        exam_data, 
        x='과목', 
        y='점수',
        markers=True,
        title="과목별 시험 점수",
        labels={'점수': '점수', '과목': '과목명'}
    )
    fig_line.update_traces(line=dict(width=3), marker=dict(size=8))
    fig_line.update_layout(height=400, xaxis_tickangle=-45)
    st.plotly_chart(fig_line, use_container_width=True)
    
    # 4. 추천 취업처 목록
    st.markdown("### 🎯 맞춤 추천 취업처")
    
    if not recommendations.empty:
        # 상위 5개 추천 기업만 표시
        top_recommendations = recommendations.head(5)
        
        for idx, row in top_recommendations.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="job-card">
                                         <div style="display: flex; justify-content: space-between; align-items: center;">
                         <div>
                             <h4>🏢 {row.get('recommended_company', '기업명')}</h4>
                             <p><strong>직무:</strong> {row.get('recommended_title', '직무명')}</p>
                             <p><strong>지역:</strong> {row.get('recommended_location', '지역')}</p>
                             <p><strong>산업:</strong> {row.get('recommended_industry', '산업')}</p>
                         </div>
                         <div style="text-align: right;">
                             <h3 style="color: #667eea;">#{row.get('recommendation_rank', idx+1)}</h3>
                             <p style="color: #28a745; font-weight: bold;">
                                 적합도: {row.get('final_score', 0.85):.3f}
                             </p>
                         </div>
                     </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        # 가상의 추천 데이터 생성
        virtual_jobs = [
            {
                'company': '삼성전자',
                'job': '소프트웨어 개발자',
                'location': '서울 강남구',
                'salary': '연 4,000만원',
                'score': 0.92
            },
            {
                'company': 'LG전자',
                'job': 'AI 엔지니어',
                'location': '서울 영등포구',
                'salary': '연 3,800만원',
                'score': 0.88
            },
            {
                'company': '네이버',
                'job': '웹 개발자',
                'location': '경기 성남시',
                'salary': '연 4,500만원',
                'score': 0.85
            },
            {
                'company': '카카오',
                'job': '백엔드 개발자',
                'location': '제주 제주시',
                'salary': '연 4,200만원',
                'score': 0.83
            },
            {
                'company': '쿠팡',
                'job': '데이터 엔지니어',
                'location': '서울 송파구',
                'salary': '연 4,300만원',
                'score': 0.81
            }
        ]
        
        for idx, job in enumerate(virtual_jobs, 1):
            with st.container():
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
