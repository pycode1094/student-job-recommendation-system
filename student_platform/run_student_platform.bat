@echo off
echo 학생용 취업지원 플랫폼 시작 중...
echo.
echo 학생용 로그인 페이지가 실행됩니다.
echo 브라우저에서 http://localhost:8502 로 접근하세요.
echo.
echo 종료하려면 Ctrl+C를 누르세요.
echo.
streamlit run student_login.py --server.port 8502 --server.address 0.0.0.0
pause
