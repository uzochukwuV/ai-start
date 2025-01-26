from geopy.distance import geodesic
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="your_app_name") 





import os
import json

def save_json_to_root(data, filename):
    """Save JSON to root working directory"""
    root_dir = os.getcwd()
    filepath = os.path.join(root_dir, filename)
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def load_json_from_root(filename):
    """Load JSON from root working directory"""
    root_dir = os.getcwd()
    filepath = os.path.join(root_dir, filename)
    
    with open(filepath, 'r') as f:
        return json.load(f)


def savejson():
    save_json_to_root(country_coords, 'country_coords.json')

def getjson():
    return load_json_from_root('country_coords.json')

country_coords = getjson()



def get_coordinates(country):
  if country in country_coords:
    print(country_coords[country])
    location = country_coords[country]
    return location["latitude"], location["longitude"]
  else:
      
      try:
            location = geolocator.geocode(country)
            if location:
                country_coords[country] = {
                    "latitude": location.latitude,
                    "longitude": location.longitude
                }
                return location.latitude, location.longitude
            else:
                return 1, 1 
      except Exception as e:
            print(f"Error getting coordinates for {country}: {e}")
            return 1, 1
      
def calculate_distance(row):
    school_coords = (row['latitude'], row['longitude'])
    server_coords = (row['server_location_latitude'], row['server_location_longitude'])
    if None in server_coords:
        return None  # Handle cases where server coordinates are missing
    return geodesic(school_coords, server_coords).kilometers