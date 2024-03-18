import pandas as pd
from errors import FileReadError, UnsupportedCropError

def convert_ppm_to_ppa(ppm, depth_cm, bulk_density=1.6):
    """
    Convert ppm to ppa given the depth in cm.
    
    Parameters:
    ppm (float): The concentration in parts per million.
    depth_cm (float): The depth in centimeters.
    bulk_density (float): The bulk density of the soil in g/cm^3. Default is 1.6 g/cm^3.

    Returns:
    float: The concentration in pounds per acre.
    """
    # Convert depth from cm to inches (1 inch = 2.54 cm)
    depth_in = depth_cm / 2.54

    # Convert depth from inches to feet (1 foot = 12 inches)
    depth_ft = depth_in / 12

    # Convert bulk density from g/cm^3 to lb/ft^3 (1 g/cm^3 = 62.43 lb/ft^3)
    bulk_density_lb_ft3 = bulk_density * 62.43

    # Calculate the weight of the soil per acre in pounds
    weight_per_acre_lb = 43560 * depth_ft * bulk_density_lb_ft3

    # Convert ppm to ppa
    ppa = ppm * weight_per_acre_lb / 1e6

    return ppa

def calculate_extractable_nutrients(ppm_P, ppm_K, depth_cm, bulk_density=1.6):
    """
    Calculate the pounds of extractable phosphorus pentoxide and potassium oxide per acre.
    
    Parameters:
    ppm_P (float): The concentration of phosphorus in parts per million.
    ppm_K (float): The concentration of potassium in parts per million.
    depth_cm (float): The depth in centimeters.
    bulk_density (float): The bulk density of the soil in g/cm^3. Default is 1.6 g/cm^3.

    Returns:
    tuple: The pounds of extractable phosphorus pentoxide and potassium oxide per acre.
    """
    # Convert ppm to ppa
    ppa_P = convert_ppm_to_ppa(ppm_P, depth_cm, bulk_density)
    ppa_K = convert_ppm_to_ppa(ppm_K, depth_cm, bulk_density)

    # Calculate the pounds of extractable phosphorus pentoxide and potassium oxide per acre
    P2O5_per_acre = ppa_P * 2.2913
    K2O_per_acre = ppa_K * 1.2046

    return P2O5_per_acre, K2O_per_acre


def get_planting_duration(crop_name):
    crop_name = crop_name.lower()
    
    # Read the planting duration csv
    planting_durations = pd.read_csv('data/planting_durations.csv')
    
    if crop_name not in planting_durations['crop'].values:
        raise UnsupportedCropError(f"The crop '{crop_name}' is not supported.")
    
    return planting_durations[planting_durations['crop'] == crop_name]['duration(days)'].values[0]



def get_all_crops():
    try:
        # Read the planting duration csv
        planting_durations = pd.read_csv('data/planting_durations.csv')
    except Exception as e:
        raise FileReadError("Failed to read the file 'data/planting_durations.csv'")
    return planting_durations['crop'].values.tolist()