@echo off
chcp 65001 >nul
title AI 활용 아이디어경진대회 - 대시보드 실행

echo.
echo ========================================
echo    AI 활용 아이디어경진대회 대시보드
echo ========================================
echo.
echo 🚀 관리자 대시보드와 학생 플랫폼을 동시에 실행합니다...
echo.

REM 현재 디렉토리 확인
echo 📁 현재 작업 디렉토리: %CD%
echo.

REM 포트 사용 확인
echo 🔍 포트 사용 현황 확인 중...
netstat -ano | findstr :8501 >nul
if %errorlevel% equ 0 (
    echo ⚠️  포트 8501이 이미 사용 중입니다.
    echo    기존 프로세스를 종료하시겠습니까? (Y/N)
    set /p choice=
    if /i "%choice%"=="Y" (
        for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8501') do taskkill /f /pid %%a >nul 2>&1
        echo ✅ 포트 8501 프로세스가 종료되었습니다.
    )
)

netstat -ano | findstr :8502 >nul
if %errorlevel% equ 0 (
    echo ⚠️  포트 8502가 이미 사용 중입니다.
    echo    기존 프로세스를 종료하시겠습니까? (Y/N)
    set /p choice=
    if /i "%choice%"=="Y" (
        for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8502') do taskkill /f /pid %%a >nul 2>&1
        echo ✅ 포트 8502 프로세스가 종료되었습니다.
    )
)

echo.
echo 🎯 대시보드 실행 중...
echo.

REM 관리자 대시보드 실행 (백그라운드)
echo 📊 관리자 대시보드 실행 중... (포트 8501)
start "관리자 대시보드" cmd /k "cd /d %CD% && streamlit run job_recommendation_dashboard.py --server.port 8501 --server.address 0.0.0.0"

REM 잠시 대기
timeout /t 3 /nobreak >nul

REM 학생 플랫폼 실행 (백그라운드)
echo 🎓 학생 플랫폼 실행 중... (포트 8502)
start "학생 플랫폼" cmd /k "cd /d %CD%\student_platform && streamlit run student_login.py --server.port 8502 --server.address 0.0.0.0"

echo.
echo ✅ 두 대시보드가 모두 실행되었습니다!
echo.
echo 🌐 접속 주소:
echo    📊 관리자 대시보드: http://localhost:8501
echo    🎓 학생 플랫폼: http://localhost:8502
echo.
echo 💡 사용 방법:
echo    - 관리자 대시보드: 전체 데이터 분석 및 관리
echo    - 학생 플랫폼: 학번으로 로그인하여 개인 대시보드 이용
echo.
echo ⚠️  종료하려면 각 창에서 Ctrl+C를 누르거나 창을 닫으세요.
echo.
pause
