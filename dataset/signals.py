from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
import tensorflow as tf
from util.src.align import detect_face
from util.service import facenet
import pickle

from .models import Image, Dataset

with tf.Graph().as_default():
    sess = tf.Session(config=tf.ConfigProto(log_device_placement=False))
    with sess.as_default():
        pnet, rnet, onet = detect_face.create_mtcnn(sess, None)


@receiver(m2m_changed, sender=Dataset.images.through)
def align_dataset_photo(sender, instance, action, reverse, model, pk_set, using, *args, **kwargs):
    # Notice that we're checking for `created` here. We only want to do this
    # the first time the `User` instance is created. If the save that caused
    # this signal to be run was an update action, we know the user already
    # has a profile.
    if instance and action == 'post_add':
        for pk in pk_set:
            imageInstance = Image.objects.get(pk=pk)
            imagePath = imageInstance.image.path

            print("[INFO] Alignment: [{}]'s dataset photo - [{}], created by [{}]".format(instance.name,
                                                                                   imageInstance.image.url,
                                                                                   instance.user.username))
            (prewhitens, bounding_boxes) = facenet.align_face(pnet, rnet, onet, imagePath)

            encoded = pickle.dumps({
                'bouding_boxes': bounding_boxes,
                'prewhitens': prewhitens
            })
            imageInstance.encoding = encoded
            imageInstance.save()
            print("[SUCCESS] Alignment and save encoding to image table")