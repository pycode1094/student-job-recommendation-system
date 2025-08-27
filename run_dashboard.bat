@echo off
echo AI Job Recommendation Dashboard 시작 중...
echo.
echo 같은 사무실 직원들이 접근할 수 있는 주소:
echo Network URL: http://10.10.11.53:8501
echo.
echo 브라우저에서 위 주소로 접근하세요.
echo.
echo 종료하려면 Ctrl+C를 누르세요.
echo.
streamlit run job_recommendation_dashboard.py --server.port 8501 --server.address 0.0.0.0
pause
