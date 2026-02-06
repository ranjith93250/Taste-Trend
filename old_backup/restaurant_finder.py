import pandas as pd
import zipfile
import os
from tabulate import tabulate
import sys
from typing import List, Dict, Any

def extract_dataset(zip_path: str, extract_to: str = '.') -> str:
    """Extract the dataset if it hasn't been extracted already."""
    csv_path = os.path.join(extract_to, 'zomato_restaurants_in_India.csv')
    
    if not os.path.exists(csv_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
    
    return csv_path

def load_restaurant_data(csv_path: str) -> pd.DataFrame:
    """Load and preprocess the restaurant data."""
    # Read the CSV file
    df = pd.read_csv(csv_path)
    
    # Select and rename relevant columns
    columns = {
        'name': 'restaurant_name',
        'city': 'location',
        'cuisines': 'cuisines',
        'aggregate_rating': 'rating',
        'votes': 'votes',
        'average_cost_for_two': 'average_cost_for_two',
        'address': 'address',
        'rating_text': 'rating_text'
    }
    
    # Keep only the columns we need
    df = df[list(columns.keys())].rename(columns=columns)
    
    # Clean and preprocess the data
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df['votes'] = pd.to_numeric(df['votes'], errors='coerce').fillna(0).astype(int)
    df = df.dropna(subset=['rating', 'restaurant_name', 'location'])
    
    # Convert cost to numeric, handling any non-numeric values
    df['average_cost_for_two'] = pd.to_numeric(
        df['average_cost_for_two'], 
        errors='coerce'
    ).fillna(0).astype(int)
    
    # Filter out restaurants with very few ratings for better quality results
    df = df[df['votes'] >= 10]
    
    return df

def find_restaurants_by_dish(
    df: pd.DataFrame, 
    dish: str, 
    location: str, 
    top_n: int = 3
) -> List[Dict[str, Any]]:
    """
    Find top restaurants serving a specific dish in a given location.
    
    Args:
        df: DataFrame containing restaurant data
        dish: Name of the dish to search for
        location: City or area to search in
        top_n: Number of top restaurants to return
        
    Returns:
        List of dictionaries containing restaurant information
    """
    # Create a copy to avoid SettingWithCopyWarning
    df = df.copy()
    
    # Convert to lowercase for case-insensitive search
    df['cuisines_lower'] = df['cuisines'].str.lower()
    dish_lower = dish.lower()
    
    # Filter by location (case-insensitive)
    location_filter = df['location'].str.lower() == location.lower()
    filtered = df[location_filter].copy()
    
    if filtered.empty:
        return []
    
    # Create a score for each restaurant based on how well it matches the dish
    def calculate_dish_score(row):
        score = 0
        
        # Exact match in cuisines
        if pd.notna(row['cuisines_lower']):
            if dish_lower in row['cuisines_lower'].split(','):
                score += 100
            # Partial match in cuisines
            elif dish_lower in row['cuisines_lower']:
                score += 50
        
        # Add rating to the score (normalized to 0-50 range)
        score += row['rating'] * 10
        
        # Add votes (normalized to 0-20 range)
        score += min(20, row['votes'] / 100)
        
        return score
    
    # Calculate scores and filter
    filtered['dish_score'] = filtered.apply(calculate_dish_score, axis=1)
    
    # Get top N results by score
    results = filtered.nlargest(top_n, 'dish_score')
    
    # Drop the temporary columns
    results = results.drop(columns=['cuisines_lower', 'dish_score'])
    
    return results.to_dict('records')

def display_results(results: List[Dict[str, Any]], dish: str, location: str) -> None:
    """Display the search results in a formatted table."""
    if not results:
        print(f"\nNo restaurants found serving {dish} in {location}.")
        return
    
    print(f"\nTop {len(results)} Restaurants for '{dish}' in {location}:\n")
    
    # Prepare data for tabulate
    table_data = []
    for i, result in enumerate(results, 1):
        table_data.append([
            i,
            result['restaurant_name'][:25] + ('...' if len(result['restaurant_name']) > 25 else ''),
            f"⭐ {result['rating']:.1f} ({result.get('rating_text', 'N/A')})",
            f"👥 {result.get('votes', 0):,}",
            f"💰 ₹{result.get('average_cost_for_two', 0):,}",
            result['location']
        ])
    
    # Create and print the table
    headers = [
        "#", 
        "Restaurant", 
        "Rating (Text)", 
        "Votes", 
        "Cost for Two", 
        "Location"
    ]
    print(tabulate(table_data, headers=headers, tablefmt="grid", stralign="left"))
    print("\n")

def main():
    if len(sys.argv) < 3:
        print("Usage: python restaurant_finder.py 'Dish Name' 'Location'")
        print("Example: python restaurant_finder.py 'Pizza' 'Mumbai'")
        return
    
    dish = sys.argv[1]
    location = sys.argv[2]
    
    # Path to the dataset
    dataset_zip = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'zomato_restaurants_in_India.csv.zip'
    )
    
    # If not found in root, try the 'major project' subdirectory
    if not os.path.exists(dataset_zip):
        dataset_zip = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'major project',
            'zomato_restaurants_in_India.csv.zip'
        )
    
    try:
        # Extract and load the dataset
        print("Loading restaurant data...")
        csv_path = extract_dataset(dataset_zip)
        df = load_restaurant_data(csv_path)
        
        # Find and display results
        results = find_restaurants_by_dish(df, dish, location)
        display_results(results, dish, location)
        
    except FileNotFoundError:
        print("Error: Could not find the dataset file.")
        print(f"Make sure the file exists at: {dataset_zip}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
