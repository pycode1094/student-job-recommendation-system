# 🌐 AI 직업 추천 시스템 외부 배포 가이드

## 📋 개요
이 가이드는 AI 직업 추천 시스템을 외부 컴퓨터에서도 접속할 수 있도록 배포하는 방법을 설명합니다.

## 🚀 빠른 시작

### 1. 배포 스크립트 실행
```bash
# Windows
deploy_external.bat

# Linux/Mac
chmod +x deploy_external.sh
./deploy_external.sh
```

### 2. 웹 브라우저에서 접속
- 로컬 접속: `http://localhost:5000`
- 외부 접속: `http://[서버공인IP]:5000`

## 🔧 상세 설정

### 1. 방화벽 설정

#### Windows 방화벽
```powershell
# 관리자 권한으로 PowerShell 실행
New-NetFirewallRule -DisplayName "AI 추천 시스템" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
```

#### Linux 방화벽 (ufw)
```bash
sudo ufw allow 5000
sudo ufw reload
```

#### AWS/클라우드 서비스
- 보안 그룹에서 5000번 포트 인바운드 규칙 추가
- 소스: 0.0.0.0/0 (모든 IP 허용)

### 2. MySQL 외부 접속 허용

#### MySQL 설정 파일 수정
```bash
# /etc/mysql/mysql.conf.d/mysqld.cnf 또는 my.cnf
[mysqld]
bind-address = 0.0.0.0  # 모든 IP에서 접속 허용
```

#### MySQL 사용자 권한 설정
```sql
-- MySQL에 접속
mysql -u root -p

-- 외부 접속 허용 사용자 생성
CREATE USER 'root'@'%' IDENTIFIED BY '15861';
GRANT ALL PRIVILEGES ON job_recoder.* TO 'root'@'%';
FLUSH PRIVILEGES;

-- 또는 기존 사용자 권한 수정
UPDATE mysql.user SET Host='%' WHERE User='root' AND Host='localhost';
FLUSH PRIVILEGES;
```

#### MySQL 서비스 재시작
```bash
# Windows
net stop mysql
net start mysql

# Linux
sudo systemctl restart mysql
```

### 3. 환경 변수 설정

#### Windows
```cmd
set DB_HOST=0.0.0.0
set DB_PORT=3306
set DB_USER=root
set DB_PASSWORD=15861
set DB_NAME=job_recoder
```

#### Linux/Mac
```bash
export DB_HOST=0.0.0.0
export DB_PORT=3306
export DB_USER=root
export DB_PASSWORD=15861
export DB_NAME=job_recoder
```

## 📡 API 사용법

### 1. 시스템 상태 확인
```bash
curl http://[서버IP]:5000/api/health
```

### 2. 추천 생성
```bash
curl -X POST http://[서버IP]:5000/api/generate-recommendations \
  -H "Content-Type: application/json" \
  -d '{"top_k": 10}'
```

### 3. 추천 결과 조회
```bash
# 전체 결과
curl http://[서버IP]:5000/api/recommendations

# 특정 훈련생 결과
curl http://[서버IP]:5000/api/recommendations/trainee/[학번]
```

## 🌍 외부 접속 테스트

### 1. 공인 IP 확인
```bash
# Windows
curl ifconfig.me

# Linux
curl ifconfig.me
# 또는
wget -qO- ifconfig.me
```

### 2. 포트 접속 테스트
```bash
# telnet으로 포트 확인
telnet [서버IP] 5000

# 또는 nmap 사용
nmap -p 5000 [서버IP]
```

### 3. 브라우저에서 테스트
- `http://[서버공인IP]:5000` 접속
- API 엔드포인트 테스트

## 🔒 보안 고려사항

### 1. 방화벽 제한
```bash
# 특정 IP만 허용 (권장)
sudo ufw allow from [신뢰할IP] to any port 5000

# 또는 특정 네트워크 대역만 허용
sudo ufw allow from 192.168.1.0/24 to any port 5000
```

### 2. MySQL 보안
```sql
-- 특정 IP에서만 접속 허용
CREATE USER 'root'@'192.168.1.%' IDENTIFIED BY '15861';
GRANT ALL PRIVILEGES ON job_recoder.* TO 'root'@'192.168.1.%';
```

### 3. HTTPS 설정 (선택사항)
```python
# improved_recommendation.py에서
app.run(
    host='0.0.0.0',
    port=5000,
    ssl_context='adhoc'  # 자체 서명 인증서
)
```

## 🐛 문제 해결

### 1. 포트가 열리지 않는 경우
```bash
# 포트 사용 중인지 확인
netstat -an | findstr :5000  # Windows
netstat -tulpn | grep :5000  # Linux

# 프로세스 종료
taskkill /PID [프로세스ID] /F  # Windows
kill -9 [프로세스ID]           # Linux
```

### 2. MySQL 연결 오류
```bash
# MySQL 상태 확인
systemctl status mysql  # Linux
sc query mysql          # Windows

# MySQL 로그 확인
tail -f /var/log/mysql/error.log  # Linux
```

### 3. 방화벽 문제
```bash
# Windows 방화벽 규칙 확인
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*AI*"}

# Linux 방화벽 상태 확인
sudo ufw status
```

## 📱 모바일/태블릿 접속

### 1. 같은 Wi-Fi 네트워크
- `http://[서버로컬IP]:5000` 접속
- 예: `http://192.168.1.100:5000`

### 2. 외부 네트워크
- `http://[서버공인IP]:5000` 접속
- 공유기 포트포워딩 설정 필요

## 🔄 자동 시작 설정

### Windows 서비스 등록
```cmd
# 관리자 권한으로 실행
sc create "AI추천시스템" binPath="python C:\path\to\improved_recommendation.py"
sc start "AI추천시스템"
```

### Linux systemd 서비스
```bash
# /etc/systemd/system/ai-recommendation.service
[Unit]
Description=AI Job Recommendation System
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/path/to/project
ExecStart=/usr/bin/python3 improved_recommendation.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 서비스 활성화
sudo systemctl enable ai-recommendation
sudo systemctl start ai-recommendation
```

## 📊 모니터링

### 1. 로그 확인
```bash
# 실시간 로그
tail -f app.log

# 에러 로그만
grep "ERROR" app.log
```

### 2. 성능 모니터링
```bash
# CPU/메모리 사용량
top
htop

# 네트워크 연결
netstat -an | grep :5000
```

## 🎯 다음 단계

1. **로드 밸런서 설정**: 여러 서버로 트래픽 분산
2. **데이터베이스 클러스터**: 고가용성 확보
3. **캐싱 시스템**: Redis 등으로 성능 향상
4. **모니터링 도구**: Prometheus, Grafana 등
5. **CI/CD 파이프라인**: 자동 배포 설정

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. 방화벽 설정
2. MySQL 외부 접속 허용
3. 포트 5000 사용 가능 여부
4. 서버 공인 IP 주소
5. 네트워크 연결 상태


