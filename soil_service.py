import requests
from tif_reader import get_value_at_point
class LocationNotSupportedError(Exception):
    """Raised when a location is not supported"""
    pass

def get_soil_properties(longitude, latitude):
    # Get nitrogen and pH values 
    nitrogen_and_ph = _get_nitrogen_and_ph(longitude, latitude)

    # Get phosphorus and potassium values
    phosphorus_raster_file = 'data/kenya_phosphorus.tif'
    potassium_raster_file = 'data/kenya_potassium.tif'

    try:
        phosphorus = get_value_at_point(phosphorus_raster_file, longitude, latitude)/100 # Divide by 100 to convert to ppm
        potassium = get_value_at_point(potassium_raster_file, longitude, latitude)
    except Exception:
        raise LocationNotSupportedError(f"Location with longitude {longitude} and latitude {latitude} is not supported")

    return {
        'nitrogen': nitrogen_and_ph['nitrogen'],
        'ph': nitrogen_and_ph['phh2o']/10,  # Convert to pH as is received in pH*10
        'phosphorus': phosphorus,
        'potassium': potassium
    }

def _get_nitrogen_and_ph(longitude, latitude):
    response = _fetch_nitrogen_and_ph(longitude, latitude)
    return _compute_mean_for_first_three_depths(response)


def _fetch_nitrogen_and_ph(longitude, latitude):
    url = f"https://dev-rest.isric.org/soilgrids/v2.0/properties/query?lon={longitude}&lat={latitude}&property=nitrogen&property=phh2o&value=mean"
    headers = {
        'authority': 'dev-rest.isric.org',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'dnt': '1',
        'origin': 'https://soilgrids.org',
        'referer': 'https://soilgrids.org/',
    }
    response = requests.get(url, headers=headers)
    response_json = response.json()

    # Check if all mean values are None
    for layer in response_json['properties']['layers']:
        if all(depth['values']['mean'] is None for depth in layer['depths']):
            raise LocationNotSupportedError(f"Location with longitude {longitude} and latitude {latitude} is not supported")

    return response_json

def _compute_mean_for_first_three_depths(response):
    properties = response['properties']['layers']
    result = {}

    for prop in properties:
        name = prop['name']
        depths = prop['depths'][:3]  # Get the first three depths
        values = [depth['values']['mean'] for depth in depths]  # Extract the mean values
        mean_value = sum(values) / len(values)  # Compute the mean
        result[name] = mean_value

    return result

def _convert_phosphorus_to_ppa(phosphorus_mg_per_100kg):
    # Convert mg/100kg to ppm
    phosphorus_ppm = phosphorus_mg_per_100kg / 10

    # Convert ppm to pounds per acre (ppa) of phosphorus
    ppa_phosphorus = phosphorus_ppm * 2.3

    # Assuming soil depth of 30 cm (approximately 11.8 inches)
    soil_depth_inches = 11.8

    # Calculate the phosphorus ratio
    phosphorus_ratio = ppa_phosphorus / soil_depth_inches
    
    return phosphorus_ratio