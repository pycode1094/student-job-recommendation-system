import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

# 페이지 설정 - 최적화
st.set_page_config(
    page_title="학생 맞춤 채용 추천 시스템",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 로딩 최적화를 위한 캐싱 강화
@st.cache_data(ttl=3600)  # 1시간 캐시
def load_recommendations():
    """추천 결과 파일을 로드합니다. (최적화됨)"""
    try:
        # CSV 파일 로드 - 최적화된 방식
        df = pd.read_csv('student_recommendations.csv', 
                        usecols=['student_id', 'recommendation_rank', 'recommended_title', 
                                'recommended_company', 'recommended_industry', 'recommended_location', 
                                'recommended_job_type', 'recommended_job_id', 'semantic_similarity', 
                                'course_industry_score', 'location_score', 'diversity_score', 
                                'freshness_score', 'final_score'])
        
        # 데이터 타입 최적화
        df['student_id'] = df['student_id'].astype('category')
        df['recommended_company'] = df['recommended_company'].astype('category')
        df['recommended_industry'] = df['recommended_industry'].astype('category')
        df['recommended_location'] = df['recommended_location'].astype('category')
        
        # 점수 컬럼 최적화
        score_columns = ['semantic_similarity', 'course_industry_score', 'location_score', 
                        'diversity_score', 'freshness_score', 'final_score']
        for col in score_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0).round(4)
        
        return df
    except Exception as e:
        st.error(f"파일 로드 실패: {e}")
        return None

@st.cache_data(ttl=3600)
def get_student_credentials():
    """학생 로그인 정보를 반환합니다. (캐시됨)"""
    df = load_recommendations()
    if df is None:
        return {}
    
    # 학생별 정보 추출 - 최적화
    students = {}
    unique_students = df['student_id'].unique()
    for student_id in unique_students:
        students[student_id] = {
            'name': f"학생 {student_id[-4:]}",
            'course': "AI 활용 과정",
            'password': '0000'
        }
    
    return students

@st.cache_data(ttl=1800)  # 30분 캐시
def get_student_recommendations(student_id):
    """학생의 추천 결과를 가져옵니다. (캐시됨)"""
    try:
        df = load_recommendations()
        if df is None:
            return None
        
        # 해당 학생의 추천 결과만 필터링 - 최적화
        student_recommendations = df[df['student_id'] == student_id].copy()
        
        if student_recommendations.empty:
            return None
        
        # 순위별로 정렬
        student_recommendations = student_recommendations.sort_values('recommendation_rank')
        
        return student_recommendations
    except Exception as e:
        st.error(f"추천 결과 로드 실패: {e}")
        return None

def login_page():
    """로그인 페이지를 표시합니다. (최적화됨)"""
    # 간단한 로딩 표시
    with st.spinner("시스템 로딩 중..."):
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <h1>🎯 학생 맞춤 채용 추천 시스템</h1>
            <p style="font-size: 1.2rem; color: #666;">AI 기반 개인화된 채용 정보를 확인하세요</p>
            <p style="font-size: 1rem; color: #888;">📊 실제 추천 결과 기반</p>
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
                    with st.spinner("로그인 확인 중..."):
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
            
            # 사용 가능한 학번 정보 표시 (지연 로딩)
            if st.button("📋 사용 가능한 학번 보기"):
                with st.spinner("학번 목록 로딩 중..."):
                    credentials = get_student_credentials()
                    if credentials:
                        st.markdown("### 📋 사용 가능한 학번")
                        available_students = list(credentials.keys())[:10]
                        demo_info = ""
                        for student_id in available_students:
                            demo_info += f"**{student_id}**  \n"
                        st.markdown(demo_info)
                        
                        if len(credentials) > 10:
                            st.markdown(f"*... 및 {len(credentials) - 10}개 더*")

def display_recommendations(df, student_name, course_name):
    """추천 결과를 표시합니다. (최적화됨)"""
    if df is None or df.empty:
        st.warning("📭 아직 추천 결과가 없습니다.")
        return
    
    # 헤더 정보
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 10px; color: white;">
        <h2>👋 {student_name}님의 맞춤 채용 추천</h2>
        <p style="font-size: 1.1rem; margin: 0;">📚 과정: {course_name}</p>
        <p style="font-size: 1.1rem; margin: 0;">📊 총 {len(df)}개의 추천 결과</p>
        <p style="font-size: 1rem; margin: 0; opacity: 0.9;">🎯 AI 기반 맞춤 추천</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 추천 결과를 배치로 표시 (성능 향상)
    batch_size = 3  # 한 번에 3개씩 표시
    
    for i in range(0, len(df), batch_size):
        batch_df = df.iloc[i:i+batch_size]
        
        # 배치별로 컬럼 생성
        cols = st.columns(batch_size)
        
        for j, (idx, row) in enumerate(batch_df.iterrows()):
            with cols[j]:
                # 간소화된 카드 표시
                st.markdown(f"""
                <div style="border: 1px solid #ddd; border-radius: 10px; padding: 1rem; margin: 0.5rem 0; background: white;">
                    <h4>🏆 {row['recommendation_rank']}순위</h4>
                    <h5 style="color: #1f77b4;">{row['recommended_title'][:30]}{'...' if len(row['recommended_title']) > 30 else ''}</h5>
                    <p><strong>🏢</strong> {row['recommended_company']}</p>
                    <p><strong>📍</strong> {row['recommended_location']}</p>
                    <p><strong>🎯</strong> {row['final_score']:.3f}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Saramin 링크
                if 'recommended_job_id' in row and pd.notna(row['recommended_job_id']):
                    job_id = int(row['recommended_job_id'])
                    saramin_url = f"https://www.saramin.co.kr/zf_user/jobs/relay/view?isMypage=no&rec_idx={job_id}"
                    
                    st.markdown(f"""
                    <a href="{saramin_url}" target="_blank">
                        <button style="
                            background: #667eea;
                            color: white;
                            border: none;
                            padding: 0.3rem 0.8rem;
                            border-radius: 5px;
                            cursor: pointer;
                            font-size: 0.8rem;
                        ">
                            🔗 채용공고
                        </button>
                    </a>
                    """, unsafe_allow_html=True)
        
        # 배치 간 구분선
        if i + batch_size < len(df):
            st.markdown("---")

def display_statistics(df):
    """통계 정보를 표시합니다. (최적화됨)"""
    if df is None or df.empty:
        return
    
    st.markdown("### 📈 추천 결과 통계")
    
    # 간단한 메트릭만 표시 (성능 향상)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_final_score = df['final_score'].mean()
        st.metric("평균 점수", f"{avg_final_score:.3f}")
    
    with col2:
        st.metric("추천 수", len(df))
    
    with col3:
        st.metric("회사 수", df['recommended_company'].nunique())
    
    with col4:
        st.metric("지역 수", df['recommended_location'].nunique())
    
    # 차트는 필요시에만 표시
    if st.checkbox("📊 상세 차트 보기"):
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = px.histogram(
                df, 
                x='final_score', 
                nbins=8,  # 빈 수 줄임
                title="점수 분포"
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = px.scatter(
                df,
                x='semantic_similarity',
                y='location_score',
                title="유사도 vs 지역"
            )
            st.plotly_chart(fig2, use_container_width=True)

def main():
    """메인 애플리케이션 (최적화됨)"""
    # 세션 상태 초기화
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    # 사이드바 (간소화)
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h3>🎯 추천 시스템</h3>
            <p>AI 기반 맞춤 채용 추천</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state['logged_in']:
            st.success(f"✅ {st.session_state['student_name']}님")
            
            if st.button("🚪 로그아웃"):
                st.session_state['logged_in'] = False
                st.rerun()
            
            st.markdown("---")
            st.markdown("### 📊 메뉴")
            st.markdown("- 🏠 **홈**: 추천 결과")
            st.markdown("- 📈 **통계**: 분석")
            st.markdown("- 🔍 **검색**: 필터링")
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
        
        # 추천 결과 가져오기 (캐시 활용)
        with st.spinner("추천 결과 로딩 중..."):
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
                # 간단한 필터만 제공
                col1, col2 = st.columns(2)
                
                with col1:
                    locations = ['전체'] + list(recommendations_df['recommended_location'].unique())
                    selected_location = st.selectbox("지역", locations)
                
                with col2:
                    min_score = st.slider("최소 점수", 0.0, 1.0, 0.0, 0.1)
                
                # 필터링
                filtered_df = recommendations_df.copy()
                
                if selected_location != '전체':
                    filtered_df = filtered_df[filtered_df['recommended_location'] == selected_location]
                
                filtered_df = filtered_df[filtered_df['final_score'] >= min_score]
                
                st.markdown(f"### 🔍 결과 ({len(filtered_df)}개)")
                if not filtered_df.empty:
                    st.dataframe(
                        filtered_df[['recommendation_rank', 'recommended_title', 'recommended_company', 'final_score']],
                        use_container_width=True
                    )
                else:
                    st.warning("📭 조건에 맞는 결과가 없습니다.")

if __name__ == "__main__":
    main()
