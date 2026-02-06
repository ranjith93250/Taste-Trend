from fastapi import FastAPI, Request, Form, HTTPException, Depends, status, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import pandas as pd
import os
import json
import csv
from pydantic import BaseModel
import uvicorn
import logging
import sys

# Import the database connection
from database import db

# Configure logging
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)

# File handler
file_handler = logging.FileHandler('app.log')
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)

# Log unhandled exceptions
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception
logger = logging.getLogger(__name__)

# Import the database connection
from database import db

# Import authentication modules
from auth import (
    get_current_user,
    authenticate_user,
    create_access_token,
    get_password_hash,
    User,
    UserInDB,
    Token,
    SECRET_KEY,
    ALGORITHM,
    pwd_context
)

# Security
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Token settings
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(title="Success Map - Career Guidance")

class LoginForm:
    def __init__(self, request: Request):
        self.request = request
        self.username: str = ""
        self.password: str = ""

    async def load_data(self):
        form = await self.request.form()
        self.username = form.get("username")
        self.password = form.get("password")

class SignupForm:
    def __init__(self, request: Request):
        self.request = request
        self.full_name: str = ""
        self.email: str = ""
        self.password: str = ""
        self.confirm_password: str = ""
        
    async def load_data(self):
        form = await self.request.form()
        self.full_name = form.get("full_name", "").strip()
        self.email = form.get("email", "").strip().lower()
        self.password = form.get("password", "")
        self.confirm_password = form.get("confirm_password", "")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_user(email: str):
    user_data = users_collection.find_one({"email": email})
    if user_data:
        return UserInDB(**user_data)
    return None

def authenticate_user(email: str, password: str):
    user = get_user(email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# Global variable to store the restaurant data
df = None

def load_data():
    global df
    if df is not None:
        return df
        
    print("\n=== Starting to load data ===")
    
    # Possible paths to the dataset
    possible_paths = [
        os.path.join('major project', 'zomato_restaurants_in_India.csv'),
        os.path.join('major project', 'zomato_restaurants_in_India.csv.zip'),
        'zomato_restaurants_in_India.csv',
        'zomato_restaurants_in_India.csv.zip'
    ]
    
    try:
        # Try each possible path
        for path in possible_paths:
            full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
            print(f"Trying path: {full_path}")
            
            if os.path.exists(full_path):
                print(f"Found file at: {full_path}")
                
                # If it's a CSV file
                if full_path.endswith('.csv'):
                    try:
                        df = pd.read_csv(full_path, low_memory=False)
                        print(f"Successfully loaded {len(df)} rows from CSV")
                        print(f"Available columns: {', '.join(df.columns.tolist())}")
                        break
                    except Exception as e:
                        print(f"Error reading CSV: {e}")
                
                # If it's a zip file
                elif full_path.endswith('.zip'):
                    try:
                        # Try to extract to the same directory
                        extract_dir = os.path.dirname(full_path)
                        with zipfile.ZipFile(full_path, 'r') as zip_ref:
                            zip_ref.extractall(extract_dir)
                        print("Successfully extracted the zip file")
                        
                        # Look for the extracted CSV
                        csv_path = full_path.replace('.zip', '')
                        if os.path.exists(csv_path):
                            try:
                                df = pd.read_csv(csv_path, low_memory=False)
                                print(f"Successfully loaded {len(df)} rows from extracted CSV")
                                print(f"Available columns: {', '.join(df.columns.tolist())}")
                                break
                            except Exception as e:
                                print(f"Error reading extracted CSV: {e}")
                        else:
                            print(f"Error: Extracted CSV not found at {csv_path}")
                    except Exception as e:
                        print(f"Error extracting zip file: {e}")
        
        if df is None:
            print("Error: Could not find or load the dataset file.")
            return None
            
        # Define column mappings
        column_mappings = {
            'name': 'restaurant_name',
            'restaurant_name': 'restaurant_name',
            'city': 'location',
            'locality': 'locality',
            'address': 'address',
            'cuisines': 'cuisines',
            'aggregate_rating': 'rating',
            'rating_text': 'rating_text',
            'votes': 'votes',
            'average_cost_for_two': 'average_cost_for_two',
            'thumb': 'image_url',
            'featured_image': 'image_url',
            'photos_url': 'image_url',
            'menu_url': 'menu_url',
            'url': 'url',
            'timings': 'timings',
            'highlights': 'highlights'
        }
        
        # Only use columns that exist in the dataframe
        columns_to_keep = {k: v for k, v in column_mappings.items() if k in df.columns}
        
        # Rename columns
        df = df.rename(columns=columns_to_keep)
        
        # Keep only the columns we need
        df = df[list(set(columns_to_keep.values()))]
        
        # Add any missing columns with default values
        for col in ['rating', 'votes', 'average_cost_for_two', 'locality', 'address', 'cuisines']:
            if col not in df.columns:
                df[col] = ''
        
        # Convert data types
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0)
        df['votes'] = pd.to_numeric(df['votes'], errors='coerce').fillna(0).astype(int)
        df['average_cost_for_two'] = pd.to_numeric(df['average_cost_for_two'], errors='coerce').fillna(0).astype(int)
        
        # Clean up text data
        for col in ['restaurant_name', 'location', 'locality', 'address', 'cuisines']:
            if col in df.columns:
                df[col] = df[col].fillna('').astype(str).str.strip()
        
        # Create a combined location string if locality is available
        if 'locality' in df.columns and 'location' in df.columns:
            df['location'] = df.apply(
                lambda x: f"{x['location']}, {x['locality']}" if x['locality'] and x['locality'] != x['location'] else x['location'],
                axis=1
            )
        
        print(f"Successfully processed {len(df)} restaurants")
        return df
        
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def find_restaurants(dish: str, location: str, top_n: int = 10) -> List[Dict[str, Any]]:
    """
    Find restaurants serving a specific dish in a given location.
    
    Args:
        dish (str): The dish or cuisine to search for
        location (str): The location to search in (can be city or specific area)
        top_n (int): Maximum number of results to return
        
    Returns:
        List[Dict]: List of restaurant dictionaries with complete details
    """
    try:
        df = load_data()
        if df is None or df.empty:
            print("Error: No data loaded")
            return []
            
        print(f"\n=== New Search ===")
        print(f"Dish: {dish}")
        print(f"Location: {location}")
        print(f"Total restaurants in dataset: {len(df)}")
        print("Sample locations:", df['location'].dropna().unique()[:5])
        
        # Convert to lowercase for case-insensitive search
        dish_terms = [d.strip().lower() for d in dish.split() if d.strip()]
        location_terms = [loc.strip().lower() for loc in location.split(',') if loc.strip()]
        
        print(f"Searching for dish terms: {dish_terms}")
        print(f"Searching in location terms: {location_terms}")
        
        # First filter by location (more restrictive filter first)
        location_columns = ['location', 'locality', 'address']
        location_columns = [col for col in location_columns if col in df.columns]
        
        # Create a combined search string for location
        def create_location_string(row):
            return ' '.join(str(row[col]).lower() for col in location_columns if col in row and pd.notna(row[col]))
            
        df['location_search'] = df.apply(create_location_string, axis=1)
        
        # Create a filter that requires ALL location terms to match
        location_filter = df['location_search'].apply(
            lambda x: all(term in str(x).lower() for term in location_terms)
        )
        
        filtered_df = df[location_filter].copy()
        
        if filtered_df.empty:
            print(f"No restaurants found in location: {location}")
            print("Sample location strings:", df['location_search'].head().tolist())
            return []
            
        print(f"Found {len(filtered_df)} restaurants in location")
        
        # Filter by dish (checking in multiple columns)
        dish_columns = ['cuisines', 'restaurant_name', 'name', 'menu_dish', 'dish_name']
        dish_columns = [col for col in dish_columns if col in filtered_df.columns]
        
        # Create a combined search string for each row
        def create_search_string(row):
            return ' '.join(str(row[col]).lower() for col in dish_columns if col in row and pd.notna(row[col]))
            
        filtered_df['search_string'] = filtered_df.apply(create_search_string, axis=1)
        
        # Create a filter that requires ANY dish term to match (more permissive)
        def dish_match(search_str):
            search_str = str(search_str).lower()
            return any(term in search_str for term in dish_terms)
            
        dish_filter = filtered_df['search_string'].apply(dish_match)
        results_df = filtered_df[dish_filter].copy()
        
        if results_df.empty:
            print(f"No restaurants found serving '{dish}' in {location}")
            print("Sample search strings:", filtered_df['search_string'].head().tolist())
            # Try a more permissive search with just the first term
            if len(dish_terms) > 1:
                first_term = dish_terms[0]
                print(f"Trying more permissive search with term: {first_term}")
                dish_filter = filtered_df['search_string'].str.contains(first_term, case=False, na=False)
                results_df = filtered_df[dish_filter].copy()
                
                if results_df.empty:
                    print("Still no results with permissive search")
                    return []
                print(f"Found {len(results_df)} restaurants with permissive search")
            else:
                return []
        else:
            print(f"Found {len(results_df)} restaurants serving '{dish}'")
        
        # Get unique restaurants (keep first occurrence)
        results_df = results_df.drop_duplicates(subset=['restaurant_name', 'location'])
        
        # Convert to list of dictionaries with complete details
        restaurants = []
        for _, row in results_df.iterrows():
            # Process URL
            url = None
            if 'url' in row and pd.notna(row['url']) and row['url'] not in ['', 'nan', 'NaN']:
                url = str(row['url']).strip()
                if not url.startswith(('http://', 'https://')):
                    url = f'https://www.zomato.com{url}' if url.startswith('/') else f'https://www.zomato.com/{url}'
            
            # Process timings
            timings = None
            if 'timings' in row and pd.notna(row['timings']):
                timings = row['timings']
                if isinstance(timings, str) and timings.startswith('[') and timings.endswith(']'):
                    try:
                        timings = eval(timings)  # Convert string representation of list to actual list
                        timings = ', '.join([str(t).strip() for t in timings if str(t).strip()])
                    except:
                        timings = str(timings)
            
            # Process highlights
            highlights = None
            if 'highlights' in row and pd.notna(row['highlights']):
                highlights = row['highlights']
                if isinstance(highlights, str) and highlights.startswith('[') and highlights.endswith(']'):
                    try:
                        highlights = eval(highlights)  # Convert string representation of list to actual list
                        highlights = [h.strip() for h in highlights if h and str(h).strip()]
                    except:
                        highlights = [str(highlights)]
                elif isinstance(highlights, str):
                    highlights = [h.strip() for h in highlights.split(',') if h.strip()]
            
            restaurant = {
                'restaurant_name': row.get('restaurant_name', row.get('name', 'Unnamed Restaurant')),
                'address': row.get('address', row.get('location', 'Address not available')),
                'locality': row.get('locality', 'Locality not available'),
                'city': row.get('city', row.get('location', 'City not available')),
                'cuisines': row.get('cuisines', 'Cuisines not specified'),
                'url': url,
                'menu_url': row.get('menu_url', None),
                'image_url': row.get('image_url', None),
                'rating': float(row['rating']) if 'rating' in row and pd.notna(row['rating']) and str(row['rating']).replace('.', '').isdigit() else None,
                'rating_text': row.get('rating_text', 'No rating'),
                'votes': int(float(row['votes'])) if 'votes' in row and pd.notna(row['votes']) and str(row['votes']).replace('.', '').isdigit() else 0,
                'average_cost_for_two': int(float(row['average_cost_for_two'])) if 'average_cost_for_two' in row and pd.notna(row['average_cost_for_two']) and str(row['average_cost_for_two']).replace('.', '').isdigit() else None,
                'price_range': row.get('price_range', 'Price not available'),
                'currency': row.get('currency', 'INR'),
                'highlights': highlights,
                'timings': timings,
                'delivery': row.get('delivery', 'Not specified'),
                'takeaway': row.get('takeaway', 'Not specified')
            }
            restaurants.append(restaurant)
        
        # Sort by rating (highest first) and limit to top_n results
        restaurants.sort(key=lambda x: (x['rating'] is not None, x['rating'] or 0), reverse=True)
        restaurants = restaurants[:top_n]
        
        print(f"Returning {len(restaurants)} restaurants")
        if restaurants:
            print("Sample restaurant:", {
                'name': restaurants[0]['restaurant_name'],
                'location': restaurants[0].get('location', 'N/A'),
                'rating': restaurants[0].get('rating', 'N/A'),
                'cuisines': restaurants[0].get('cuisines', 'N/A')
            })
        
        return restaurants
        
    except Exception as e:
        print(f"Error in find_restaurants: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

@app.get("/api/cities")
async def get_cities():
    """Get list of all available cities."""
    try:
        df = load_data()
        if df is None or df.empty:
            return {"error": "No data available"}
        
        # Get unique cities (first word of location), sort them, and remove any NaN/None values
        cities = sorted(set(loc.split(',')[0].strip() for loc in df['location'].dropna().astype(str) if loc))
        return {"cities": cities}
    except Exception as e:
        print(f"Error getting cities: {str(e)}")
        return {"error": str(e)}

@app.get("/api/sublocations")
async def get_sublocations(city: str):
    """Get sub-locations for a given city using the 'locality' column."""
    try:
        df = load_data()
        if df is None or df.empty:
            return {"sublocations": []}
        
        # Convert city to lowercase for case-insensitive comparison
        city_lower = city.lower()
        
        # Initialize a set to store unique sub-locations
        sublocations = set()
        
        # First, try to get localities from the 'locality' column
        if 'locality' in df.columns:
            # Get all rows where location contains the city name (case-insensitive)
            city_matches = df[df['location'].str.lower().str.contains(city_lower, na=False)]
            
            # Extract unique localities
            localities = city_matches['locality'].dropna().unique()
            
            # Add all non-empty localities to our set
            for loc in localities:
                if pd.notna(loc) and str(loc).strip() and str(loc).lower() != city_lower:
                    sublocations.add(str(loc).strip())
        
        # Also parse the location column for additional sub-locations
        city_matches = df[df['location'].str.lower().str.contains(city_lower, na=False)]
        for loc in city_matches['location'].dropna().unique():
            # Split by common separators and clean up
            parts = []
            for sep in [',', '/', '|', '-']:
                if sep in str(loc):
                    parts = [p.strip() for p in str(loc).split(sep) if p.strip()]
                    break
            
            # If we have multiple parts and the first part is the city
            if len(parts) > 1 and parts[0].lower() == city_lower:
                # Add all subsequent parts as sub-locations
                for part in parts[1:]:
                    part = part.strip()
                    if part and part.lower() != city_lower:
                        sublocations.add(part)
        
        # Convert to list and sort
        sublocations = sorted(list(sublocations), key=lambda x: x.lower())
        
        # Add 'All Areas' as the first option
        sublocations = ["All Areas"] + sublocations
        
        return {"sublocations": sublocations}
        
    except Exception as e:
        print(f"Error getting sub-locations: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@app.get("/api/dishes")
async def get_dishes(city: str = None, sublocation: str = None):
    """Get list of all available dishes, optionally filtered by city and sub-location."""
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
        print(f"Error getting dishes: {str(e)}")
        return {"error": str(e)}

@app.get("/", response_class=HTMLResponse)
async def home():
    return RedirectResponse(url="/welcome")

@app.get("/welcome", response_class=HTMLResponse)
async def welcome_page(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/app", response_class=HTMLResponse)
async def app_home(request: Request, current_user: User = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/welcome")
    return templates.TemplateResponse("index.html", {"request": request, "user": current_user})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup")
async def signup(request: Request):
    try:
        logger.info("Received signup request")
        form = await request.form()
        email = form.get("email", "").strip().lower()
        password = form.get("password", "")
        confirm_password = form.get("confirm_password", "")
        full_name = form.get("full_name", "").strip()
        
        logger.debug(f"Form data - Email: {email}, Name: {full_name}")
        
        # Validate required fields
        if not all([email, password, confirm_password, full_name]):
            error_msg = f"Missing required fields. Email: {bool(email)}, Password: {bool(password)}, Confirm: {bool(confirm_password)}, Name: {bool(full_name)}"
            logger.warning(error_msg)
            return templates.TemplateResponse(
                "signup.html",
                {"request": request, "error": "All fields are required"},
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        # Validate email format
        if "@" not in email or "." not in email:
            return templates.TemplateResponse(
                "signup.html",
                {"request": request, "error": "Please enter a valid email address"},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate passwords match
        if password != confirm_password:
            return templates.TemplateResponse(
                "signup.html",
                {"request": request, "error": "Passwords do not match"},
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        # Validate password strength
        if len(password) < 8:
            return templates.TemplateResponse(
                "signup.html",
                {"request": request, "error": "Password must be at least 8 characters long"},
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        # Check password length (in bytes) to ensure it's not too long for bcrypt
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            return templates.TemplateResponse(
                "signup.html",
                {"request": request, "error": "Password is too long. Please use 72 characters or fewer."},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Check if user already exists
        logger.debug(f"Checking if user {email} already exists")
        try:
            existing_user = db.users.find_one({"email": email})
            if existing_user:
                logger.warning(f"Registration attempt with existing email: {email}")
                return templates.TemplateResponse(
                    "signup.html",
                    {"request": request, "error": "Email already registered"},
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            # Create user
            logger.debug("Creating new user document")
            try:
                hashed_password = get_password_hash(password)
                user_dict = {
                    "email": email,
                    "full_name": full_name,
                    "hashed_password": hashed_password,
                    "disabled": False,
                    "created_at": datetime.utcnow()
                }
                logger.debug(f"User document prepared: {user_dict}")
            except Exception as e:
                logger.error(f"Error preparing user document: {str(e)}")
                raise

            # Insert user into database
            result = db.users.insert_one(user_dict)
            logger.info(f"User {email} created successfully with ID: {result.inserted_id}")
            
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            return templates.TemplateResponse(
                "signup.html",
                {"request": request, "error": "Database error. Please try again later."},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Log the user in automatically after signup
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": email}, expires_delta=access_token_expires
        )
        
        # Set the access token in a secure HTTP-only cookie
        response = RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax"
        )
        return response
        
    except Exception as e:
        error_msg = f"Error during signup: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "error": f"An error occurred during registration: {str(e)}"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("profile.html", {"request": request, "user": current_user})

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie("access_token")
    return response

@app.post("/search")
async def search_restaurants(dish: str = Form(...), location: str = Form(...)):
    try:
        # First try exact match
        results = find_restaurants(dish, location)
        
        # If no results, try a more flexible search
        if not results:
            df = load_data()
            if df is not None and not df.empty:
                # Try matching just the city if full location didn't work
                city = location.split(',')[0].strip()
                if city != location:
                    results = find_restaurants(dish, city)
        
        # Add direct URLs to results
        if results:
            df = load_data()
            if df is not None and not df.empty:
                for result in results:
                    # Find the restaurant in the original data to get the URL
                    restaurant_data = df[
                        (df['restaurant_name'].str.lower() == result['restaurant_name'].lower()) &
                        (df['location'].str.lower().str.contains(location.lower()))
                    ].iloc[0] if not df[
                        (df['restaurant_name'].str.lower() == result['restaurant_name'].lower()) &
                        (df['location'].str.lower().str.contains(location.lower()))
                    ].empty else None
                    
                    if restaurant_data is not None and 'url' in restaurant_data:
                        result['url'] = restaurant_data['url']
                    elif 'menu_url' in result:
                        result['url'] = result['menu_url']
        
        return {"success": True, "results": results}
    except Exception as e:
        print(f"Error in search: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static/css", exist_ok=True)
    os.makedirs("static/js", exist_ok=True)
    
    # Create index.html if it doesn't exist
    if not os.path.exists("templates/index.html"):
        with open("templates/index.html", "w", encoding="utf-8") as f:
            f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Restaurant Finder</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        .restaurant-card {
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .restaurant-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        }
        .loading {
            display: none;
        }
        .loading.active {
            display: block;
        }
    </style>
</head>
<body class="bg-gray-100 min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <header class="text-center mb-12">
            <h1 class="text-4xl font-bold text-indigo-700 mb-2">🍽️ Restaurant Finder</h1>
            <p class="text-gray-600">Discover the best restaurants for your favorite dishes</p>
        </header>

        <div class="max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-6 mb-12">
            <form id="searchForm" class="space-y-4">
                <div>
                    <label for="dish" class="block text-sm font-medium text-gray-700 mb-1">What would you like to eat?</label>
                    <input type="text" id="dish" name="dish" required
                           class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                           placeholder="e.g., Pizza, Biryani, Pasta">
                </div>
                
                <div>
                    <label for="location" class="block text-sm font-medium text-gray-700 mb-1">Where?</label>
                    <input type="text" id="location" name="location" required
                           class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                           placeholder="e.g., Mumbai, Delhi, Bangalore">
                </div>
                
                <button type="submit" 
                        class="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 transition duration-200 flex items-center justify-center">
                    <i class="fas fa-search mr-2"></i> Find Restaurants
                </button>
            </form>
        </div>

        <div id="results" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <!-- Results will be displayed here -->
        </div>

        <div id="noResults" class="text-center py-12 hidden">
            <i class="fas fa-utensils text-5xl text-gray-300 mb-4"></i>
            <h3 class="text-xl font-medium text-gray-700">No restaurants found</h3>
            <p class="text-gray-500">Try a different search term or location</p>
        </div>

        <div id="loading" class="loading text-center py-12">
            <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500 mx-auto"></div>
            <p class="mt-4 text-gray-600">Finding the best restaurants for you...</p>
        </div>
    </div>

    <footer class="bg-white py-6 mt-12 border-t">
        <div class="container mx-auto px-4 text-center text-gray-500 text-sm">
            <p>© 2023 Restaurant Finder. All rights reserved.</p>
        </div>
    </footer>

    <script>
        document.getElementById('searchForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const dish = document.getElementById('dish').value.trim();
            const location = document.getElementById('location').value.trim();
            const resultsDiv = document.getElementById('results');
            const noResultsDiv = document.getElementById('noResults');
            const loadingDiv = document.getElementById('loading');
            
            // Show loading, hide other states
            loadingDiv.classList.add('active');
            resultsDiv.innerHTML = '';
            noResultsDiv.classList.add('hidden');
            
            try {
                const response = await fetch('/search', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams({
                        'dish': dish,
                        'location': location
                    })
                });
                
                const data = await response.json();
                
                if (data.success && data.results && data.results.length > 0) {
                    // Display results
                    resultsDiv.innerHTML = data.results.map((restaurant, index) => `
                        <div class="restaurant-card bg-white rounded-lg overflow-hidden shadow-md">
                            ${restaurant.image_url ? 
                                `<img src="${restaurant.image_url}" alt="${restaurant.restaurant_name}" class="w-full h-48 object-cover">` : 
                                `<div class="w-full h-48 bg-gray-200 flex items-center justify-center">
                                    <i class="fas fa-utensils text-4xl text-gray-400"></i>
                                </div>`
                            }
                            <div class="p-4">
                                <div class="flex justify-between items-start mb-2">
                                    <h3 class="text-lg font-semibold text-gray-800">${restaurant.restaurant_name}</h3>
                                    <span class="bg-indigo-100 text-indigo-800 text-xs font-medium px-2.5 py-0.5 rounded">
                                        ${restaurant.rating.toFixed(1)} ⭐
                                    </span>
                                </div>
                                <p class="text-gray-600 text-sm mb-3">${restaurant.address || 'Address not available'}</p>
                                <div class="flex justify-between items-center text-sm text-gray-500">
                                    <span><i class="fas fa-users mr-1"></i> ${restaurant.votes.toLocaleString()} votes</span>
                                    <span class="font-medium">₹${restaurant.average_cost_for_two.toLocaleString()} for two</span>
                                </div>
                                ${restaurant.menu_url ? 
                                    `<a href="${restaurant.menu_url}" target="_blank" class="block mt-4 text-center bg-indigo-50 text-indigo-700 hover:bg-indigo-100 py-2 rounded-md text-sm font-medium transition duration-200">
                                        <i class="fas fa-utensils mr-2"></i>View Menu
                                    </a>` : ''
                                }
                            </div>
                        </div>
                    `).join('');
                    
                    noResultsDiv.classList.add('hidden');
                } else {
                    // No results
                    resultsDiv.innerHTML = '';
                    noResultsDiv.classList.remove('hidden');
                }
            } catch (error) {
                console.error('Error:', error);
                resultsDiv.innerHTML = `
                    <div class="col-span-3 bg-red-50 border-l-4 border-red-500 p-4">
                        <div class="flex">
                            <div class="flex-shrink-0">
                                <i class="fas fa-exclamation-circle text-red-500"></i>
                            </div>
                            <div class="ml-3">
                                <p class="text-sm text-red-700">An error occurred while searching. Please try again later.</p>
                            </div>
                        </div>
                    </div>
                `;
            } finally {
                loadingDiv.classList.remove('active');
            }
        });
    </script>
</body>
</html>""")
    
    # Create indexes for better performance
    try:
        db.users.create_index("email", unique=True)
        logger.info("Created unique index on email field")
    except Exception as e:
        logger.error(f"Error creating index: {str(e)}")
    
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000)
