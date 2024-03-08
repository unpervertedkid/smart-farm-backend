import requests
from tif_reader import get_value_at_point

def get_soil_properties(longitude, latitude):
    # Get nitrogen and pH values 
    nitrogen_and_ph = _get_nitrogen_and_ph(longitude, latitude)

    # Get phosphorus and potassium values
    phosphorus_raster_file = 'phosphorus.tif'
    potassium_raster_file = 'potassium.tif'

    phosphorus = get_value_at_point(phosphorus_raster_file, longitude, latitude)
    potassium = get_value_at_point(potassium_raster_file, longitude, latitude)

    return {
        'nitrogen': nitrogen_and_ph['nitrogen'],
        'ph': nitrogen_and_ph['phh2o'],
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
    return response.json()

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

# Example usage for nairobi
longitude = 36.817223
latitude = 1.286389

soil_properties = get_soil_properties(longitude, latitude)
print(soil_properties)