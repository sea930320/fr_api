import tensorflow as tf
from util.src.align import detect_face
from util.src import facenet
from . import download_model
import os
import cv2
import numpy as np
from scipy import spatial

minsize = 20  # minimum size of face
threshold = [0.6, 0.7, 0.7]  # three steps's threshold
factor = 0.709  # scale factor

home = os.path.abspath(os.path.dirname(__name__)) + '/core'
model_path = home + '/.facenet_model/20180408-102900/20180408-102900.pb'
facenet.load_model(model_path)

# Get input and output tensors
images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")
tf.Graph().as_default()
sess = tf.Session()

def align_face(pnet, rnet, onet, image, image_size=160, margin=11):
    img = cv2.imread(os.path.expanduser(image))[:, :, ::-1]
    img_size = np.asarray(img.shape)[0:2]
    bounding_boxes, _ = detect_face.detect_face(
        img, minsize, pnet, rnet, onet, threshold, factor)
    print (bounding_boxes)
    prewhitens = []
    for (i, bounding_box) in enumerate(bounding_boxes):
        det = np.squeeze(bounding_box[0:4])
        bb = np.zeros(4, dtype=np.int32)
        bb[0] = np.maximum(det[0] - margin / 2, 0) # x1
        bb[1] = np.maximum(det[1] - margin / 2, 0) # y1
        bb[2] = np.minimum(det[2] + margin / 2, img_size[1]) # x2
        bb[3] = np.minimum(det[3] + margin / 2, img_size[0]) # y2
        cropped = img[bb[1]:bb[3], bb[0]:bb[2], :]
        aligned = cv2.resize(cropped[:, :, ::-1],
                             (image_size, image_size))[:, :, ::-1]
        prewhiten = facenet.prewhiten(aligned)
        prewhitens.append(prewhiten)
        break
    return (prewhitens, bounding_boxes[:1])

def align_opencv_face(pnet, rnet, onet, cvimg, image_size=160, margin=11):
    img = cvimg[:, :, ::-1]
    img_size = np.asarray(img.shape)[0:2]
    bounding_boxes, _ = detect_face.detect_face(
        img, minsize, pnet, rnet, onet, threshold, factor)
    print (bounding_boxes)
    prewhitens = []
    for (i, bounding_box) in enumerate(bounding_boxes):
        det = np.squeeze(bounding_box[0:4])
        bb = np.zeros(4, dtype=np.int32)
        bb[0] = np.maximum(det[0] - margin / 2, 0) # x1
        bb[1] = np.maximum(det[1] - margin / 2, 0) # y1
        bb[2] = np.minimum(det[2] + margin / 2, img_size[1]) # x2
        bb[3] = np.minimum(det[3] + margin / 2, img_size[0]) # y2
        cropped = img[bb[1]:bb[3], bb[0]:bb[2], :]
        aligned = cv2.resize(cropped[:, :, ::-1],
                             (image_size, image_size))[:, :, ::-1]
        prewhiten = facenet.prewhiten(aligned)
        prewhitens.append(prewhiten)
        break
    return (prewhitens, bounding_boxes[:1])

def embedding(images):
    # facenet.load_model(model_path)
    # Run forward pass to calculate embeddings
    feed_dict = {images_placeholder: images,
                 phase_train_placeholder: False}
    emb = sess.run(embeddings, feed_dict=feed_dict)
    return emb


def compare(images, threshold=0.7):
    emb = embedding(images)

    sims = np.zeros((len(images), len(images)))
    for i in range(len(images)):
        for j in range(len(images)):
            sims[i][j] = (
                1 - spatial.distance.cosine(emb[i], emb[j]) > threshold)

    return sims

