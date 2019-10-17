from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes, api_view
from rest_framework.exceptions import ValidationError
import tensorflow as tf
from util.src.align import detect_face
from util.utils import data_uri_to_cv2_img
from util.service import facenet
import pickle
import numpy as np
from scipy import spatial
from django.conf import settings
from dataset.models import Dataset
from authentication.serializers import UserSerializer
from authentication.models import User

# preprocess...
with tf.Graph().as_default():
    sess = tf.Session(config=tf.ConfigProto(log_device_placement=False))
    with sess.as_default():
        pnet, rnet, onet = detect_face.create_mtcnn(sess, None)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search(request):
    uri = request.data.get('image', '')
    try:
        img = data_uri_to_cv2_img(uri)
    except Exception:
        raise ValidationError({"image": "invalid base64 image"})
    if img is None:
        raise ValidationError({"image": "invalid base64 image"})

    # get bounding boxes and prewhitens
    print("[INFO] Getting bounding boxes and prewhitens of image...")
    (prewhitens, bounding_boxes) = facenet.align_opencv_face(pnet, rnet, onet, img)

    dataset_img_list = []
    user_matcher = []

    print("[INFO] get prewhitens from datasets...")
    datasets = Dataset.objects.all()
    for dataset in datasets:
        dataset_imgs = dataset.images.all()
        for dataset_img in dataset_imgs:
            if dataset_img.encoding:
                aligns = pickle.loads(dataset_img.encoding)
                # di_bounding_boxes = aligns['bouding_boxes']
                di_prewhitens = aligns['prewhitens']
                for di_prewhiten in di_prewhitens:
                    dataset_img_list.append(di_prewhiten)
                    user_matcher.append(dataset.user.id)

    if len(dataset_img_list) == 0:
        raise ValidationError({"dataset": "couldn't find dataset, please upload dataset first."})

    print("[INFO] Set embeddings including target image...")
    temp_img_list = dataset_img_list.copy()
    for prewhiten in prewhitens:
        temp_img_list.append(prewhiten)
    temp_images = np.stack(temp_img_list)
    emb = facenet.embedding(temp_images)

    print("[INFO] Identify face...")
    sims = []
    dis = np.zeros((len(bounding_boxes), len(dataset_img_list)))
    for i in range(len(bounding_boxes)):
        for j in range(len(dataset_img_list)):
            dis[i][j] = 1 - spatial.distance.cosine(emb[len(dataset_img_list) + i], emb[j])
        max_j = np.argmax(dis[i])
        is_indentified = (dis[i][max_j] > settings.THRESHOLD)
        sims.append({
            "is_indentified": is_indentified,
            "matcher_index": int(max_j),
            "bouding_box": bounding_boxes[i]
        })
    print(dis)
    print(sims)
    users = []
    for (i, sim) in enumerate(sims):
        if sim['is_indentified']:
            matcher_index = sim['matcher_index']
            user_serializer = UserSerializer(User.objects.get(pk=user_matcher[matcher_index]))
            users.append(user_serializer.data)
    print("[SUCCESS] Identify face")

    return Response({"result": users})
