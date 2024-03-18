import numpy as np
import pickle
import pandas as pd

from soil_service import get_soil_properties, LocationNotSupportedError
from weather_service import get_estimated_weather_conditions, get_rainfall_history

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

def recommend_planting_times(longitude, latitude, crop_name):
    # Get the rainfall history
    # Todo
    return None