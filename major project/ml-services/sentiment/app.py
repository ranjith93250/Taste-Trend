from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal

app = FastAPI(title="Sentiment Analysis Service API", version="1.0.0")

class ReviewRequest(BaseModel):
    review: str

class SentimentResponse(BaseModel):
    sentiment: Literal["positive", "negative"]

@app.get("/")
def home():
    return {"message": "Sentiment Analysis Service API is running"}

@app.post("/analyze", response_model=SentimentResponse)
def analyze_sentiment(review_request: ReviewRequest):
    """
    Analyze sentiment of a review text
    """
    review = review_request.review
    
    # Dummy sentiment analysis logic
    # In a real implementation, this would use a trained ML model
    # For now, return positive for reviews with positive keywords, negative otherwise
    positive_keywords = ["good", "great", "excellent", "amazing", "delicious", "love", "best", "wonderful", "fantastic", "perfect"]
    negative_keywords = ["bad", "terrible", "awful", "hate", "worst", "disgusting", "horrible", "disappointed", "poor", "sucks"]
    
    review_lower = review.lower()
    
    positive_count = sum(1 for word in positive_keywords if word in review_lower)
    negative_count = sum(1 for word in negative_keywords if word in review_lower)
    
    # Simple logic: if more positive keywords than negative, return positive
    sentiment = "positive" if positive_count >= negative_count else "negative"
    
    return SentimentResponse(sentiment=sentiment)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)