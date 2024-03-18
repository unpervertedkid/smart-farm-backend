from flask import Flask, request, jsonify, make_response
from predictor import get_crop_recommendations
from soil_service import LocationNotSupportedError
import os

app = Flask(__name__)

@app.route('/crop-recommendations', methods=['POST'])
def recommend_crops():
    # Get the input data from the request
    data = request.get_json()

    # Check if all required fields are in the data
    required_fields = ['latitude', 'longitude']
    for field in required_fields:
        if field not in data:
            return make_response(jsonify({'error': f'Bad Request, missing field: {field}'}), 400)

    # Validate latitude and longitude
    latitude = data['latitude']
    longitude = data['longitude']
    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        return make_response(jsonify({'error': 'Bad Request, invalid latitude or longitude'}), 400)

    try:
        # Get crop recommendations
        response = get_crop_recommendations(longitude, latitude)
    except LocationNotSupportedError:
        return make_response(jsonify({'error': 'Location not supported'}), 400)

    return make_response(response, 200)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)