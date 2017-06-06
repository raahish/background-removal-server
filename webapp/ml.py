from keras.models import load_model
import numpy as np
import tensorflow as tf

model = load_model('tiramisu_2_classes_with_weights.h5')
graph = tf.get_default_graph()


def predict(image):
    with graph.as_default():
        prediction = model.predict(image[None, :, :, :])
    prediction = prediction.reshape((224,224, -1))
    return prediction


