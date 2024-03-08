import numpy as np
import pickle
import pandas as pd

from soil_service import get_soil_properties
from weather_service import get_estimated_weather_conditions

def get_crop_recommendations(longitude, latitude):
    soil_properties = get_soil_properties(longitude, latitude)
    estimated_weather_conditions = get_estimated_weather_conditions(longitude, latitude)

    data = {
       "N": soil_properties['nitrogen'],
        "P": soil_properties['phosphorus'],
        "K": soil_properties['potassium'],
        "temperature": estimated_weather_conditions['temperature'],
        "humidity": estimated_weather_conditions['relative_humidity'],
        "ph": soil_properties['ph'],
        "rainfall": estimated_weather_conditions['precipitation']
    }

    # Load the model
    with open('model/CropPrediction.pkl', 'rb') as f:
        model = pickle.load(f)

    # Prepare the data
    input_data = pd.DataFrame([data], columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])

    # Make a prediction
    prediction = model.predict(input_data)

    print(prediction)

# Example usage for nairobi
longitude = 36.817223
latitude = 1.286389
get_crop_recommendations(longitude, latitude)