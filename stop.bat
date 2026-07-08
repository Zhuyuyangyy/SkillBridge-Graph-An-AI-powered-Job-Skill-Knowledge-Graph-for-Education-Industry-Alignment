@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo  Shurong Zhilian Stop
echo ==========================================
echo.

call :kill_port 8000 Backend
call :kill_port 5173 Frontend

echo Closing service command windows...
taskkill /F /FI "WINDOWTITLE eq shurong-zhilian-backend*" >nul 2>nul
taskkill /F /FI "WINDOWTITLE eq shurong-zhilian-frontend*" >nul 2>nul

echo.
echo Stop commands have been executed.
echo If a port is still occupied, close the related command window and run this file again.
pause
exit /b 0

:kill_port
set "PORT=%~1"
set "NAME=%~2"
set "FOUND=0"

for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":%PORT% .*LISTENING"') do (
  set "PID=%%P"
  set "FOUND=1"
  echo Stopping %NAME% on port %PORT% ^(PID !PID!^)...
  taskkill /F /PID !PID! >nul 2>nul
  if errorlevel 1 (
    echo [WARN] Failed to stop PID !PID!. It may have already exited.
  ) else (
    echo [OK] %NAME% stopped.
  )
)

if "%FOUND%"=="0" (
  echo [OK] No %NAME% service found on port %PORT%.
)
exit /b 0
