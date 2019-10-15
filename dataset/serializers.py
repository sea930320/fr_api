from rest_framework import serializers
from django.core.files.base import ContentFile
from rest_framework.validators import ValidationError
import base64
import six
import uuid
import imghdr

from .models import Dataset, Image
from authentication.serializers import UserSerializer


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the base64 string is in the "data:" format
            if 'data:' in data and ';base64,' in data:
                # Break out the header from the base64 content
                header, data = data.split(';base64,')

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            # Generate file name:
            file_name = str(uuid.uuid4())[:12]  # 12 characters are more than enough.
            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = "%s.%s" % (file_name, file_extension,)

            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


class ImageSerializer(serializers.ModelSerializer):
    image = Base64ImageField(
        max_length=None, use_url=True,
    )

    class Meta:
        model = Image
        fields = ('pk', 'image')


class DatasetSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    images = ImageSerializer(many=True, read_only=True)

    name = serializers.CharField(max_length=255, required=True)

    user_id = serializers.IntegerField(write_only=True, required=True)
    image = ImageSerializer(many=False, write_only=True, required=False)

    class Meta:
        model = Dataset
        fields = ['pk', 'user', 'user_id', 'name', 'images', 'image']

    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        name = validated_data.get('name')
        if Dataset.objects.filter(user_id=user_id, name=name).exists():
            raise ValidationError("This person's name already exists, please use another name")
        return Dataset.objects.create(**validated_data)

    def update(self, instance, validated_data):
        image_data = validated_data.pop('image', None)

        for (key, value) in validated_data.items():
            # For the keys remaining in `validated_data`, we will set them on
            # the current `Dataset` instance one at a time.
            if key == 'name':
                if Dataset.objects.filter(user_id=instance.user_id, name=value).exclude(pk=instance.pk).exists():
                    raise ValidationError("This person's name already exists, please use another name")
            setattr(instance, key, value)

        if image_data is not None:
            image_serializer = ImageSerializer(data=image_data)
            image_serializer.is_valid(raise_exception=True)
            image_instance = image_serializer.save()

            instance.images.add(image_instance)
        # After everything has been updated we must explicitly save
        # the model. It's worth pointing out that `.set_password()` does not
        # save the model.
        instance.save()

        return instance
