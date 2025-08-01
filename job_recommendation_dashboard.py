import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import numpy as np
from datetime import datetime
import plotly.figure_factory as ff

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
</style>
""", unsafe_allow_html=True)

# 데이터베이스 연결
@st.cache_data(ttl=300)  # 5분마다 캐시 갱신
def load_data():
    try:
        # 환경변수에서 데이터베이스 설정 가져오기
        import os
        
        # Streamlit secrets에서 설정 가져오기 (배포 환경)
        if hasattr(st, 'secrets') and st.secrets:
            db_config = st.secrets.get("DB_CONFIG", {})
            host = db_config.get("host", "127.0.0.1")
            user = db_config.get("user", "root")
            password = db_config.get("password", "15861")
            database = db_config.get("database", "job_recoder")
            port = db_config.get("port", "3306")
        else:
            # 로컬 환경에서는 기본값 사용
            host = os.getenv("DB_HOST", "127.0.0.1")
            user = os.getenv("DB_USER", "root")
            password = os.getenv("DB_PASSWORD", "15861")
            database = os.getenv("DB_NAME", "job_recoder")
            port = os.getenv("DB_PORT", "3306")
        
        engine = create_engine(
            f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4'
        )
        
        # 추천 결과 로드
        recommendations_query = """
        SELECT * FROM enhanced_job_recommendations 
        ORDER BY trainee_name, rank
        """
        recommendations_df = pd.read_sql(recommendations_query, engine)
        
        # 훈련생 데이터 로드
        trainees_query = "SELECT * FROM merged_trainee_data"
        trainees_df = pd.read_sql(trainees_query, engine)
        
        # 채용 데이터 로드
        jobs_query = "SELECT * FROM enhanced_job_postings WHERE active = 1"
        jobs_df = pd.read_sql(jobs_query, engine)
        
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
    avg_similarity = recommendations_df['similarity_score'].mean()
    st.markdown(f"""
    <div class="metric-card">
        <h3>평균 유사도</h3>
        <h2>{avg_similarity:.3f}</h2>
    </div>
    """, unsafe_allow_html=True)
    
with col4:
    max_similarity = recommendations_df['similarity_score'].max()
    st.markdown(f"""
    <div class="metric-card">
        <h3>최고 유사도</h3>
        <h2>{max_similarity:.3f}</h2>
    </div>
    """, unsafe_allow_html=True)

# 차트 섹션
col1, col2 = st.columns(2)

with col1:
    # 유사도 분포 차트
    fig_similarity = px.histogram(
        recommendations_df, 
        x='similarity_score',
        nbins=20,
        title="📈 유사도 점수 분포",
        labels={'similarity_score': '유사도 점수', 'count': '추천 개수'},
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
    ]
    
    # 훈련생 정보
    trainee_info = trainees_df[trainees_df['이름'] == selected_trainee].iloc[0]
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("""
        <div style="background: white; padding: 0.75rem; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border: 1px solid #e9ecef;">
            <h3 style="color: #2c3e50; margin-bottom: 0.25rem;">👤 훈련생 정보</h3>
        </div>
        """, unsafe_allow_html=True)
        st.write(f"**이름**: {trainee_info['이름']}")
        st.write(f"**과정명**: {trainee_info['과정명']}")
        st.write(f"**희망직종**: {trainee_info['희망직종']}")
        st.write(f"**희망업종**: {trainee_info['희망업종']}")
        st.write(f"**희망지역**: {trainee_info['희망지역']}")
        st.write(f"**희망보수**: {trainee_info['희망보수']}만원")
    
    with col2:
        st.markdown("""
        <div style="background: white; padding: 0.75rem; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border: 1px solid #e9ecef;">
            <h3 style="color: #2c3e50; margin-bottom: 0.25rem;">🎯 추천 채용</h3>
        </div>
        """, unsafe_allow_html=True)
        
        for idx, row in trainee_recommendations.iterrows():
            similarity_color = "🟢" if row['similarity_score'] >= 0.9 else "🟡" if row['similarity_score'] >= 0.8 else "🔴"
            
            with st.expander(f"{similarity_color} {row['rank']}. {row['job_title']} - {row['company_name']} (유사도: {row['similarity_score']:.3f})"):
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

# 채용정보 테이블
if len(filtered_jobs) > 0:
    display_jobs = filtered_jobs[['title', 'company_name', 'industry', 'location', 'job_type', 'salary']].head(20)
    st.dataframe(display_jobs, use_container_width=True)

# 4. 과정별 추천 분석
st.markdown("""
<div class="section-header">
    <h2>📚 과정별 분석</h2>
</div>
""", unsafe_allow_html=True)

# 과정별 평균 유사도
course_analysis = recommendations_df.merge(
    trainees_df[['이름', '과정명']], 
    left_on='trainee_name', 
    right_on='이름'
)

course_avg_similarity = course_analysis.groupby('과정명')['similarity_score'].mean().sort_values(ascending=False)

fig_course = px.bar(
    x=course_avg_similarity.values,
    y=course_avg_similarity.index,
    orientation='h',
    title="📚 과정별 평균 유사도",
    labels={'x': '평균 유사도', 'y': '과정명'},
    color_discrete_sequence=['#667eea']
)
fig_course.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    title_font_size=16,
    font=dict(family="Inter", size=12),
    margin=dict(l=20, r=20, t=40, b=20)
)
fig_course.update_xaxes(gridcolor='rgba(0,0,0,0.1)', zeroline=False)
fig_course.update_yaxes(gridcolor='rgba(0,0,0,0.1)', zeroline=False)
st.plotly_chart(fig_course, use_container_width=True)

# 5. 추가 분석 섹션
st.markdown("""
<div class="section-header">
    <h2>📊 상세 분석</h2>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # 유사도 구간별 분포
    similarity_ranges = pd.cut(recommendations_df['similarity_score'], 
                              bins=[0, 0.7, 0.8, 0.9, 1.0], 
                              labels=['낮음 (0.7미만)', '보통 (0.7-0.8)', '높음 (0.8-0.9)', '매우높음 (0.9이상)'])
    range_counts = similarity_ranges.value_counts()
    
    fig_range = px.pie(
        values=range_counts.values,
        names=range_counts.index,
        title="🎯 유사도 구간별 분포",
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