from keras.models import model_from_json
from PIL import Image
import numpy as np
from scipy.misc import imresize
import tensorflow as tf

json_file = open('./model/model.json', 'r')
model = model_from_json(json_file.read())
json_file.close()
model.load_weights('./model/weights224.01-4.25.hdf5', by_name=True)
graph = tf.get_default_graph()

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

def predict(image):
    image = Image.open(image)
    image = imresize(image, (224, 224 ,3))
    image = np.asarray(image)

    with graph.as_default():
        prediction = model.predict(image[None, :, :, :], batch_size=1)

    prediction = np.argmax(prediction, axis=-1)
    prediction = prediction.reshape((-1,224,224))

    mask = prediction[0]
    mask = color_label(mask)
    return Image.fromarray(np.uint8(mask))
