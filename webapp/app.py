print("Starting app.py")
import io

from flask import Flask, jsonify, request
from flask import send_file

from flask_mako import MakoTemplates, render_template
from plim import preprocessor

import ml
from PIL import Image
from scipy.misc import imresize
import numpy as np

app = Flask(__name__, instance_relative_config=True)
# For Plim templates
mako = MakoTemplates(app)
app.config['MAKO_PREPROCESSOR'] = preprocessor
app.config.from_object('config.ProductionConfig')

def compose_transparent(prediction, image):
    # Add alpha channel
    image = np.pad(image, (0,1), 'constant', constant_values=255)
    # Find all foreground predicted to be non background pixels
    foreground_indexes = np.where(prediction!=0)
    transparent_image = np.zeros((image.shape[0], image.shape[1], 4))
    transparent_image[foreground_indexes] = image[foreground_indexes]
    return transparent_image

@app.route('/predict', methods=['POST'])
def predict():
    # Convert image file into numpy
    image = request.files['file']
    image = Image.open(image)
    image = np.asarray(image).astype('float64')
    resized_image = imresize(image, (224, 224 ,3))

    # The current image from the center camera of the car
    prediction = ml.predict(resized_image)
    prediction = imresize(prediction, (image.shape[0], image.shape[1]))

    transparent_image = compose_transparent(prediction, image)
    transparent_image = Image.fromarray(np.uint8(transparent_image))


    byte_io = io.BytesIO()
    transparent_image.save(byte_io, 'PNG')
    byte_io.seek(0)
    return send_file(byte_io, mimetype='image/png')

@app.route('/')
def homepage():
    return render_template('index.html.slim', name='mako')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
