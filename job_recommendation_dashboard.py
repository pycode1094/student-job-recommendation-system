import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import numpy as np
from datetime import datetime
import plotly.figure_factory as ff
from collections import Counter
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64

# 페이지 설정
st.set_page_config(
    page_title="AI Job Recommender",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)



# 모던한 CSS 스타일링
st.markdown("""
<style>
    /* 전체 폰트 설정 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* 메인 헤더 */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        opacity: 0.3;
    }
    
    .main-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        position: relative;
        z-index: 1;
    }
    
    /* 메트릭 카드 */
    .metric-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    .metric-card h3 {
        color: #6c757d;
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    
    .metric-card h2 {
        color: #2c3e50;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    
    /* 섹션 헤더 */
    .section-header {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem 2rem;
        border-radius: 15px;
        border-left: 5px solid #667eea;
        margin: 2rem 0 1rem 0;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
    }
    
    .section-header h2 {
        color: #2c3e50;
        font-size: 1.5rem;
        font-weight: 600;
        margin: 0;
    }
    
    /* 사이드바 스타일링 */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* 버튼 스타일링 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 25px;
        border: none;
        color: white;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* 셀렉트박스 스타일링 */
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 2px solid #e9ecef;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* 멀티셀렉트 스타일링 */
    .stMultiSelect > div > div {
        border-radius: 10px;
        border: 2px solid #e9ecef;
        transition: all 0.3s ease;
    }
    
    .stMultiSelect > div > div:hover {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* 익스팬더 스타일링 */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 10px;
        border: 1px solid #dee2e6;
        padding: 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
        transform: translateX(5px);
    }
    
    /* 데이터프레임 스타일링 */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* 푸터 */
    .footer {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-top: 3rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    }
    
    /* 스크롤바 스타일링 */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* 애니메이션 */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .metric-card, .section-header {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* 반응형 디자인 */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .metric-card {
            padding: 1.5rem;
        }
        
        .metric-card h2 {
            font-size: 2rem;
        }
    }
    
    /* 홈 카드 스타일 */
    .home-card {
        background: white;
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        cursor: pointer;
        text-align: center;
        height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    .home-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
    }
    
    .home-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    .home-card h3 {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #2c3e50;
    }
    
    .home-card p {
        font-size: 1rem;
        color: #7f8c8d;
        margin: 0;
    }
    
    .home-card .icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 홈 화면 함수
def show_home_page():
    st.markdown("""
    <div class="main-header">
        <h1>🎯 AI Job Recommender</h1>
        <p>SBERT 기반 맞춤형 취업 추천 시스템</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem;">
        <h2 style="color: #2c3e50; font-weight: 600; margin-bottom: 1rem;">📊 대시보드 메뉴</h2>
        <p style="color: #7f8c8d; font-size: 1.1rem;">원하시는 메뉴를 선택하세요</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 2x2 그리드로 카드 배치
    col1, col2 = st.columns(2)
    
    with col1:
        # 전체 통계 카드
        if st.button("", key="stats_card", help="전체 통계 보기"):
            st.session_state.current_page = 'stats'
            st.rerun()
        
        st.markdown("""
        <div class="home-card" onclick="document.querySelector('[data-testid=stButton]').click()">
            <div class="icon">📈</div>
            <h3>전체 통계</h3>
            <p>전체 훈련생 및 채용 현황 통계</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 훈련생 카드
        if st.button("", key="trainee_card", help="훈련생 정보 보기"):
            st.session_state.current_page = 'trainee'
            st.rerun()
        
        st.markdown("""
        <div class="home-card" onclick="document.querySelector('[data-testid=stButton]').click()">
            <div class="icon">👥</div>
            <h3>훈련생</h3>
            <p>개별 훈련생 정보 및 맞춤형 추천</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # 채용정보 카드
        if st.button("", key="job_card", help="채용정보 검색 보기"):
            st.session_state.current_page = 'job'
            st.rerun()
        
        st.markdown("""
        <div class="home-card" onclick="document.querySelector('[data-testid=stButton]').click()">
            <div class="icon">💼</div>
            <h3>채용정보</h3>
            <p>채용정보 검색 및 필터링</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 기타 통계 카드
        if st.button("", key="other_card", help="기타 통계 보기"):
            st.session_state.current_page = 'other'
            st.rerun()
        
        st.markdown("""
        <div class="home-card" onclick="document.querySelector('[data-testid=stButton]').click()">
            <div class="icon">📊</div>
            <h3>기타 통계</h3>
            <p>산업현황, 워드클라우드, 상세분석</p>
        </div>
        """, unsafe_allow_html=True)

# 데이터베이스 연결
def clean_location(location):
    """지역명에서 HTML 엔티티 제거"""
    if pd.isna(location):
        return location
    return str(location).replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&')

def clean_job_type(job_type):
    """고용형태 간소화"""
    if pd.isna(job_type):
        return job_type
    
    job_type_str = str(job_type).lower()
    
    if '정규직' in job_type_str:
        return '정규직'
    elif '계약직' in job_type_str:
        return '계약직'
    elif '인턴' in job_type_str or '인턴십' in job_type_str:
        return '인턴'
    elif '파트타임' in job_type_str or '알바' in job_type_str or '시간제' in job_type_str:
        return '파트타임'
    elif '프리랜서' in job_type_str or '자유계약' in job_type_str:
        return '프리랜서'
    elif '단기' in job_type_str:
        return '단기계약'
    elif '장기' in job_type_str:
        return '장기계약'
    else:
        return job_type

@st.cache_data(ttl=300)  # 5분마다 캐시 갱신
def load_data():
    try:
        # 로컬 환경에서는 기본 연결 정보 사용
        engine = create_engine(
            'mysql+pymysql://root:15861@127.0.0.1:3306/job_recoder?charset=utf8mb4'
        )
        
        # 개선된 가중치 기반 추천 결과 로드
        recommendations_query = """
        SELECT * FROM improved_recommendations 
        ORDER BY trainee_name, rank
        """
        recommendations_df = pd.read_sql(recommendations_query, engine)
        
        # 훈련생 데이터 로드
        trainees_query = "SELECT * FROM merged_trainee_data"
        trainees_df = pd.read_sql(trainees_query, engine)
        
        # 채용 데이터 로드
        jobs_query = "SELECT * FROM enhanced_job_postings WHERE active = 1"
        jobs_df = pd.read_sql(jobs_query, engine)
        
        # 데이터 전처리
        if not jobs_df.empty:
            jobs_df['location'] = jobs_df['location'].apply(clean_location)
            jobs_df['job_type'] = jobs_df['job_type'].apply(clean_job_type)
        
        return recommendations_df, trainees_df, jobs_df
    except Exception as e:
        st.error(f"데이터베이스 연결 오류: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# 데이터 로드
with st.spinner("🔄 데이터를 불러오는 중..."):
    recommendations_df, trainees_df, jobs_df = load_data()

# 메인 헤더
st.markdown("""
<div class="main-header">
    <h1>🎯 대한상공회의소 리코더 프로젝트</h1>
    <p>취업지원 DB구축 및 데이터활용 AI 추천시스템</p>
</div>
""", unsafe_allow_html=True)

# 사이드바
st.sidebar.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 15px; color: white; margin-bottom: 1rem;">
    <h3>⚙️ 설정</h3>
</div>
""", unsafe_allow_html=True)

# 실시간 업데이트 시간
st.sidebar.markdown(f"""
<div style="background: white; padding: 1rem; border-radius: 10px; border: 1px solid #e9ecef; margin-bottom: 1rem;">
    <p style="margin: 0; color: #6c757d; font-size: 0.9rem;">🕒 마지막 업데이트</p>
    <p style="margin: 0; color: #2c3e50; font-weight: 600;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
</div>
""", unsafe_allow_html=True)

# 1. 전체 통계 대시보드
st.markdown("""
<div class="section-header">
    <h2>📊 전체 통계</h2>
</div>
""", unsafe_allow_html=True)

# 메트릭 카드들
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h3>총 추천 개수</h3>
        <h2>{len(recommendations_df):,}</h2>
    </div>
    """, unsafe_allow_html=True)
    
with col2:
    st.markdown(f"""
    <div class="metric-card">
        <h3>훈련생 수</h3>
        <h2>{recommendations_df['trainee_name'].nunique()}</h2>
    </div>
    """, unsafe_allow_html=True)
    
with col3:
    avg_similarity = recommendations_df['weighted_similarity_score'].mean()
    st.markdown(f"""
    <div class="metric-card">
        <h3>평균 가중치 점수</h3>
        <h2>{avg_similarity:.3f}</h2>
    </div>
    """, unsafe_allow_html=True)
    
with col4:
    max_similarity = recommendations_df['weighted_similarity_score'].max()
    st.markdown(f"""
    <div class="metric-card">
        <h3>최고 가중치 점수</h3>
        <h2>{max_similarity:.3f}</h2>
    </div>
    """, unsafe_allow_html=True)

# 차트 섹션
col1, col2 = st.columns(2)

with col1:
    # 가중치 점수 분포 차트
    fig_similarity = px.histogram(
        recommendations_df, 
        x='weighted_similarity_score',
        nbins=20,
        title="📈 가중치 기반 추천 점수 분포",
        labels={'weighted_similarity_score': '가중치 점수', 'count': '추천 개수'},
        color_discrete_sequence=['#667eea']
    )
    fig_similarity.update_layout(
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title_font_size=16,
        font=dict(family="Inter", size=12),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    fig_similarity.update_xaxes(gridcolor='rgba(0,0,0,0.1)', zeroline=False)
    fig_similarity.update_yaxes(gridcolor='rgba(0,0,0,0.1)', zeroline=False)
    st.plotly_chart(fig_similarity, use_container_width=True)

with col2:
    # 산업별 추천 분포
    industry_counts = recommendations_df['industry'].value_counts().head(10)
    fig_industry = px.bar(
        x=industry_counts.values,
        y=industry_counts.index,
        orientation='h',
        title="🏢 상위 10개 산업별 분포",
        labels={'x': '추천 개수', 'y': '산업'},
        color_discrete_sequence=['#764ba2']
    )
    fig_industry.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title_font_size=16,
        font=dict(family="Inter", size=12),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    fig_industry.update_xaxes(gridcolor='rgba(0,0,0,0.1)', zeroline=False)
    fig_industry.update_yaxes(gridcolor='rgba(0,0,0,0.1)', zeroline=False)
    st.plotly_chart(fig_industry, use_container_width=True)

# 2. 훈련생별 추천 결과
st.markdown("""
<div class="section-header">
    <h2>👥 개인별 추천</h2>
</div>
""", unsafe_allow_html=True)

# 훈련생 선택
selected_trainee = st.selectbox(
    "훈련생을 선택하세요:",
    sorted(recommendations_df['trainee_name'].unique()),
    help="추천 결과를 확인할 훈련생을 선택하세요"
)

if selected_trainee:
    trainee_recommendations = recommendations_df[
        recommendations_df['trainee_name'] == selected_trainee
    ].head(5)  # 상위 5개만 표시
    
    # 훈련생 정보
    trainee_info = trainees_df[trainees_df['이름'] == selected_trainee].iloc[0]
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("""
        <div style="background: white; padding: 0.75rem; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border: 1px solid #e9ecef;">
            <h3 style="color: #2c3e50; margin-bottom: 0.25rem;">👤 훈련생 정보</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # 박스 제목과 내용 사이 여백 추가
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.write(f"**이름**: {trainee_info['이름']}")
        st.write(f"**과정명**: {trainee_info['과정명']}")
        st.write(f"**희망직종**: {trainee_info['희망직종']}")
        st.write(f"**희망업종**: {trainee_info['희망업종']}")
        st.write(f"**희망지역**: {trainee_info['희망지역']}")
        st.write(f"**희망보수**: {trainee_info['희망보수']}만원")
        
        # 최근 상담내용 추가
        if '상담내용' in trainee_info and pd.notna(trainee_info['상담내용']):
            st.markdown("---")
            st.markdown("**💬 최근 상담내용**")
            st.info(trainee_info['상담내용'])
        else:
            st.markdown("---")
            st.markdown("**💬 최근 상담내용**")
            st.warning("상담내용이 없습니다.")
        
        # 여백 추가
        st.markdown("<br>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: white; padding: 0.75rem; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border: 1px solid #e9ecef;">
            <h3 style="color: #2c3e50; margin-bottom: 0.25rem;">🎯 추천 채용</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # 박스 제목과 내용 사이 여백 추가
        st.markdown("<br>", unsafe_allow_html=True)
        
        for idx, row in trainee_recommendations.iterrows():
            similarity_color = "🟢" if row['weighted_similarity_score'] >= 0.8 else "🟡" if row['weighted_similarity_score'] >= 0.6 else "🔴"
            
            with st.expander(f"{similarity_color} {row['rank']}. {row['job_title']} - {row['company_name']} (가중치 점수: {row['weighted_similarity_score']:.3f})"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"**회사**: {row['company_name']}")
                    st.write(f"**직무**: {row['job_title']}")
                    st.write(f"**산업**: {row['industry']}")
                    st.write(f"**지역**: {row['location']}")
                with col_b:
                    st.write(f"**고용형태**: {row['job_type']}")
                    st.write(f"**경력**: {row['experience']}")
                    st.write(f"**학력**: {row['education']}")
                    st.write(f"**급여**: {row['salary']}")
                if row['job_url']:
                    st.link_button("🔗 채용정보 보기", row['job_url'])

        # 여백 추가
        st.markdown("<br>", unsafe_allow_html=True)

# 3. 채용정보 검색
st.markdown("""
<div class="section-header">
    <h2>🔍 채용정보 검색</h2>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    location_filter = st.multiselect(
        "📍 지역 선택",
        sorted(jobs_df['location'].dropna().unique()),
        help="원하는 지역을 선택하세요"
    )

with col2:
    industry_filter = st.multiselect(
        "🏢 산업 선택",
        sorted(jobs_df['industry'].dropna().unique()),
        help="원하는 산업을 선택하세요"
    )

with col3:
    job_type_filter = st.multiselect(
        "💼 고용형태 선택",
        sorted(jobs_df['job_type'].dropna().unique()),
        help="원하는 고용형태를 선택하세요"
    )

# 필터링된 채용정보
filtered_jobs = jobs_df.copy()

if location_filter:
    filtered_jobs = filtered_jobs[filtered_jobs['location'].isin(location_filter)]
if industry_filter:
    filtered_jobs = filtered_jobs[filtered_jobs['industry'].isin(industry_filter)]
if job_type_filter:
    filtered_jobs = filtered_jobs[filtered_jobs['job_type'].isin(job_type_filter)]

st.success(f"**검색 결과**: {len(filtered_jobs)}개 채용정보")

# 페이지네이션 추가
if len(filtered_jobs) > 0:
    # 페이지당 표시할 개수
    items_per_page = 20
    total_pages = (len(filtered_jobs) + items_per_page - 1) // items_per_page
    
    # session_state로 현재 페이지 관리
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    
    current_page = st.session_state.current_page
    
    # 현재 페이지에 해당하는 데이터 추출
    start_idx = (current_page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, len(filtered_jobs))
    
    # 페이지 정보 표시
    st.info(f"📄 **{current_page}페이지** (전체 {len(filtered_jobs)}개 중 {start_idx + 1}-{end_idx}번째)")
    
    # 채용정보 테이블 (클릭 가능한 링크 포함)
    # 사용 가능한 컬럼 확인
    available_columns = ['title', 'company_name', 'industry', 'location', 'job_type', 'salary']
    if 'url' in filtered_jobs.columns:
        available_columns.append('url')
    
    display_jobs = filtered_jobs.iloc[start_idx:end_idx][available_columns].copy()
    
    # 박스 형태로 데이터프레임 표시
    st.markdown("""
    <div style="background: white; padding: 1rem; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border: 1px solid #e9ecef; margin-bottom: 1rem;">
    """, unsafe_allow_html=True)
    
    # url이 있는 경우 링크 컬럼 추가
    if 'url' in filtered_jobs.columns:
        # 링크 컬럼 추가 (URL 직접 사용)
        def create_link_url(row):
            if pd.notna(row['url']) and row['url']:
                return row['url']
            else:
                return None
        
        display_jobs['link'] = display_jobs.apply(create_link_url, axis=1)
        
        # url 컬럼 제거 (표시용이므로)
        display_jobs = display_jobs.drop('url', axis=1)
        
        # Streamlit dataframe의 column_config를 사용하여 링크 기능 구현
        st.dataframe(
            display_jobs,
            use_container_width=True,
            column_config={
                "link": st.column_config.LinkColumn(
                    "링크",
                    help="채용 페이지로 이동",
                    max_chars=10
                )
            }
        )
    else:
        # 일반 데이터프레임으로 표시
        st.dataframe(display_jobs, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)
    
    # 페이지 네비게이션 버튼 (테이블 아래에 배치)
    if total_pages > 1:
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if current_page > 1:
                if st.button("◀️ 이전 페이지", key=f"prev_page_{current_page}", use_container_width=True):
                    st.session_state.current_page = current_page - 1
                    st.rerun()
        
        with col3:
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; background: #f8f9fa; border-radius: 10px; border: 1px solid #dee2e6;">
                <strong>{current_page} / {total_pages}</strong>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            if current_page < total_pages:
                if st.button("다음 페이지 ▶️", key=f"next_page_{current_page}", use_container_width=True):
                    st.session_state.current_page = current_page + 1
                    st.rerun()

# 4. 산업 현황 대시보드
st.markdown("""
<div class="section-header">
    <h2>🏢 산업 현황 대시보드</h2>
</div>
""", unsafe_allow_html=True)

# 사이드바에 산업 현황 필터 추가
st.sidebar.markdown("""
<div style="background: white; padding: 1rem; border-radius: 10px; border: 1px solid #e9ecef; margin-bottom: 1rem;">
    <h4 style="color: #2c3e50; margin-bottom: 0.5rem;">🏢 산업 현황 필터</h4>
</div>
""", unsafe_allow_html=True)

# 지역별 필터
selected_location_industry = st.sidebar.selectbox(
    "📍 지역 선택",
    ["전체"] + sorted(jobs_df['location'].dropna().unique().tolist()),
    help="특정 지역의 산업 현황을 확인하세요"
)

# 산업별 필터
selected_industry_filter = st.sidebar.selectbox(
    "🏭 산업 선택",
    ["전체"] + sorted(jobs_df['industry'].dropna().unique().tolist()),
    help="특정 산업의 현황을 확인하세요"
)

# 필터링된 데이터
filtered_industry_data = jobs_df.copy()
if selected_location_industry != "전체":
    filtered_industry_data = filtered_industry_data[filtered_industry_data['location'] == selected_location_industry]
if selected_industry_filter != "전체":
    filtered_industry_data = filtered_industry_data[filtered_industry_data['industry'] == selected_industry_filter]

# 2행 2열 그래프 배치 - 정렬 개선
col1, col2 = st.columns(2)

with col1:
    # 1. 산업별 채용 건수 (상위 10개)
    industry_counts = filtered_industry_data['industry'].value_counts().head(10)
    fig_industry_count = px.bar(
        x=industry_counts.values,
        y=industry_counts.index,
    orientation='h',
        title="🏭 산업별 채용 건수 (상위 10개)",
        labels={'x': '채용 건수', 'y': '산업'},
    color_discrete_sequence=['#667eea']
)
    fig_industry_count.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
        title_font_size=14,
        font=dict(family="Inter", size=10),
        margin=dict(l=20, r=20, t=40, b=20),
        height=320,
        showlegend=False
    )
    fig_industry_count.update_xaxes(gridcolor='rgba(0,0,0,0.1)', zeroline=False)
    fig_industry_count.update_yaxes(gridcolor='rgba(0,0,0,0.1)', zeroline=False)
    st.plotly_chart(fig_industry_count, use_container_width=True, config={'displayModeBar': False})

with col2:
    # 2. 지역별 채용 분포
    location_counts = filtered_industry_data['location'].value_counts().head(10)
    fig_location_dist = px.pie(
        values=location_counts.values,
        names=location_counts.index,
        title="📍 지역별 채용 분포 (상위 10개)",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_location_dist.update_layout(
        title_font_size=14,
        font=dict(family="Inter", size=10),
        margin=dict(l=20, r=20, t=40, b=20),
        height=320
    )
    st.plotly_chart(fig_location_dist, use_container_width=True, config={'displayModeBar': False})

col3, col4 = st.columns(2)

with col3:
    # 3. 고용형태별 분포
    job_type_counts = filtered_industry_data['job_type'].value_counts()
    fig_job_type = px.bar(
        x=job_type_counts.index,
        y=job_type_counts.values,
        title="💼 고용형태별 분포",
        labels={'x': '고용형태', 'y': '채용 건수'},
        color_discrete_sequence=['#764ba2']
    )
    fig_job_type.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title_font_size=14,
        font=dict(family="Inter", size=10),
        margin=dict(l=20, r=20, t=40, b=20),
        height=320,
        xaxis_tickangle=-45,
        showlegend=False
    )
    fig_job_type.update_xaxes(gridcolor='rgba(0,0,0,0.1)', zeroline=False)
    fig_job_type.update_yaxes(gridcolor='rgba(0,0,0,0.1)', zeroline=False)
    st.plotly_chart(fig_job_type, use_container_width=True, config={'displayModeBar': False})

with col4:
    # 4. 급여 분포 - 개선된 버전
    salary_data = filtered_industry_data['salary'].dropna()
    
    # 급여 데이터가 있는 경우와 없는 경우 모두 동일한 높이로 처리
    if len(salary_data) > 0:
        def categorize_salary(salary):
            try:
                salary_str = str(salary).replace('만원', '').replace(',', '').strip()
                if salary_str == '' or salary_str == 'nan':
                    return '정보 없음'
                salary_num = float(salary_str)
                if salary_num <= 3000:
                    return '3000만원 이하'
                elif salary_num <= 5000:
                    return '3000-5000만원'
                else:
                    return '5000만원 이상'
            except:
                return '정보 없음'
        
        salary_categories = salary_data.apply(categorize_salary)
        salary_dist = salary_categories.value_counts()
        
        # 정보 없음이 너무 많으면 다른 차트로 대체
        if len(salary_dist) == 1 and '정보 없음' in salary_dist.index:
            # 대신 회사 규모별 분포 표시
            company_size_data = filtered_industry_data['company_size'].dropna()
            if len(company_size_data) > 0:
                company_size_counts = company_size_data.value_counts()
                fig_salary = px.pie(
                    values=company_size_counts.values,
                    names=company_size_counts.index,
                    title="🏢 회사 규모별 분포",
                    color_discrete_sequence=['#ff6b6b', '#feca57', '#48dbfb', '#a8e6cf']
                )
            else:
                # 기본 급여 차트 (정보 없음)
                fig_salary = px.pie(
                    values=[1],
                    names=['정보 없음'],
                    title="💰 급여 분포",
                    color_discrete_sequence=['#6c757d']
                )
        else:
            fig_salary = px.pie(
                values=salary_dist.values,
                names=salary_dist.index,
                title="💰 급여 분포",
                color_discrete_sequence=['#ff6b6b', '#feca57', '#48dbfb']
            )
    else:
        # 급여 데이터가 없으면 회사 규모별 분포 표시
        company_size_data = filtered_industry_data['company_size'].dropna()
        if len(company_size_data) > 0:
            company_size_counts = company_size_data.value_counts()
            fig_salary = px.pie(
                values=company_size_counts.values,
                names=company_size_counts.index,
                title="🏢 회사 규모별 분포",
                color_discrete_sequence=['#ff6b6b', '#feca57', '#48dbfb', '#a8e6cf']
            )
        else:
            # 모든 데이터가 없으면 기본 메시지
            fig_salary = px.pie(
                values=[1],
                names=['데이터 없음'],
                title="📊 데이터 현황",
                color_discrete_sequence=['#6c757d']
            )
    
    fig_salary.update_layout(
        title_font_size=14,
        font=dict(family="Inter", size=10),
        margin=dict(l=20, r=20, t=40, b=20),
        height=320
    )
    st.plotly_chart(fig_salary, use_container_width=True, config={'displayModeBar': False})

# 5. 과정별 추천 분석
st.markdown("""
<div class="section-header">
    <h2>📚 과정별 워드 체크</h2>
</div>
""", unsafe_allow_html=True)

# 과정별 워드클라우드 생성
course_analysis = recommendations_df.merge(
    trainees_df[['이름', '과정명']], 
    left_on='trainee_name', 
    right_on='이름'
)

# 과정별로 추천된 직무 키워드 추출
def extract_keywords(text):
    if pd.isna(text):
        return []
    
    # 제거할 조사와 불필요한 단어들
    stop_words = {
        '이', '가', '을', '를', '의', '에', '로', '으로', '와', '과', '도', '만', '은', '는', '이런', '저런', '그런',
        '있', '없', '하', '되', '되다', '하다', '있다', '없다', '되다', '하다', '되', '하', '있', '없',
        '그', '이', '저', '우리', '저희', '너희', '그들', '이들', '저들',
        '때', '곳', '것', '일', '수', '분', '년', '월', '일', '시', '분', '초',
        '등', '등등', '또', '또한', '그리고', '하지만', '그런데', '그러나',
        '많', '적', '크', '작', '좋', '나쁘', '높', '낮', '빠르', '느리',
        '개발', '개발자', '프로그래머', '엔지니어', '디자이너', '매니저', '관리자',
        '회사', '기업', '업체', '사', '주식회사', '유한회사', '협회', '재단',
        '학원', '학교', '대학교', '고등학교', '중학교', '초등학교',
        '과정', '교육', '훈련', '강의', '수업', '학습', '공부',
        '희망', '원하', '하고싶', '되', '되다', '하다', '하', '되',
        '직종', '업종', '직업', '일', '일자리', '취업', '구직', '채용',
        '정규직', '계약직', '인턴', '파트타임', '프리랜서', '단기계약', '장기계약',
        '급여', '연봉', '월급', '봉급', '임금', '보수', '수당', '상여금',
        '지역', '지방', '도시', '시', '군', '구', '동', '읍', '면',
        '산업', '업계', '분야', '영역', '부분', '측면', '관점',
        '기술', '기술력', '능력', '실력', '경험', '경력', '자격', '자격증',
        '프로젝트', '업무', '업무내용', '담당', '담당업무', '업무분야',
        '환경', '조건', '요건', '자격요건', '지원자격', '우대사항',
        '복리후생', '복지', '혜택', '보험', '연금', '휴가', '휴일',
        '근무시간', '근무일', '근무조건', '근무환경', '근무지',
        '성장', '발전', '향상', '개선', '향상', '발전', '성장',
        '미래', '앞으로', '앞', '앞날', '앞으로', '앞으로',
        '현재', '지금', '이제', '지금', '현재', '이제',
        '과거', '이전', '전', '전에', '이전에', '전에',
        '미래', '앞으로', '앞', '앞날', '앞으로', '앞으로',
        '현재', '지금', '이제', '지금', '현재', '이제',
        '과거', '이전', '전', '전에', '이전에', '전에'
    }
    
    # 한글, 영문, 숫자만 추출하고 공백으로 분리
    words = re.findall(r'[가-힣a-zA-Z0-9]+', str(text))
    
    # 필터링: 2글자 이상, 불용어 제거, 명사성 단어만
    filtered_words = []
    for word in words:
        if len(word) >= 2 and word not in stop_words:
            # 한글의 경우 조사가 붙은 형태 제거 (예: 개발자가 -> 개발자)
            if re.match(r'^[가-힣]+', word):
                # 조사 제거
                word = re.sub(r'(이|가|을|를|의|에|로|으로|와|과|도|만|은|는|싶습니다)$', '', word)
                if len(word) >= 2:
                    filtered_words.append(word)
            else:
                filtered_words.append(word)
    
    return filtered_words

# 각 과정별로 학생들이 입력한 희망 직무 키워드 수집
course_keywords = {}
course_counseling = {}

for course in trainees_df['과정명'].unique():
    course_data = trainees_df[trainees_df['과정명'] == course]
    all_keywords = []
    all_counseling = []
    
    # 희망직종에서 키워드 추출
    for job_type in course_data['희망직종'].dropna():
        all_keywords.extend(extract_keywords(job_type))
    
    # 희망업종에서 키워드 추출
    for industry in course_data['희망업종'].dropna():
        all_keywords.extend(extract_keywords(industry))
    
    # 상담내용에서 키워드 추출
    for counseling in course_data['상담내용'].dropna():
        all_keywords.extend(extract_keywords(counseling))
        all_counseling.append(str(counseling))
    
    # 키워드 빈도 계산
    keyword_counts = Counter(all_keywords)
    # 상위 10개 키워드만 선택
    course_keywords[course] = dict(keyword_counts.most_common(10))
    
    # 상담내용 저장
    course_counseling[course] = all_counseling

# 워드클라우드 생성 함수 (WordCloud 라이브러리 사용)
def create_wordcloud(keywords, title, color_scheme):
    if not keywords:
        return go.Figure().add_annotation(
            text="데이터가 없습니다",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="gray")
        )
    
    # matplotlib 한글 폰트 설정
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False
    
    # 한글 폰트 경로 설정
    font_path = 'C:/Windows/Fonts/malgun.ttf'
    
    # WordCloud 생성 (generate_from_frequencies 사용)
    wordcloud = WordCloud(
        font_path=font_path,
        width=400,
        height=300,
        background_color='white',
        max_words=10,
        colormap='viridis',  # 색상 맵
        prefer_horizontal=0.7,  # 가로 배치 비율
        relative_scaling=0.5,  # 빈도에 따른 크기 차이
        min_font_size=10,
        max_font_size=60
    ).generate_from_frequencies(keywords)
    
    # matplotlib으로 워드클라우드 생성
    plt.figure(figsize=(8, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(title, fontsize=14, pad=20)
    
    # 이미지를 base64로 인코딩
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150, transparent=True)
    img_buffer.seek(0)
    img_str = base64.b64encode(img_buffer.getvalue()).decode()
    plt.close()
    
    # HTML로 이미지 표시
    html_code = f"""
    <div style="text-align: center;">
        <img src="data:image/png;base64,{img_str}" style="width: 100%; max-width: 400px; height: auto;">
    </div>
    """
    
    return html_code

# 색상 스키마들
color_schemes = [
    ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe'],
    ['#43e97b', '#38f9d7', '#fa709a', '#fee140', '#a8edea'],
    ['#ff9a9e', '#fecfef', '#fecfef', '#fad0c4', '#ffd1ff'],
    ['#a8edea', '#fed6e3', '#ffecd2', '#fcb69f', '#ff9a9e'],
    ['#ffecd2', '#fcb69f', '#ff9a9e', '#fecfef', '#fad0c4']
]

# 과정별 워드클라우드 표시 (2행 3열로 배치)
courses = list(course_keywords.keys())
if len(courses) > 0:
    # 첫 번째 행
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if len(courses) > 0:
            # 과정명 제목을 모던하게 스타일링
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                color: white;
                padding: 15px 20px;
                border-radius: 10px;
                margin-bottom: 15px;
                text-align: center;
                font-weight: 600;
                font-size: 16px;
                box-shadow: 0 4px 15px rgba(44, 62, 80, 0.2);
                border: 1px solid #ecf0f1;
                letter-spacing: 0.5px;
            ">
                📚 {courses[0]}
            </div>
            """, unsafe_allow_html=True)
            html1 = create_wordcloud(course_keywords[courses[0]], "", color_schemes[0])
            st.markdown(html1, unsafe_allow_html=True)
    
    with col2:
        if len(courses) > 1:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
                color: white;
                padding: 15px 20px;
                border-radius: 10px;
                margin-bottom: 15px;
                text-align: center;
                font-weight: 600;
                font-size: 16px;
                box-shadow: 0 4px 15px rgba(44, 62, 80, 0.2);
                border: 1px solid #ecf0f1;
                letter-spacing: 0.5px;
            ">
                📚 {courses[1]}
            </div>
            """, unsafe_allow_html=True)
            html2 = create_wordcloud(course_keywords[courses[1]], "", color_schemes[1])
            st.markdown(html2, unsafe_allow_html=True)
    
    with col3:
        if len(courses) > 2:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                color: white;
                padding: 15px 20px;
                border-radius: 10px;
                margin-bottom: 15px;
                text-align: center;
                font-weight: 600;
                font-size: 16px;
                box-shadow: 0 4px 15px rgba(44, 62, 80, 0.2);
                border: 1px solid #ecf0f1;
                letter-spacing: 0.5px;
            ">
                📚 {courses[2]}
            </div>
            """, unsafe_allow_html=True)
            html3 = create_wordcloud(course_keywords[courses[2]], "", color_schemes[2])
            st.markdown(html3, unsafe_allow_html=True)
    
    # 두 번째 행 (과정이 4개 이상인 경우)
    if len(courses) > 3:
        col4, col5, col6 = st.columns(3)
        
        with col4:
            if len(courses) > 3:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
                    color: white;
                    padding: 15px 20px;
                    border-radius: 10px;
                    margin-bottom: 15px;
                    text-align: center;
                    font-weight: 600;
                    font-size: 16px;
                    box-shadow: 0 4px 15px rgba(44, 62, 80, 0.2);
                    border: 1px solid #ecf0f1;
                    letter-spacing: 0.5px;
                ">
                    📚 {courses[3]}
                </div>
                """, unsafe_allow_html=True)
                html4 = create_wordcloud(course_keywords[courses[3]], "", color_schemes[3])
                st.markdown(html4, unsafe_allow_html=True)
        
        with col5:
            if len(courses) > 4:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                    color: white;
                    padding: 15px 20px;
                    border-radius: 10px;
                    margin-bottom: 15px;
                    text-align: center;
                    font-weight: 600;
                    font-size: 16px;
                    box-shadow: 0 4px 15px rgba(44, 62, 80, 0.2);
                    border: 1px solid #ecf0f1;
                    letter-spacing: 0.5px;
                ">
                    📚 {courses[4]}
                </div>
                """, unsafe_allow_html=True)
                html5 = create_wordcloud(course_keywords[courses[4]], "", color_schemes[4])
                st.markdown(html5, unsafe_allow_html=True)
        
        with col6:
            if len(courses) > 5:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
                    color: white;
                    padding: 15px 20px;
                    border-radius: 10px;
                    margin-bottom: 15px;
                    text-align: center;
                    font-weight: 600;
                    font-size: 16px;
                    box-shadow: 0 4px 15px rgba(44, 62, 80, 0.2);
                    border: 1px solid #ecf0f1;
                    letter-spacing: 0.5px;
                ">
                    📚 {courses[5]}
                </div>
                """, unsafe_allow_html=True)
                html6 = create_wordcloud(course_keywords[courses[5]], "", color_schemes[0])
                st.markdown(html6, unsafe_allow_html=True)
else:
    st.info("과정별 데이터가 없습니다.")

# 5. 추가 분석 섹션
st.markdown("""
<div class="section-header">
    <h2>📊 상세 분석</h2>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # 가중치 점수 구간별 분포
    similarity_ranges = pd.cut(recommendations_df['weighted_similarity_score'], 
                              bins=[0, 0.4, 0.6, 0.8, 1.0], 
                              labels=['낮음 (0.4미만)', '보통 (0.4-0.6)', '높음 (0.6-0.8)', '매우높음 (0.8이상)'])
    range_counts = similarity_ranges.value_counts()
    
    fig_range = px.pie(
        values=range_counts.values,
        names=range_counts.index,
        title="🎯 가중치 점수 구간별 분포",
        color_discrete_sequence=['#ff6b6b', '#feca57', '#48dbfb', '#0abde3']
    )
    fig_range.update_layout(
        title_font_size=16,
        font=dict(family="Inter", size=12),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_range, use_container_width=True)

with col2:
    # 지역별 추천 분포
    location_counts = recommendations_df['location'].value_counts().head(10)
    fig_location = px.bar(
        x=location_counts.index,
        y=location_counts.values,
        title="📍 지역별 추천 분포 (상위 10개)",
        labels={'x': '지역', 'y': '추천 개수'},
        color_discrete_sequence=['#764ba2']
    )
    fig_location.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title_font_size=16,
        font=dict(family="Inter", size=12),
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_tickangle=-45
    )
    fig_location.update_xaxes(gridcolor='rgba(0,0,0,0.1)', zeroline=False)
    fig_location.update_yaxes(gridcolor='rgba(0,0,0,0.1)', zeroline=False)
    st.plotly_chart(fig_location, use_container_width=True)

# 푸터
st.markdown("""
<div class="footer">
    <p><strong>🎯 AI Job Recommender</strong> | SBERT 기반 맞춤형 추천 시스템</p>
    <p>© 2024 AI 활용 아이디어 경진대회 | 실시간 업데이트</p>
</div>
""", unsafe_allow_html=True) 