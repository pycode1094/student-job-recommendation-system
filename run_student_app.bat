@echo off
echo 🎯 학생 맞춤 채용 추천 시스템을 시작합니다...
echo.
echo 📋 필요한 패키지를 설치합니다...
pip install streamlit plotly

echo.
echo 🚀 Streamlit 앱을 실행합니다...
echo 🌐 브라우저에서 http://localhost:8503 을 열어주세요
echo.
echo ⚠️  앱을 종료하려면 Ctrl+C를 누르세요
echo.

streamlit run student_recommendation_app.py --server.port 8503 --server.address localhost

pause
