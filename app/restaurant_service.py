"""
Restaurant finder service using Zomato dataset
"""
import pandas as pd
import os
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Global variable to store the restaurant data
df = None


def load_data():
    """Load restaurant data from CSV file"""
    global df
    if df is not None:
        return df
        
    logger.info("Starting to load restaurant data")
    
    # Possible paths to the dataset
    possible_paths = [
        os.path.join('zomato_restaurants_in_India.csv'),
        os.path.join('major project', 'zomato_restaurants_in_India.csv'),
    ]
    
    try:
        # Try each possible path
        for path in possible_paths:
            full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), path)
            logger.debug(f"Trying path: {full_path}")
            
            if os.path.exists(full_path):
                logger.info(f"Found file at: {full_path}")
                
                try:
                    df = pd.read_csv(full_path, low_memory=False)
                    logger.info(f"Successfully loaded {len(df)} rows from CSV")
                    logger.info(f"Available columns: {', '.join(df.columns.tolist())}")
                    break
                except Exception as e:
                    logger.error(f"Error reading CSV: {e}")
        
        if df is None:
            logger.error("Could not find or load the dataset file.")
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
        
        logger.info(f"Successfully processed {len(df)} restaurants")
        return df
        
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}", exc_info=True)
        return None


def find_restaurants(dish: str, location: str, top_n: int = 10) -> List[Dict[str, Any]]:
    """
    Find restaurants serving a specific dish in a given location.
    
    Args:
        dish: The dish or cuisine to search for
        location: The location to search in (can be city or specific area)
        top_n: Maximum number of results to return
        
    Returns:
        List of restaurant dictionaries with complete details
    """
    try:
        data = load_data()
        if data is None or data.empty:
            logger.error("No data loaded")
            return []
            
        logger.info(f"Searching for '{dish}' in '{location}'")
        
        # Convert to lowercase for case-insensitive search
        dish_terms = [d.strip().lower() for d in dish.split() if d.strip()]
        location_terms = [loc.strip().lower() for loc in location.split(',') if loc.strip()]
        
        # Filter by location
        location_columns = ['location', 'locality', 'address']
        location_columns = [col for col in location_columns if col in data.columns]
        
        def create_location_string(row):
            return ' '.join(str(row[col]).lower() for col in location_columns if col in row and pd.notna(row[col]))
            
        data['location_search'] = data.apply(create_location_string, axis=1)
        
        location_filter = data['location_search'].apply(
            lambda x: all(term in str(x).lower() for term in location_terms)
        )
        
        filtered_df = data[location_filter].copy()
        
        if filtered_df.empty:
            logger.warning(f"No restaurants found in location: {location}")
            return []
            
        logger.info(f"Found {len(filtered_df)} restaurants in location")
        
        # Filter by dish
        dish_columns = ['cuisines', 'restaurant_name']
        dish_columns = [col for col in dish_columns if col in filtered_df.columns]
        
        def create_search_string(row):
            return ' '.join(str(row[col]).lower() for col in dish_columns if col in row and pd.notna(row[col]))
            
        filtered_df['search_string'] = filtered_df.apply(create_search_string, axis=1)
        
        def dish_match(search_str):
            search_str = str(search_str).lower()
            return any(term in search_str for term in dish_terms)
            
        dish_filter = filtered_df['search_string'].apply(dish_match)
        results_df = filtered_df[dish_filter].copy()
        
        if results_df.empty:
            logger.warning(f"No restaurants found serving '{dish}' in {location}")
            return []
        
        logger.info(f"Found {len(results_df)} restaurants serving '{dish}'")
        
        # Get unique restaurants
        results_df = results_df.drop_duplicates(subset=['restaurant_name', 'location'])
        
        # Convert to list of dictionaries
        restaurants = []
        for _, row in results_df.iterrows():
            restaurant = {
                'restaurant_name': row.get('restaurant_name', 'Unnamed Restaurant'),
                'address': row.get('address', row.get('location', 'Address not available')),
                'locality': row.get('locality', 'Locality not available'),
                'city': row.get('city', row.get('location', 'City not available')),
                'cuisines': row.get('cuisines', 'Cuisines not specified'),
                'url': row.get('url', None),
                'menu_url': row.get('menu_url', None),
                'image_url': row.get('image_url', None),
                'rating': float(row['rating']) if 'rating' in row and pd.notna(row['rating']) else 0.0,
                'rating_text': row.get('rating_text', 'No rating'),
                'votes': int(row['votes']) if 'votes' in row and pd.notna(row['votes']) else 0,
                'average_cost_for_two': int(row['average_cost_for_two']) if 'average_cost_for_two' in row and pd.notna(row['average_cost_for_two']) else 0,
            }
            restaurants.append(restaurant)
        
        # Sort by rating and limit results
        restaurants.sort(key=lambda x: x['rating'], reverse=True)
        restaurants = restaurants[:top_n]
        
        logger.info(f"Returning {len(restaurants)} restaurants")
        return restaurants
        
    except Exception as e:
        logger.error(f"Error in find_restaurants: {str(e)}", exc_info=True)
        return []
