@echo off
echo Starting Todo App Servers...

echo Starting backend server on port 8000...
start cmd /k "cd /d backend && python -m uvicorn src.main:app --reload --port 8000"

echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo Starting frontend server on port 3000...
start cmd /k "cd /d frontend && npm run dev"

echo.
echo Both servers started!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo Chat Interface: http://localhost:3000/chat
pause