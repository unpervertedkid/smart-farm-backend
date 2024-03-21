import os
import logging
from flask import Flask, request, jsonify, make_response
from predictor import get_crop_recommendations, get_plant_time_recommendations
from soil_service import LocationNotSupportedError
from errors import UnsupportedCropError, FileReadError
from utils import get_all_crops

from flask_cors import CORS
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Set up logging
logging.basicConfig(level=logging.INFO)

@app.route('/crop-recommendations', methods=['POST'])
def recommend_crops():
    # Get the input data from the request
    data = request.get_json()

    # Check if all required fields are in the data
    required_fields = ['latitude', 'longitude']
    for field in required_fields:
        if field not in data:
            logging.error(f'Bad Request for crop recommendation, missing field: {field}')
            return make_response(jsonify({'error': f'Bad Request, missing field: {field}'}), 400)

    # Validate latitude and longitude
    latitude = data['latitude']
    longitude = data['longitude']
    logging.info(f'Received crop recommendation request for location: {data["latitude"]}, {data["longitude"]}')
    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        logging.error(f'Invalid latitude or longitude: {latitude}, {longitude}')
        return make_response(jsonify({'error': 'Bad Request, invalid latitude or longitude'}), 400)

    try:
        # Get crop recommendations
        response = get_crop_recommendations(longitude, latitude)
    except LocationNotSupportedError:
        logging.error(f'Location with latitude {latitude} and longitude {longitude} is not supported')
        return make_response(jsonify({'error': 'Location not supported. Sending error due to invalid location.'}), 404)

    logging.info(f'Sending crop recommendation response for location{latitude}, {longitude}: {response}')
    return make_response(response, 200)


@app.route('/plant-time-recommendations', methods=['POST'])
def recommend_plant_time():
    # Get the input data from the request
    data = request.get_json()

    # Check if all required fields are in the data
    required_fields = ['latitude', 'longitude', 'crop']
    for field in required_fields:
        if field not in data:
            logging.error(f'Bad Request for plant time recommendation, missing field: {field}')
            return make_response(jsonify({'error': f'Bad Request, missing field: {field}'}), 400)

    # Validate latitude and longitude
    latitude = data['latitude']
    longitude = data['longitude']
    logging.info(f'Received plant time recommendation request for location: {latitude}, {longitude}')
    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        logging.error(f'Invalid latitude or longitude: {latitude}, {longitude}. Sending error due to invalid location.')
        return make_response(jsonify({'error': 'Bad Request, invalid latitude or longitude'}), 400)

    try:
        # Get the planting recommendations
        response = get_plant_time_recommendations(longitude=longitude, latitude=latitude, crop_name=data['crop'])
    except UnsupportedCropError as e:
        supported_crops = get_all_crops()
        logging.error(f'Crop {data["crop"]} is not supported. Sending error due to unsupported crop.')
        return make_response(jsonify({'error': str(e), 'supported_crops': supported_crops}), 404)

    logging.info(f'Sending Plant time recommendations for location {latitude}, {longitude}: {response}')
    return make_response(jsonify(response), 200)

@app.route('/crops', methods=['GET'])
def get_crops():
    logging.info('Received request for all crops')
    try:
        crops = get_all_crops()
    except FileReadError:
        logging.error('Failed to read the crops data. Sending error due to file read error.')
        return make_response(jsonify({'error': 'Failed to read the crops data'}), 500)
    logging.info(f'Sending all crops: {crops}')
    return make_response(jsonify(crops), 200)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)