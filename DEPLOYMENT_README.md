# 🚀 Streamlit Cloud 배포 가이드

## 📋 배포 전 준비사항

### 1. GitHub 계정 및 저장소
- GitHub 계정이 필요합니다
- 새로운 공개 저장소를 생성해야 합니다

### 2. 데이터베이스 설정
현재 로컬 MariaDB를 사용하고 있으므로, 클라우드 배포 시 다음 중 하나를 선택해야 합니다:

#### 옵션 A: 클라우드 데이터베이스 사용
- **PlanetScale** (MySQL 호환, 무료 티어 제공)
- **AWS RDS** (MySQL)
- **Google Cloud SQL** (MySQL)

#### 옵션 B: 로컬 데이터베이스 터널링
- **ngrok** 또는 **localtunnel** 사용
- 보안상 권장하지 않음

## 🔧 배포 과정

### 1단계: GitHub 저장소 생성
```bash
# 1. GitHub에서 새 저장소 생성
# 2. 저장소 이름: student-job-recommendation-system
# 3. 공개 저장소로 설정
# 4. README 파일 생성하지 않음
```

### 2단계: 로컬 코드 업로드
```bash
git add .
git commit -m "Initial commit: Student Job Recommendation System"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/student-job-recommendation-system.git
git push -u origin main
```

### 3단계: Streamlit Cloud 배포
1. [share.streamlit.io](https://share.streamlit.io) 접속
2. GitHub 계정으로 로그인
3. 저장소 선택: `student-job-recommendation-system`
4. 메인 파일 경로: `student_recommendation_app.py`
5. 배포 버튼 클릭

## ⚙️ 환경 변수 설정

Streamlit Cloud에서 다음 환경 변수를 설정해야 합니다:

### 필수 환경 변수
```
DB_HOST=your-database-host
DB_USER=your-database-username
DB_PASSWORD=your-database-password
DB_NAME=your-database-name
DB_PORT=3306
```

### 설정 방법
1. Streamlit Cloud 대시보드에서 앱 선택
2. Settings → Secrets → Edit secrets
3. 위의 환경 변수들을 추가

## 🔒 보안 고려사항

### 1. 데이터베이스 접근
- 공개 저장소에 데이터베이스 자격 증명을 포함하지 마세요
- 환경 변수를 통해 안전하게 관리하세요

### 2. API 키
- Saramin API 키가 있다면 환경 변수로 관리하세요
- 코드에 직접 하드코딩하지 마세요

## 📱 배포 후 확인사항

### 1. 앱 접속 테스트
- 제공된 URL로 접속 가능한지 확인
- 로그인 기능이 정상 작동하는지 확인

### 2. 데이터베이스 연결 테스트
- 학생 정보 로드가 정상인지 확인
- 추천 결과 표시가 정상인지 확인

### 3. 성능 모니터링
- 페이지 로딩 속도 확인
- 동시 사용자 처리 능력 확인

## 🆘 문제 해결

### 일반적인 문제들
1. **데이터베이스 연결 실패**: 환경 변수 확인
2. **모듈 import 오류**: requirements.txt 확인
3. **권한 오류**: 데이터베이스 사용자 권한 확인

### 지원 채널
- Streamlit Cloud 문서
- GitHub Issues
- Stack Overflow

## 🎯 다음 단계

배포가 완료되면:
1. 학생들에게 공개 URL 공유
2. 사용자 피드백 수집
3. 성능 최적화
4. 추가 기능 개발

---

**🚀 행운을 빕니다! 성공적인 배포를 기원합니다!**
