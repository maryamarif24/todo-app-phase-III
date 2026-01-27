@echo on
echo Killing processes on ports 3000-3007 and 8000...

REM Kill processes on port 8000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    echo Killing process %%a on port 8000
    taskkill /f /pid %%a 2>nul
)

REM Kill processes on ports 3000-3007
for /L %%i in (3000,1,3007) do (
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%%i ^| findstr LISTENING') do (
        echo Killing process %%a on port %%i
        taskkill /f /pid %%a 2>nul
    )
)

echo Done killing processes.
pause