from langchain_core.tools import tool
import requests
from app.core.config import settings

@tool
def get_drug_info(drug_name: str) -> str:
    """
    Look up a drug/medication in the OpenFDA database to find information about its indications, usage, 
    warnings, side effects, and interactions. Always use this tool when a user asks about a specific medicine.
    """
    if not settings.OPENFDA_API_KEY or settings.OPENFDA_API_KEY == "your_openfda_api_key_here":
        return "OpenFDA API key is not configured. Cannot retrieve drug information."
    
    url = f"https://api.fda.gov/drug/label.json?api_key={settings.OPENFDA_API_KEY}&search=openfda.brand_name:\"{drug_name}\"&limit=1"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "results" in data and len(data["results"]) > 0:
                result = data["results"][0]
                
                # Extract key fields
                warnings = result.get("warnings", ["No warnings listed."])[0]
                indications = result.get("indications_and_usage", ["No indications listed."])[0]
                interactions = result.get("drug_interactions", ["No specific interactions listed."])[0]
                
                return (
                    f"Drug Info for {drug_name}:\n"
                    f"- Indications: {indications[:500]}...\n"
                    f"- Warnings: {warnings[:500]}...\n"
                    f"- Interactions: {interactions[:500]}..."
                )
            return f"No information found for {drug_name}."
        else:
            return f"Error retrieving drug information: {response.status_code}"
    except Exception as e:
        return f"Failed to connect to FDA database: {str(e)}"

@tool
def find_nearby_hospitals(location_query: str) -> str:
    """
    Find nearby hospitals, clinics, or pharmacies based on a location provided by the user.
    """
    if not settings.GOOGLE_MAPS_API_KEY or settings.GOOGLE_MAPS_API_KEY == "your_google_maps_api_key_here":
        return "Google Maps API key is not configured. Cannot find nearby hospitals."
        
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query=hospitals+near+{location_query}&key={settings.GOOGLE_MAPS_API_KEY}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "results" in data and len(data["results"]) > 0:
                places = []
                for place in data["results"][:3]:
                    name = place.get("name")
                    address = place.get("formatted_address")
                    rating = place.get("rating", "N/A")
                    places.append(f"- {name} ({rating} stars): {address}")
                return "Found the following nearby facilities:\n" + "\n".join(places)
            return f"No hospitals found near {location_query}."
        return f"Error searching for hospitals: {response.status_code}"
    except Exception as e:
        return f"Failed to connect to Google Maps: {str(e)}"

# List of tools to bind to the LLM
get_medical_tools = [get_drug_info, find_nearby_hospitals]
