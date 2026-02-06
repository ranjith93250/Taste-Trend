from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import pickle
import os

app = FastAPI(title="Recommender Service API", version="1.0.0")

class UserRequest(BaseModel):
    user_id: int

class RecommendationResponse(BaseModel):
    recommendations: List[str]

# Dummy recommendation data
DUMMY_DISHES = [
    "Chicken Biryani",
    "Margherita Pizza", 
    "Beef Burger",
    "Sushi Roll",
    "Pasta Carbonara",
    "Fish and Chips",
    "Tacos",
    "Pad Thai",
    "Caesar Salad",
    "Chocolate Cake"
]

@app.get("/")
def home():
    return {"message": "Recommender Service API is running"}

@app.post("/recommend", response_model=RecommendationResponse)
def recommend(user_request: UserRequest):
    """
    Get food recommendations for a user based on their user_id
    """
    user_id = user_request.user_id
    
    # Dummy recommendation logic - return first 3 dishes for now
    # In a real implementation, this would use the trained model
    recommendations = DUMMY_DISHES[:3]
    
    return RecommendationResponse(recommendations=recommendations)

def create_placeholder_model():
    """
    Create a placeholder model file for demonstration purposes
    """
    # Create a simple placeholder model (just a dictionary for now)
    placeholder_model = {
        "model_type": "recommendation_model",
        "version": "1.0.0",
        "features": ["user_id", "dish_ratings", "cuisine_preferences"],
        "dummy_data": True
    }
    
    # Save as pickle file
    with open("model.pkl", "wb") as f:
        pickle.dump(placeholder_model, f)
    
    print("Placeholder model saved as model.pkl")

if __name__ == "__main__":
    # Create placeholder model if it doesn't exist
    if not os.path.exists("model.pkl"):
        create_placeholder_model()
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)