from django.db import models
from core.models import TimestampedModel


class Dataset(TimestampedModel):
    # identify user who use this dataset
    user = models.OneToOneField(
        'authentication.User', on_delete=models.CASCADE
    )

    # person's name of this dataset
    # name = models.CharField(max_length=256)

    # person's photos of this dataset
    images = models.ManyToManyField('Image', related_name="image_dataset")

    def __str__(self):
        return self.user.username


class Image(TimestampedModel):
    # field for storing image
    image = models.ImageField(upload_to='images/%Y/%m/%d/')

    # field for storing alignment image
    encoding = models.BinaryField(null=True, blank=True, default=None)

    # Django is using this method to display an object in the Django admin site
    def __str__(self):
        return self.image