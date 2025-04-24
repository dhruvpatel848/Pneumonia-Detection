from flask import Flask, render_template, request, jsonify
import numpy as np
import os
from tensorflow.keras.models import load_model
from PIL import Image as PILImage

app = Flask(__name__)

# Load the trained model
model_path = 'model/model.h5'
model = load_model(model_path)

# Define image dimensions for the model input
img_width, img_height = 150, 150

# Define the prediction function
def prepare_image(img_path):
    img = PILImage.open(img_path).convert('RGB')  # Convert to RGB to remove alpha channel
    img = img.resize((img_width, img_height))  # Resize image to match model input
    img = np.array(img) / 255.0  # Rescale pixel values to [0, 1]
    img = np.expand_dims(img, axis=0)  # Add batch dimension
    return img

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    try:
        # Prepare image
        img_path = os.path.join('uploads', file.filename)
        file.save(img_path)
        
        img_array = prepare_image(img_path)
        
        # Predict using the model
        prediction = model.predict(img_array)
        print("Raw prediction:", prediction)  # Debugging line
        
        # If the prediction is greater than 0.5, classify as "Pneumonia"
        if prediction[0] > 0.5:
            result = "Pneumonia"
        else:
            result = "Normal"
        
        return jsonify({"result": result})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
