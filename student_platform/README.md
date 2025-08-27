# 학생용 취업지원 플랫폼

대한상공회의소 취업지원 DB구축 및 데이터활용 AI 추천시스템의 학생용 플랫폼입니다.

## 🚀 실행 방법

### 1. 배치 파일로 실행 (권장)
```bash
run_student_platform.bat
```

### 2. 직접 실행
```bash
streamlit run student_login.py --server.port 8502
```

## 🔐 로그인 정보

- **아이디**: 등록된 학번
- **비밀번호**: 0000 (기본값)
- **접속 주소**: http://localhost:8502

## 📁 파일 구조

```
student_platform/
├── student_login.py          # 학생 로그인 페이지
├── run_student_platform.bat  # 실행 배치 파일
└── README.md                # 이 파일
```

## 🎯 주요 기능

### 현재 구현된 기능
- ✅ 학생 로그인 (학번 기반)
- ✅ 세션 관리
- ✅ 로그아웃

### 향후 구현 예정 기능
- 🔄 개인 맞춤 취업 추천
- 🔄 추천 결과 상세 보기
- 🔄 관심 채용공고 저장
- 🔄 지원 현황 관리
- 🔄 개인 프로필 관리

## 🛠️ 기술 스택

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: MySQL (MariaDB)
- **Styling**: CSS3, Inter Font

## 📊 데이터베이스 연결

- **Host**: 127.0.0.1:3306
- **Database**: job_recoder
- **Table**: merged_trainee_data
- **Columns**: 학번, 이름

## 🔧 개발 환경 설정

1. Python 3.8+ 설치
2. 필요한 패키지 설치:
   ```bash
   pip install streamlit pandas sqlalchemy pymysql
   ```
3. MariaDB/MySQL 서버 실행
4. 데이터베이스 연결 확인

## 📝 주의사항

- 기존 관리자 대시보드(포트 8501)와 별도로 포트 8502에서 실행됩니다.
- 로그인 후 세션 정보는 브라우저를 닫으면 초기화됩니다.
- 데이터베이스 연결이 필요하므로 MariaDB 서버가 실행 중이어야 합니다.





