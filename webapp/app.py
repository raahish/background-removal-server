import io, traceback

from flask import Flask, request, g
from flask import send_file
from flask_mako import MakoTemplates, render_template
from plim import preprocessor

from PIL import Image, ExifTags
from scipy.misc import imresize
import numpy as np
from keras.models import load_model
import tensorflow as tf

app = Flask(__name__, instance_relative_config=True)
# For Plim templates
mako = MakoTemplates(app)
app.config['MAKO_PREPROCESSOR'] = preprocessor
app.config.from_object('config.ProductionConfig')


# Preload our model
print("Loading model")
model = load_model('./model/tiramisu_2_classes_with_weights.h5')
graph = tf.get_default_graph()

def ml_predict(image):
    with graph.as_default():
        # Add a dimension for the batch
        prediction = model.predict(image[None, :, :, :])
    prediction = prediction.reshape((224,224, -1))
    return prediction

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
        return image

@app.route('/predict', methods=['POST'])
def predict():
    # Load image
    image = request.files['file']
    image = Image.open(image)
    image = rotate_by_exif(image)
    print()
    resized_image = imresize(image, (224, 224))

    # Model input shape = (224,224,3)
    # [0:3] - Take only the first 3 RGB channels and drop ALPHA 4th channel in case this is a PNG
    prediction = ml_predict(resized_image[:, :, 0:3])

    # Resize back to original image size
    # [:, :, 1] = Take predicted class 1 - currently in our model = Person class. Class 0 = Background
    prediction = imresize(prediction[:, :, 1], (image.height, image.width))

    # Append transparency 4th channel to the 3 RGV image channels.
    transparent_image = np.append(image, prediction[: , :, None], axis=-1)
    transparent_image = Image.fromarray(transparent_image)


    # Send back the result image to the client
    byte_io = io.BytesIO()
    transparent_image.save(byte_io, 'PNG')
    byte_io.seek(0)
    return send_file(byte_io, mimetype='image/png')

@app.route('/')
def homepage():
    return render_template('index.html.slim', name='mako')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
