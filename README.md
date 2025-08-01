# 🎯 AI 기반 채용 추천 시스템

SBERT(Sentence-BERT) 기반의 맞춤형 채용 추천 시스템입니다.

## ✨ 주요 기능

- **🤖 AI 기반 추천**: SBERT 모델을 활용한 정확한 채용 매칭
- **📊 실시간 대시보드**: Streamlit 기반의 인터랙티브 웹 대시보드
- **🔍 상세 분석**: 유사도 점수, 산업별/지역별 분포 분석
- **👥 개인별 추천**: 훈련생별 맞춤형 채용 추천 결과
- **📈 통계 시각화**: Plotly 기반의 아름다운 차트와 그래프

## 🚀 기술 스택

- **Backend**: Python, SQLAlchemy, PyMySQL
- **AI/ML**: Sentence-BERT, Scikit-learn
- **Frontend**: Streamlit, Plotly
- **Database**: MySQL
- **API**: Saramin 채용 API

## 📦 설치 및 실행

### 1. 환경 설정
```bash
pip install -r requirements.txt
```

### 2. 데이터베이스 설정
MySQL 데이터베이스 `job_recoder`에 다음 테이블들이 필요합니다:
- `enhanced_job_postings`: 채용 정보
- `enhanced_job_recommendations`: 추천 결과
- `merged_trainee_data`: 훈련생 정보

### 3. 실행
```bash
streamlit run job_recommendation_dashboard.py
```

## 🌐 배포 방법

### Streamlit Cloud 배포 (추천)

1. **GitHub에 코드 업로드**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/job-recommendation-system.git
   git push -u origin main
   ```

2. **Streamlit Cloud에서 배포**
   - [share.streamlit.io](https://share.streamlit.io) 접속
   - GitHub 계정 연결
   - 저장소 선택
   - 배포 설정 후 배포

### 환경 변수 설정
배포 시 다음 환경 변수를 설정하세요:
```
DB_HOST=your-database-host
DB_USER=your-database-user
DB_PASSWORD=your-database-password
DB_NAME=your-database-name
```

## 📊 대시보드 기능

### 1. 전체 통계
- 총 추천 개수, 훈련생 수
- 평균/최고 유사도 점수
- 유사도 분포 히스토그램

### 2. 훈련생별 추천
- 개인별 맞춤 추천 결과
- 유사도 점수별 색상 구분
- 상세 채용 정보 제공

### 3. 채용정보 검색
- 지역, 산업, 고용형태별 필터링
- 실시간 검색 결과

### 4. 과정별 분석
- 과정별 평균 유사도 점수
- 추천 정확도 분석

### 5. 추가 분석
- 유사도 구간별 분포 (파이 차트)
- 지역별 추천 분포

## 🎨 디자인 특징

- **그라데이션 색상**: 보라색-파란색 그라데이션 테마
- **반응형 디자인**: 모바일/데스크톱 모두 지원
- **인터랙티브 요소**: 호버 효과, 애니메이션
- **직관적 UI**: 이모지와 색상으로 정보 구분

## 📈 성능 지표

- **평균 유사도**: 0.889 (매우 높은 정확도)
- **추천 범위**: 0.7 이상의 유사도만 추천
- **실시간 업데이트**: 5분마다 데이터 갱신

## 🔧 커스터마이징

### 색상 테마 변경
`job_recommendation_dashboard.py`의 CSS 섹션에서 색상을 수정할 수 있습니다:

```css
.main-header {
    background: linear-gradient(90deg, #your-color1 0%, #your-color2 100%);
}
```

### 차트 스타일 변경
Plotly 차트의 `color_discrete_sequence` 파라미터를 수정하여 색상을 변경할 수 있습니다.

## 📝 라이선스

© 2024 AI 활용 아이디어 경진대회

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해 주세요. 