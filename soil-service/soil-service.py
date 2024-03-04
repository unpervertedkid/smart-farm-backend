import requests

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

def get_nitrogen_and_ph(longitude, latitude):
    response = _fetch_nitrogen_and_ph(longitude, latitude)
    return _compute_mean_for_first_three_depths(response)

# Example usage
mean_values = get_nitrogen_and_ph(5.6037, 52.1016)
print(mean_values)