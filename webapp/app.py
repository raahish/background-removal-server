import io

from flask import Flask, jsonify, request
import keras
from PIL import Image
from flask import send_file
from keras.models import model_from_json
import numpy as np
from scipy.misc import imresize

import tensorflow as tf

json_file = open('./model/model.json', 'r')
model = model_from_json(json_file.read())
json_file.close()
model.load_weights('./model/weights224.01-4.25.hdf5', by_name=True)
graph = tf.get_default_graph()

app = Flask(__name__)


def parse_code(l):
    splitted = l.strip().split("\t")
    a = splitted[0]
    b = splitted[-1]
    return tuple(int(o) for o in a.split(' ')), b

label_codes,label_names = zip(*[
    parse_code(l) for l in open("./label_colors.txt")])

def color_label(a):
    r,c=a.shape
    res = np.zeros((r,c,3), 'uint8')
    for j in range(r):
        for k in range(c):
            o=label_codes[a[j,k]]
            res[j,k] = o
    return res

@app.route('/predict', methods=['POST'])
def predict():
    # The current image from the center camera of the car
    img_stream = request.files['image']
    image = Image.open(img_stream)
    image = imresize(image, (224, 224 ,3))
    image_array = np.asarray(image)
    with graph.as_default():
        prediction = model.predict(image_array[None, :, :, :], batch_size=1)
        prediction = np.argmax(prediction, axis=-1)
        prediction = prediction.reshape((-1,224,224))

        mask = prediction[0]
        mask = color_label(mask)
        mask = Image.fromarray(np.uint8(mask))

        byte_io = io.BytesIO()
        mask.save(byte_io, 'PNG')
        byte_io.seek(0)
        return send_file(byte_io, mimetype='image/png')
        # return jsonify({'prediction': repr(prediction)})
    # return jsonify({'prediction': None})

@app.route('/')
def homepage():
    return "Hello World!"

if __name__ == '__main__':
    app.run(host='0.0.0.0')
