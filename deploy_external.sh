#!/bin/bash

echo "========================================"
echo "    AI 직업 추천 시스템 외부 배포"
echo "========================================"
echo

echo "📦 필요한 패키지 설치 중..."
pip3 install -r requirements.txt

echo
echo "🔧 환경 변수 설정..."
export DB_HOST=0.0.0.0
export DB_PORT=3306
export DB_USER=root
export DB_PASSWORD=15861
export DB_NAME=job_recoder

echo
echo "🌐 웹 서버 시작 중..."
echo "서버 주소: http://0.0.0.0:5000"
echo "외부 접속: http://[서버공인IP]:5000"
echo
echo "⚠️  외부 접속을 위해서는:"
echo "1. 방화벽에서 5000번 포트를 열어주세요"
echo "2. MySQL에서 외부 접속을 허용해주세요"
echo "3. 서버의 공인 IP 주소를 확인하세요"
echo

echo "🚀 서버 시작..."
python3 improved_recommendation.py

