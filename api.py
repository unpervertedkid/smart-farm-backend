from flask import Flask, request, jsonify, make_response
import pickle
import numpy as np
from sklearn.preprocessing import LabelEncoder

app = Flask(__name__)

@app.route('/', methods=['POST'])
@app.route('/recommend', methods=['POST'])
def predict_crops():
    # Get the input data from the request
    data = request.get_json()

    # Check if all required fields are in the data
    required_fields = ['Nitrogen', 'Phosphorus', 'Potassium', 'Temperature', 'Humidity', 'pH', 'Rainfall']
    for field in required_fields:
        if field not in data:
            return make_response(jsonify({'error': f'Bad Request, missing field: {field}'}), 400)

    # Make a prediction
    response = predict_top_crops(data)

    return make_response(response, 200)

def predict_top_crops(data):
    # Load the model
    with open('model/CropPrediction.pkl', 'rb') as f:
        model = pickle.load(f)

    # Prepare the data
    input_data = [data[field] for field in ['Nitrogen', 'Phosphorus', 'Potassium', 'Temperature', 'Humidity', 'pH', 'Rainfall']]
    input_data = np.array(input_data).reshape(1, -1)

    # Make a prediction
    probabilities = model.predict_proba(input_data)

    # Get the top 5 crops
    top_crops_indices = np.argsort(probabilities, axis=1)[0, -5:]
    top_crops_probabilities = probabilities[0, top_crops_indices]

    # Convert the indices to crop names
    le = LabelEncoder()
    le.classes_ = model.classes_
    top_crops_names = le.inverse_transform(top_crops_indices)

    # Prepare the response
    response = []
    for name, prob in zip(top_crops_names, top_crops_probabilities):
        if prob * 100 >= 49:  # Only include crops with a probability above 20%
            response.append({
                'name': name,
                'probability': round(prob * 100)
            })

    return jsonify(response)

if __name__ == '__main__':
    app.run(port=5050)
