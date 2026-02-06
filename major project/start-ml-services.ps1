Write-Host "Starting ML Services..." -ForegroundColor Green

Write-Host "Starting Recommender Service on port 8001..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'ml-services\recommender'; uvicorn app:app --host 0.0.0.0 --port 8001"

Write-Host "Starting Sentiment Service on port 8002..." -ForegroundColor Yellow  
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'ml-services\sentiment'; uvicorn app:app --host 0.0.0.0 --port 8002"

Write-Host "Starting Trend Service on port 8003..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'ml-services\trend'; uvicorn app:app --host 0.0.0.0 --port 8003"

Write-Host "All ML services started!" -ForegroundColor Green
Write-Host "- Recommender: http://localhost:8001" -ForegroundColor Cyan
Write-Host "- Sentiment: http://localhost:8002" -ForegroundColor Cyan
Write-Host "- Trend: http://localhost:8003" -ForegroundColor Cyan

Read-Host "Press Enter to continue"
