"""
Main application routes (home, profile, etc.)
"""
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import logging
import pandas as pd

from ..auth_utils import get_current_user
from ..models import User
from ..restaurant_service import find_restaurants, load_data

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)


@router.get("/", response_class=HTMLResponse)
async def home():
    """Redirect to welcome page"""
    return RedirectResponse(url="/welcome")


@router.get("/welcome", response_class=HTMLResponse)
async def welcome_page(request: Request):
    """Display landing page"""
    return templates.TemplateResponse("landing.html", {"request": request})


@router.get("/app", response_class=HTMLResponse)
async def app_home(request: Request, current_user: User = Depends(get_current_user)):
    """Display main app page (requires authentication)"""
    return templates.TemplateResponse("index.html", {"request": request, "user": current_user})


@router.get("/find-restaurants", response_class=HTMLResponse)
async def find_restaurants_page(request: Request, current_user: User = Depends(get_current_user)):
    """Display restaurant finder page"""
    return templates.TemplateResponse("find_restaurants.html", {
        "request": request, 
        "user": current_user
    })


@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, current_user: User = Depends(get_current_user)):
    """Display user profile page"""
    return templates.TemplateResponse("profile.html", {"request": request, "user": current_user})


@router.post("/search")
async def search_restaurants(dish: str = Form(...), location: str = Form(...)):
    """Search for restaurants"""
    try:
        # First try exact match
        results = find_restaurants(dish, location)
        
        # If no results, try a more flexible search
        if not results:
            data = load_data()
            if data is not None and not data.empty:
                # Try matching just the city if full location didn't work
                city = location.split(',')[0].strip()
                if city != location:
                    results = find_restaurants(dish, city)
        
        return {"success": True, "results": results}
    except Exception as e:
        logger.error(f"Error in search: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}


@router.get("/api/cities")
async def get_cities():
    """Get list of all available cities"""
    try:
        df = load_data()
        if df is None or df.empty:
            return {"error": "No data available"}
        
        # Get unique cities, sort them, and remove any NaN/None values
        cities = sorted(set(loc.split(',')[0].strip() for loc in df['location'].dropna().astype(str) if loc))
        return {"cities": cities}
    except Exception as e:
        logger.error(f"Error getting cities: {str(e)}")
        return {"error": str(e)}


@router.get("/api/sublocations")
async def get_sublocations(city: str):
    """Get sub-locations for a given city"""
    try:
        df = load_data()
        if df is None or df.empty:
            return {"sublocations": []}
        
        city_lower = city.lower()
        sublocations = set()
        
        # Get localities from the 'locality' column
        if 'locality' in df.columns:
            city_matches = df[df['location'].str.lower().str.contains(city_lower, na=False)]
            localities = city_matches['locality'].dropna().unique()
            
            for loc in localities:
                if pd.notna(loc) and str(loc).strip() and str(loc).lower() != city_lower:
                    sublocations.add(str(loc).strip())
        
        # Convert to list and sort
        sublocations = sorted(list(sublocations), key=lambda x: x.lower())
        
        # Add 'All Areas' as the first option
        sublocations = ["All Areas"] + sublocations
        
        return {"sublocations": sublocations}
        
    except Exception as e:
        logger.error(f"Error getting sub-locations: {str(e)}", exc_info=True)
        return {"error": str(e)}


@router.get("/api/dishes")
async def get_dishes(city: str = None, sublocation: str = None):
    """Get list of all available dishes, optionally filtered by city and sub-location"""
    try:
        df = load_data()
        if df is None or df.empty:
            return {"error": "No data available"}
        
        # Filter by city and sub-location if provided
        if city:
            df = df[df['location'].str.lower().str.contains(city.lower(), na=False)]
            if sublocation:
                df = df[df['location'].str.lower().str.contains(sublocation.lower(), na=False)]
        
        # Extract all unique cuisines and dishes
        all_dishes = set()
        for cuisines in df['cuisines'].dropna():
            # Split cuisines by comma and clean up
            dishes = [dish.strip().lower() for dish in cuisines.split(',')]
            all_dishes.update(dishes)
        
        # Sort dishes alphabetically
        dishes = sorted(all_dishes)
        return {"dishes": dishes}
    except Exception as e:
        logger.error(f"Error getting dishes: {str(e)}")
        return {"error": str(e)}
