@echo off
echo ========================================================
echo   REVIEW LENS V2 - NOCTURNAL PERFORMANCE SUITE
echo ========================================================
echo.
echo Starting FastAPI Backend Engine on http://127.0.0.1:8000...
start "ReviewLens Backend" cmd /k "set PYTHONPATH=%CD%;%CD%\backend&& python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

echo.
echo Starting Vite Frontend on http://127.0.0.1:5173...
start "ReviewLens Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Both servers launched! Open your browser at:
echo   http://127.0.0.1:5173
echo ========================================================
