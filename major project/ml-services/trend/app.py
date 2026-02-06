from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Trend Analysis Service API", version="1.0.0")

class TrendResponse(BaseModel):
    trending_dishes: List[str]

@app.get("/")
def home():
    return {"message": "Trend Analysis Service API is running"}

@app.get("/trend", response_model=TrendResponse)
def get_trending_dishes():
    """
    Get trending dishes based on current food trends
    """
    # Dummy trending dishes data
    # In a real implementation, this would analyze social media, search trends, etc.
    trending_dishes = ["Pizza", "Biryani", "Pasta"]
    
    return TrendResponse(trending_dishes=trending_dishes)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)