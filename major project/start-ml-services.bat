@echo off
echo Starting ML Services...

echo Starting Recommender Service on port 8001...
start "Recommender Service" cmd /k "cd ml-services\recommender && uvicorn app:app --host 0.0.0.0 --port 8001"

echo Starting Sentiment Service on port 8002...
start "Sentiment Service" cmd /k "cd ml-services\sentiment && uvicorn app:app --host 0.0.0.0 --port 8002"

echo Starting Trend Service on port 8003...
start "Trend Service" cmd /k "cd ml-services\trend && uvicorn app:app --host 0.0.0.0 --port 8003"

echo All ML services started!
echo - Recommender: http://localhost:8001
echo - Sentiment: http://localhost:8002  
echo - Trend: http://localhost:8003
pause
