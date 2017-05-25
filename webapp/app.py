print("Starting app.py")
import io

from flask import Flask, jsonify, request
from flask import send_file

from flask_mako import MakoTemplates, render_template
from plim import preprocessor

import ml

app = Flask(__name__, instance_relative_config=True)
mako = MakoTemplates(app)
app.config['MAKO_PREPROCESSOR'] = preprocessor
app.config.from_object('config.ProductionConfig')


@app.route('/predict', methods=['POST'])
def predict():
    # The current image from the center camera of the car
    mask = ml.predict(request.files['file'])
    byte_io = io.BytesIO()
    mask.save(byte_io, 'PNG')
    byte_io.seek(0)
    return send_file(byte_io, mimetype='image/png')

@app.route('/')
def homepage():
    return render_template('index.html.slim', name='mako')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
