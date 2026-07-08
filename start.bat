@echo off
setlocal

set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "FRONTEND=%ROOT%frontend"

echo ==========================================
echo  Shurong Zhilian Startup
echo ==========================================
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python was not found. Please install Python 3.10 or later.
  pause
  exit /b 1
)

where npm.cmd >nul 2>nul
if errorlevel 1 (
  echo [ERROR] npm was not found. Please install Node.js first.
  pause
  exit /b 1
)

echo [1/4] Checking backend dependencies...
cd /d "%BACKEND%"
python -c "import fastapi, sqlalchemy, uvicorn" >nul 2>nul
if errorlevel 1 (
  echo Installing backend dependencies...
  pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
  if errorlevel 1 (
    echo [ERROR] Backend dependency installation failed.
    pause
    exit /b 1
  )
)

echo [2/4] Initializing database...
python -m app.db.init_db
if errorlevel 1 (
  echo [ERROR] Database initialization failed.
  pause
  exit /b 1
)

echo [3/4] Checking frontend dependencies...
cd /d "%FRONTEND%"
if not exist "node_modules" (
  echo Installing frontend dependencies...
  call npm install
  if errorlevel 1 (
    echo [ERROR] Frontend dependency installation failed.
    pause
    exit /b 1
  )
)

echo [4/4] Starting services...
netstat -ano | findstr /R /C:":8000 .*LISTENING" >nul 2>nul
if errorlevel 1 (
  start "shurong-zhilian-backend" /D "%BACKEND%" cmd /k "python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
) else (
  echo Backend is already running on port 8000.
)

netstat -ano | findstr /R /C:":5173 .*LISTENING" >nul 2>nul
if errorlevel 1 (
  start "shurong-zhilian-frontend" /D "%FRONTEND%" cmd /k "npm run dev -- --host 127.0.0.1 --port 5173"
) else (
  echo Frontend is already running on port 5173.
)

echo.
echo Backend:  http://127.0.0.1:8000
echo API docs: http://127.0.0.1:8000/docs
echo Frontend: http://127.0.0.1:5173
echo.
echo Opening browser...
timeout /t 3 /nobreak >nul
start http://127.0.0.1:5173

echo Startup commands have been executed.
echo Keep the backend and frontend command windows open while using the system.
pause
