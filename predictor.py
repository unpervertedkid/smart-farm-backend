import numpy as np
import pickle
import pandas as pd

from soil_service import get_soil_properties, LocationNotSupportedError
from weather_service import get_estimated_weather_conditions
from plant_time_predictor import recommend_plant_time_recommendations
from utils import get_planting_duration
from errors import UnsupportedCropError

def get_crop_recommendations(longitude, latitude):
    try:
        soil_properties = get_soil_properties(longitude, latitude)
    except LocationNotSupportedError as e:
        raise e
    estimated_weather_conditions = get_estimated_weather_conditions(longitude, latitude)

    data = {
       "N": soil_properties['nitrogen'],
        "P": soil_properties['phosphorus'],
        "K": soil_properties['potassium'],
        "temperature": estimated_weather_conditions['temperature'],
        "humidity": estimated_weather_conditions['relative_humidity'],
        "ph": soil_properties['ph'],
        "rainfall": estimated_weather_conditions['rainfall']
    }

    # Load the model
    with open('model/CropPrediction.pkl', 'rb') as f:
        model = pickle.load(f)

    # Prepare the data
    input_data = pd.DataFrame([data], columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])

    # Get probabilities for each class
    probabilities = model.predict_proba(input_data)[0]

    # Get the top 3 predictions
    top_three = np.argsort(probabilities)[-3:][::-1]

    # Get the class labels
    class_labels = model.classes_

    # Prepare the results
    results = []
    for i in top_three:
        confidence = round(probabilities[i] * 100)  # Convert to percentage and round off
        if confidence > 20:
            results.append({
                "crop": class_labels[i],
                "confidence": confidence
            })

    return results


def get_plant_time_recommendations(longitude, latitude, crop_name):
    """
    Get plant time recommendations based on the given longitude, latitude, and crop name.

    Parameters:
    - longitude (float): The longitude of the location.
    - latitude (float): The latitude of the location.
    - crop_name (str): The name of the crop.

    Returns:
    - recommendations (list): A list of recommended plant time periods.

    """
    try:
        # Get the planting duration for the crop
        planting_duration = get_planting_duration(crop_name)
    except UnsupportedCropError as e:
        # Rethrow the error
        raise e

    # Get the planting recommendations
    recommendations = recommend_plant_time_recommendations(longitude=longitude, latitude=latitude, planting_duration=planting_duration)

    return recommendations