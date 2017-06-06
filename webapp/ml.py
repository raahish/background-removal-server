from keras.models import model_from_json
import numpy as np
import tensorflow as tf

json_file = open('./model/tiramisu_2_classes.json', 'r')
model = model_from_json(json_file.read())
json_file.close()
model.load_weights('./model/weights224.02-0.28.hdf5', by_name=True)
graph = tf.get_default_graph()


def predict(image):
    with graph.as_default():
        prediction = model.predict(image[None, :, :, :])
    prediction = prediction.reshape((224,224, -1))
    return prediction


