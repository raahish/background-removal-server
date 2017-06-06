import io, traceback

from flask import Flask, jsonify, request
from flask import send_file

from flask_mako import MakoTemplates, render_template
from plim import preprocessor

import ml
from PIL import Image, ExifTags
from scipy.misc import imresize
import numpy as np

app = Flask(__name__, instance_relative_config=True)
# For Plim templates
mako = MakoTemplates(app)
app.config['MAKO_PREPROCESSOR'] = preprocessor
app.config.from_object('config.ProductionConfig')

def rotate_by_exif(image):
    try :
        for orientation in ExifTags.TAGS.keys() :
            if ExifTags.TAGS[orientation]=='Orientation' : break
        exif=dict(image._getexif().items())

        if   exif[orientation] == 3 :
            image=image.rotate(180, expand=True)
        elif exif[orientation] == 6 :
            image=image.rotate(270, expand=True)
        elif exif[orientation] == 8 :
            image=image.rotate(90, expand=True)
        return image
    except:
        traceback.print_exc()

@app.route('/predict', methods=['POST'])
def predict():
    # Convert image file into numpy
    image = request.files['file']
    image = Image.open(image)
    image = rotate_by_exif(image)
    resized_image = imresize(image, (224, 224 , -1))

    # Take only first 3 RGB channels and drop ALPHA 4th channel in case this is a PNG
    prediction = ml.predict(resized_image[:, :, 0:3])

    # clip values instead of using argmax to be used as transparency values
    # prediction[np.where(prediction[:, :, 0]<prediction[:, :, 1]), 1] = 0

    # Resize back to original image size
    prediction = imresize(prediction[:, :, 1], (image.height, image.width))

    transparent_image = np.append(image, prediction[: , :, None], axis=-1)
    transparent_image = Image.fromarray(transparent_image)


    byte_io = io.BytesIO()
    transparent_image.save(byte_io, 'PNG')
    byte_io.seek(0)
    return send_file(byte_io, mimetype='image/png')

@app.route('/')
def homepage():
    return render_template('index.html.slim', name='mako')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
