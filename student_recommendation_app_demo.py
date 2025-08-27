import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 페이지 설정
st.set_page_config(
    page_title="학생 맞춤 채용 추천 시스템 (데모)",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 데모 데이터 생성
def create_demo_data():
    """데모 데이터를 생성합니다."""
    
    # 학생 정보
    students = {
        "202401020011": {"name": "김철수", "course": "반도체공학과"},
        "202401020008": {"name": "이영희", "course": "전기전자공학과"},
        "202401020007": {"name": "박민수", "course": "기계공학과"},
        "202401020006": {"name": "정수진", "course": "컴퓨터공학과"},
        "202401020005": {"name": "최지원", "course": "로봇공학과"},
        "202401020004": {"name": "강동현", "course": "해양공학과"},
        "202401020003": {"name": "윤서연", "course": "AI융합학과"},
        "202401020002": {"name": "임태호", "course": "반도체공학과"},
        "202401020001": {"name": "한미영", "course": "전기전자공학과"},
        "202401020000": {"name": "송재현", "course": "기계공학과"}
    }
    
    # 채용 공고 데이터
    job_postings = [
        {
            "id": 1, "title": "반도체 설계 엔지니어", "company": "삼성전자", 
            "industry": "반도체·광학·LCD", "location": "경기도 용인시", "job_type": "정규직",
            "semantic_similarity": 0.85, "course_industry_score": 0.95, "location_score": 0.75,
            "diversity_score": 0.90, "freshness_score": 0.80, "final_score": 0.85
        },
        {
            "id": 2, "title": "AI 알고리즘 개발자", "company": "네이버", 
            "industry": "IT·정보통신업", "location": "경기도 성남시", "job_type": "정규직",
            "semantic_similarity": 0.82, "course_industry_score": 0.88, "location_score": 0.70,
            "diversity_score": 0.85, "freshness_score": 0.85, "final_score": 0.82
        },
        {
            "id": 3, "title": "전기 설계 엔지니어", "company": "LG전자", 
            "industry": "전기·전자", "location": "서울시 영등포구", "job_type": "정규직",
            "semantic_similarity": 0.78, "course_industry_score": 0.92, "location_score": 0.65,
            "diversity_score": 0.80, "freshness_score": 0.75, "final_score": 0.78
        },
        {
            "id": 4, "title": "기계 설계 엔지니어", "company": "현대자동차", 
            "industry": "자동차·자동차부품", "location": "울산광역시", "job_type": "정규직",
            "semantic_similarity": 0.75, "course_industry_score": 0.90, "location_score": 0.60,
            "diversity_score": 0.75, "freshness_score": 0.70, "final_score": 0.75
        },
        {
            "id": 5, "title": "로봇 제어 엔지니어", "company": "두산로보틱스", 
            "industry": "기계·장비", "location": "부산광역시", "job_type": "정규직",
            "semantic_similarity": 0.80, "course_industry_score": 0.93, "location_score": 0.85,
            "diversity_score": 0.85, "freshness_score": 0.80, "final_score": 0.80
        },
        {
            "id": 6, "title": "해양 구조물 설계", "company": "대우조선해양", 
            "industry": "조선·해양플랜트", "location": "부산광역시", "job_type": "정규직",
            "semantic_similarity": 0.72, "course_industry_score": 0.88, "location_score": 0.90,
            "diversity_score": 0.70, "freshness_score": 0.65, "final_score": 0.72
        },
        {
            "id": 7, "title": "AI 연구원", "company": "카카오", 
            "industry": "IT·정보통신업", "location": "제주특별자치도", "job_type": "정규직",
            "semantic_similarity": 0.88, "course_industry_score": 0.95, "location_score": 0.55,
            "diversity_score": 0.90, "freshness_score": 0.90, "final_score": 0.88
        },
        {
            "id": 8, "title": "반도체 공정 엔지니어", "company": "SK하이닉스", 
            "industry": "반도체·광학·LCD", "location": "경기도 이천시", "job_type": "정규직",
            "semantic_similarity": 0.83, "course_industry_score": 0.94, "location_score": 0.70,
            "diversity_score": 0.82, "freshness_score": 0.78, "final_score": 0.83
        },
        {
            "id": 9, "title": "전자 회로 설계", "company": "LG이노텍", 
            "industry": "전기·전자", "location": "경기도 안산시", "job_type": "정규직",
            "semantic_similarity": 0.77, "course_industry_score": 0.91, "location_score": 0.65,
            "diversity_score": 0.78, "freshness_score": 0.72, "final_score": 0.77
        },
        {
            "id": 10, "title": "자동차 엔진 설계", "company": "기아자동차", 
            "industry": "자동차·자동차부품", "location": "경기도 화성시", "job_type": "정규직",
            "semantic_similarity": 0.74, "course_industry_score": 0.89, "location_score": 0.60,
            "diversity_score": 0.73, "freshness_score": 0.68, "final_score": 0.74
        }
    ]
    
    return students, job_postings

def get_student_credentials():
    """학생 로그인 정보를 반환합니다."""
    students, _ = create_demo_data()
    
    credentials = {}
    for student_id, info in students.items():
        credentials[student_id] = {
            'name': info['name'],
            'course': info['course'],
            'password': '0000'  # 모든 학생의 비밀번호는 0000
        }
    
    return credentials

def get_student_recommendations(student_id):
    """학생의 추천 결과를 가져옵니다."""
    try:
        _, job_postings = create_demo_data()
        
        # 학생별 맞춤 추천 생성 (5개씩)
        recommendations = []
        for i, job in enumerate(job_postings[:5]):
            recommendation = {
                'recommendation_rank': i + 1,
                'recommended_title': job['title'],
                'recommended_company': job['company'],
                'recommended_industry': job['industry'],
                'recommended_location': job['location'],
                'recommended_job_type': job['job_type'],
                'recommended_job_id': job['id'],
                'semantic_similarity': job['semantic_similarity'],
                'course_industry_score': job['course_industry_score'],
                'location_score': job['location_score'],
                'diversity_score': job['diversity_score'],
                'freshness_score': job['freshness_score'],
                'final_score': job['final_score']
            }
            recommendations.append(recommendation)
        
        return pd.DataFrame(recommendations)
    except Exception as e:
        st.error(f"추천 결과 로드 실패: {e}")
        return None

def login_page():
    """로그인 페이지를 표시합니다."""
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1>🎯 학생 맞춤 채용 추천 시스템 (데모)</h1>
        <p style="font-size: 1.2rem; color: #666;">AI 기반 개인화된 채용 정보를 확인하세요</p>
        <p style="font-size: 1rem; color: #888;">💡 데모 버전: 실제 데이터베이스 연결 없이 작동</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 로그인 폼
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("---")
            st.markdown("### 🔐 로그인")
            
            # 학번 입력
            student_id = st.text_input("학번", placeholder="학번을 입력하세요")
            
            # 비밀번호 입력
            password = st.text_input("비밀번호", type="password", placeholder="0000")
            
            # 로그인 버튼
            if st.button("로그인", type="primary", use_container_width=True):
                if student_id and password:
                    credentials = get_student_credentials()
                    
                    if student_id in credentials and credentials[student_id]['password'] == password:
                        st.session_state['logged_in'] = True
                        st.session_state['student_id'] = student_id
                        st.session_state['student_name'] = credentials[student_id]['name']
                        st.session_state['course_name'] = credentials[student_id]['course']
                        st.rerun()
                    else:
                        st.error("❌ 학번 또는 비밀번호가 올바르지 않습니다.")
                else:
                    st.warning("⚠️ 학번과 비밀번호를 모두 입력해주세요.")
            
            st.markdown("---")
            st.info("💡 **로그인 정보**: 학번은 본인의 학번, 비밀번호는 0000입니다.")
            
            # 데모 계정 정보 표시
            st.markdown("### 📋 데모 계정 정보")
            students, _ = create_demo_data()
            demo_info = ""
            for i, (student_id, info) in enumerate(list(students.items())[:5]):
                demo_info += f"**{student_id}**: {info['name']} ({info['course']})  \n"
            st.markdown(demo_info)

def display_recommendations(df, student_name, course_name):
    """추천 결과를 표시합니다."""
    if df is None or df.empty:
        st.warning("📭 아직 추천 결과가 없습니다.")
        return
    
    # 헤더 정보
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 10px; color: white;">
        <h2>👋 {student_name}님의 맞춤 채용 추천</h2>
        <p style="font-size: 1.1rem; margin: 0;">📚 과정: {course_name}</p>
        <p style="font-size: 1.1rem; margin: 0;">📊 총 {len(df)}개의 추천 결과</p>
        <p style="font-size: 1rem; margin: 0; opacity: 0.9;">🎭 데모 데이터 기반 추천</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 추천 결과 카드 형태로 표시
    for idx, row in df.iterrows():
        with st.container():
            # 점수 시각화
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                <div style="border: 1px solid #ddd; border-radius: 10px; padding: 1.5rem; margin: 1rem 0; background: white;">
                    <h3>🏆 {row['recommendation_rank']}순위 추천</h3>
                    <h4 style="color: #1f77b4;">{row['recommended_title']}</h4>
                    <p><strong>🏢 회사:</strong> {row['recommended_company']}</p>
                    <p><strong>🏭 산업:</strong> {row['recommended_industry']}</p>
                    <p><strong>📍 지역:</strong> {row['recommended_location']}</p>
                    <p><strong>💼 직무:</strong> {row['recommended_job_type']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # 점수 차트
                scores = {
                    '의미적 유사도': row['semantic_similarity'],
                    '과정-산업 매칭': row['course_industry_score'],
                    '지역 점수': row['location_score'],
                    '다양성 점수': row['diversity_score'],
                    '최신성 점수': row['freshness_score']
                }
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=list(scores.values()),
                        y=list(scores.keys()),
                        orientation='h',
                        marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
                    )
                ])
                
                fig.update_layout(
                    title="📊 상세 점수",
                    xaxis_title="점수",
                    yaxis_title="항목",
                    height=300,
                    showlegend=False,
                    margin=dict(l=0, r=0, t=30, b=0)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # 최종 점수와 링크
            col3, col4 = st.columns([1, 1])
            
            with col3:
                st.metric(
                    label="🎯 최종 점수",
                    value=f"{row['final_score']:.4f}",
                    delta=f"순위: {row['recommendation_rank']}위"
                )
            
            with col4:
                # 데모 링크 (실제 채용 공고 대신 회사 홈페이지)
                company_urls = {
                    "삼성전자": "https://www.samsung.com",
                    "네이버": "https://www.naver.com",
                    "LG전자": "https://www.lg.com",
                    "현대자동차": "https://www.hyundai.com",
                    "두산로보틱스": "https://www.doosanrobotics.com",
                    "대우조선해양": "https://www.dsme.co.kr",
                    "카카오": "https://www.kakaocorp.com",
                    "SK하이닉스": "https://www.skhynix.com",
                    "LG이노텍": "https://www.lginnotek.com",
                    "기아자동차": "https://www.kia.com"
                }
                
                company = row['recommended_company']
                if company in company_urls:
                    st.markdown(f"""
                    <a href="{company_urls[company]}" target="_blank">
                        <button style="
                            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            border: none;
                            padding: 0.5rem 1rem;
                            border-radius: 5px;
                            cursor: pointer;
                            text-decoration: none;
                            display: inline-block;
                        ">
                            🔗 회사 홈페이지
                        </button>
                    </a>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")

def display_statistics(df):
    """통계 정보를 표시합니다."""
    if df is None or df.empty:
        return
    
    st.markdown("### 📈 추천 결과 통계")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_final_score = df['final_score'].mean()
        st.metric("평균 최종 점수", f"{avg_final_score:.4f}")
    
    with col2:
        avg_semantic = df['semantic_similarity'].mean()
        st.metric("평균 의미적 유사도", f"{avg_semantic:.4f}")
    
    with col3:
        avg_location = df['location_score'].mean()
        st.metric("평균 지역 점수", f"{avg_location:.4f}")
    
    with col4:
        avg_freshness = df['freshness_score'].mean()
        st.metric("평균 최신성 점수", f"{avg_freshness:.4f}")
    
    # 점수 분포 차트
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.histogram(
            df, 
            x='final_score', 
            nbins=10,
            title="최종 점수 분포",
            labels={'final_score': '최종 점수', 'count': '개수'}
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = px.scatter(
            df,
            x='semantic_similarity',
            y='location_score',
            color='recommendation_rank',
            title="의미적 유사도 vs 지역 점수",
            labels={'semantic_similarity': '의미적 유사도', 'location_score': '지역 점수'}
        )
        st.plotly_chart(fig2, use_container_width=True)

def main():
    """메인 애플리케이션"""
    # 세션 상태 초기화
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    # 사이드바
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h3>🎯 추천 시스템 (데모)</h3>
            <p>AI 기반 맞춤 채용 추천</p>
            <p style="font-size: 0.8rem; color: #888;">데모 데이터 사용</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state['logged_in']:
            st.success(f"✅ {st.session_state['student_name']}님 환영합니다!")
            
            if st.button("🚪 로그아웃", use_container_width=True):
                st.session_state['logged_in'] = False
                st.rerun()
            
            st.markdown("---")
            st.markdown("### 📊 메뉴")
            st.markdown("- 🏠 **홈**: 추천 결과 확인")
            st.markdown("- 📈 **통계**: 상세 분석")
            st.markdown("- 🔍 **검색**: 조건별 필터링")
        else:
            st.info("🔐 로그인이 필요합니다.")
    
    # 메인 콘텐츠
    if not st.session_state['logged_in']:
        login_page()
    else:
        # 로그인된 사용자 메뉴
        student_id = st.session_state['student_id']
        student_name = st.session_state['student_name']
        course_name = st.session_state['course_name']
        
        # 추천 결과 가져오기
        recommendations_df = get_student_recommendations(student_id)
        
        # 탭 메뉴
        tab1, tab2, tab3 = st.tabs(["🏠 홈", "📈 통계", "🔍 검색"])
        
        with tab1:
            display_recommendations(recommendations_df, student_name, course_name)
        
        with tab2:
            display_statistics(recommendations_df)
        
        with tab3:
            st.markdown("### 🔍 조건별 검색")
            if recommendations_df is not None and not recommendations_df.empty:
                # 지역별 필터
                locations = recommendations_df['recommended_location'].unique()
                selected_location = st.selectbox("지역 선택", ['전체'] + list(locations))
                
                # 산업별 필터
                industries = recommendations_df['recommended_industry'].unique()
                selected_industry = st.selectbox("산업 선택", ['전체'] + list(industries))
                
                # 점수 범위 필터
                min_score = st.slider("최소 점수", 0.0, 1.0, 0.0, 0.1)
                
                # 필터링된 결과
                filtered_df = recommendations_df.copy()
                
                if selected_location != '전체':
                    filtered_df = filtered_df[filtered_df['recommended_location'] == selected_location]
                
                if selected_industry != '전체':
                    filtered_df = filtered_df[filtered_df['recommended_industry'] == selected_industry]
                
                filtered_df = filtered_df[filtered_df['final_score'] >= min_score]
                
                st.markdown(f"### 🔍 필터링 결과 ({len(filtered_df)}개)")
                if not filtered_df.empty:
                    st.dataframe(
                        filtered_df[['recommendation_rank', 'recommended_title', 'recommended_company', 
                                   'recommended_location', 'final_score']],
                        use_container_width=True
                    )
                else:
                    st.warning("📭 조건에 맞는 결과가 없습니다.")

if __name__ == "__main__":
    main()
