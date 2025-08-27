import streamlit as st
import pandas as pd

st.set_page_config(page_title="채용 추천 뷰어", layout="wide")

# CSV 파일 로드
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('student_recommendations.csv')
        return df
    except:
        st.error("CSV 파일을 찾을 수 없습니다.")
        return None

# 메인 앱
st.title("🎯 학생 맞춤 채용 추천 뷰어")

# 데이터 로드
df = load_data()

if df is not None:
    st.success(f"✅ {len(df)}개의 추천 결과를 불러왔습니다.")
    
    # 학생 선택
    students = df['student_id'].unique()
    selected_student = st.selectbox("학생 선택:", students)
    
    if selected_student:
        # 해당 학생의 추천 결과
        student_data = df[df['student_id'] == selected_student].sort_values('recommendation_rank')
        
        st.header(f"👤 {selected_student}님의 추천 결과")
        
        # 추천 결과 표시
        for _, row in student_data.iterrows():
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    **{row['recommendation_rank']}순위**: {row['recommended_title']}
                    - 회사: {row['recommended_company']}
                    - 지역: {row['recommended_location']}
                    - 점수: {row['final_score']:.3f}
                    """)
                
                with col2:
                    if pd.notna(row['recommended_job_id']):
                        job_id = int(row['recommended_job_id'])
                        saramin_url = f"https://www.saramin.co.kr/zf_user/jobs/relay/view?isMypage=no&rec_idx={job_id}"
                        st.markdown(f"[🔗 채용공고]({saramin_url})")
                
                st.divider()
    
    # 전체 데이터 보기
    if st.checkbox("📊 전체 데이터 보기"):
        st.dataframe(df, use_container_width=True)

else:
    st.warning("데이터를 불러올 수 없습니다.")
