from rest_framework import serializers
from django.contrib.auth import authenticate

from .models import User, WhatIValue
from dataset.models import Dataset
from dataset.serializers import DatasetSerializer, ImageSerializer


class WhatIValueSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255)
    score = serializers.IntegerField()

    class Meta:
        model = WhatIValue
        fields = ('pk', 'name', 'score')


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializers registration requests and creates a new user."""

    # Ensure passwords are at least 8 characters long, no longer than 128
    # characters, and can not be read by the client.
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    # The client should not be able to send a token along with a registration
    # request. Making `token` read-only handles that for us.
    token = serializers.CharField(max_length=255, read_only=True)

    birthday = serializers.DateField()
    gender = serializers.ChoiceField(choices=[0, 1, 2])

    dataset = DatasetSerializer(many=False, read_only=True)
    photos = ImageSerializer(many=True, write_only=True)
    avatar = ImageSerializer(many=False, required=False)
    position = serializers.CharField(max_length=255)
    company = serializers.CharField(max_length=255)
    bio = serializers.CharField(max_length=255, required=False)
    my_style = serializers.CharField(max_length=255, required=False)
    how_to_help_me = serializers.CharField(max_length=255, required=False)
    what_i_values = WhatIValueSerializer(many=True, required=False)

    class Meta:
        model = User
        # List all of the fields that could possibly be included in a request
        # or response, including fields specified explicitly above.
        fields = ['email', 'username', 'password', 'token', 'gender', 'birthday', 'dataset', 'photos', 'avatar',
                  'position', 'company', 'bio', 'my_style', 'how_to_help_me', 'what_i_values']

    def create(self, validated_data):
        photos = validated_data.pop('photos', None)
        avatar = validated_data.pop('avatar', None)
        what_i_values = validated_data.pop('what_i_values', None)

        # Use the `create_user` method we wrote earlier to create a new user.
        instance = User.objects.create_user(**validated_data)
        instance.dataset = Dataset.objects.create(user=instance)

        if photos is not None:
            for photo in photos:
                photo_serializer = ImageSerializer(data=photo)
                photo_serializer.is_valid(raise_exception=True)
                photo_instance = photo_serializer.save()
                # instance.photos.add(photo_instance)
                instance.dataset.images.add(photo_instance)

        if avatar is not None:
            avatar_serializer = ImageSerializer(data=avatar)
            avatar_serializer.is_valid(raise_exception=True)
            avatar_instance = avatar_serializer.save()
            instance.avatar = avatar_instance

        if what_i_values is not None:
            for what_i_value in what_i_values:
                what_i_value_serializer = WhatIValueSerializer(data=what_i_value)
                what_i_value_serializer.is_valid(raise_exception=True)
                what_i_value_instance = what_i_value_serializer.save()
                instance.what_i_values.add(what_i_value_instance)

        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255, read_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        # The `validate` method is where we make sure that the current
        # instance of `LoginSerializer` has "valid". In the case of logging a
        # user in, this means validating that they've provided an email
        # and password and that this combination matches one of the users in
        # our database.
        email = data.get('email', None)
        password = data.get('password', None)

        # Raise an exception if an
        # email is not provided.
        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )

        # Raise an exception if a
        # password is not provided.
        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        # The `authenticate` method is provided by Django and handles checking
        # for a user that matches this email/password combination. Notice how
        # we pass `email` as the `username` value since in our User
        # model we set `USERNAME_FIELD` as `email`.
        user = authenticate(username=email, password=password)

        # If no user was found matching this email/password combination then
        # `authenticate` will return `None`. Raise an exception in this case.
        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )

        # Django provides a flag on our `User` model called `is_active`. The
        # purpose of this flag is to tell us whether the user has been banned
        # or deactivated. This will almost never be the case, but
        # it is worth checking. Raise an exception in this case.
        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        # The `validate` method should return a dictionary of validated data.
        # This is the data that is passed to the `create` and `update` methods
        # that we will see later on.
        return {
            'email': user.email,
            'username': user.username,
            'token': user.token
        }


class UserSerializer(serializers.ModelSerializer):
    """Handles serialization and deserialization of User objects."""

    # Passwords must be at least 8 characters, but no more than 128
    # characters. These values are the default provided by Django. We could
    # change them, but that would create extra work while introducing no real
    # benefit, so lets just stick with the defaults.
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    dataset = DatasetSerializer(many=False)
    photos = ImageSerializer(many=True, write_only=True)
    avatar = ImageSerializer(many=False, required=False)
    what_i_values = WhatIValueSerializer(many=True, required=False)

    class Meta:
        model = User
        fields = (
            'email', 'username', 'password', 'gender', 'birthday', 'dataset', 'photos', 'avatar', 'company', 'bio',
            'position', 'my_style', 'how_to_help_me', 'what_i_values')

        # The `read_only_fields` option is an alternative for explicitly
        # specifying the field with `read_only=True` like we did for password
        # above. The reason we want to use `read_only_fields` here is that
        # we don't need to specify anything else about the field. The
        # password field needed the `min_length` and
        # `max_length` properties, but that isn't the case for the token
        # field.
        read_only_fields = ('token',)

    def update(self, instance, validated_data):
        """Performs an update on a User."""

        # Passwords should not be handled with `setattr`, unlike other fields.
        # Django provides a function that handles hashing and
        # salting passwords. That means
        # we need to remove the password field from the
        # `validated_data` dictionary before iterating over it.
        password = validated_data.pop('password', None)
        photos = validated_data.pop('photos', None)
        avatar = validated_data.pop('avatar', None)
        what_i_values = validated_data.pop('what_i_values', None)

        for (key, value) in validated_data.items():
            # For the keys remaining in `validated_data`, we will set them on
            # the current `User` instance one at a time.
            setattr(instance, key, value)

        if password is not None:
            # `.set_password()`  handles all
            # of the security stuff that we shouldn't be concerned with.
            instance.set_password(password)

        if photos is not None:
            instance.dataset.images.all().delete()
            for photo in photos:
                photo_serializer = ImageSerializer(data=photo)
                photo_serializer.is_valid(raise_exception=True)
                photo_instance = photo_serializer.save()
                instance.dataset.images.add(photo_instance)

        if avatar is not None:
            if instance.avatar is not None:
                instance.avatar.delete()
            avatar_serializer = ImageSerializer(data=avatar)
            avatar_serializer.is_valid(raise_exception=True)
            avatar_instance = avatar_serializer.save()
            instance.avatar = avatar_instance

        if what_i_values is not None:
            instance.what_i_values.all().delete()
            for what_i_value in what_i_values:
                what_i_value_serializer = WhatIValueSerializer(data=what_i_value)
                what_i_value_serializer.is_valid(raise_exception=True)
                what_i_value_instance = what_i_value_serializer.save()
                instance.what_i_values.add(what_i_value_instance)

        # After everything has been updated we must explicitly save
        # the model. It's worth pointing out that `.set_password()` does not
        # save the model.
        instance.save()

        return instance
