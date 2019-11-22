import jwt

from datetime import datetime, timedelta, timezone

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.db import models
from core.models import TimestampedModel
from dataset.models import Image


class UserManager(BaseUserManager):
    """
    Django requires that custom users define their own Manager class. By
    inheriting from `BaseUserManager`, we get a lot of the same code used by
    Django to create a `User`.

    All we have to do is override the `create_user` function which we will use
    to create `User` objects.
    """

    def create_user(self, firstname, lastname, email, password=None, gender=0, birthday=None, position=None, company=None,
                    bio=None, my_style=None, how_to_help_me=None):
        """Create and return a `User` with an email, firstname, lastname and password."""
        if firstname is None:
            raise TypeError('Users must have a fist name.')

        if lastname is None:
            raise TypeError('Users must have a last name.')

        if email is None:
            raise TypeError('Users must have an email address.')

        user = self.model(firstname=firstname, lastname=lastname, email=self.normalize_email(email), gender=gender, birthday=birthday,
                          position=position, company=company, bio=bio, my_style=my_style, how_to_help_me=how_to_help_me)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, firstname, lastname, email, password):
        """
        Create and return a `User` with superuser (admin) permissions.
        """
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(firstname, lastname, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class WhatIValue(TimestampedModel):
    # name of whativalue
    name = models.CharField(max_length=256)

    # score of whativalue
    score = models.IntegerField()

    # Django is using this method to display an object in the Django admin site
    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin, TimestampedModel):
    # Each `User` needs a human-readable unique identifier that we can use to
    # represent the `User` in the UI. We want to index this column in the
    # database to improve lookup performance.
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)

    # We also need a way to contact the user and a way for the user to identify
    # themselves when logging in. Since we need an email address for contacting
    # the user anyways, we will also use the email for logging in because it is
    # the most common form of login credential at the time of writing.
    email = models.EmailField(db_index=True, unique=True)

    # When a user no longer wishes to use our platform, they may try to delete
    # their account. That's a problem for us because the data we collect is
    # valuable to us and we don't want to delete it. We
    # will simply offer users a way to deactivate their account instead of
    # letting them delete it. That way they won't show up on the site anymore,
    # but we can still analyze the data.
    is_active = models.BooleanField(default=True)

    # The `is_staff` flag is expected by Django to determine who can and cannot
    # log into the Django admin site. For most users this flag will always be
    # false.
    is_staff = models.BooleanField(default=False)

    # More fields required by Django when specifying a custom user model.
    position = models.CharField(max_length=255, default=None, null=True, blank=True)
    gender = models.IntegerField(default=0, choices=((0, "Male"), (1, "Female"), (2, "Other")))
    birthday = models.DateField(auto_now=False, null=True, blank=True)

    # photos = models.ManyToManyField(Image, related_name="photo_user")
    avatar = models.OneToOneField(
        Image, on_delete=models.SET_NULL, default=None, null=True, blank=True
    )
    company = models.CharField(max_length=255, default=None, null=True, blank=True)
    bio = models.CharField(max_length=255, default=None, null=True, blank=True)
    my_style = models.CharField(max_length=255, default=None, null=True, blank=True)
    how_to_help_me = models.CharField(max_length=255, default=None, null=True, blank=True)
    what_i_values = models.ManyToManyField(WhatIValue, related_name="what_i_value_user")

    # The `USERNAME_FIELD` property tells us which field we will use to log in.
    # In this case we want it to be the email field.
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname']

    # Tells Django that the UserManager class defined above should manage
    # objects of this type.
    objects = UserManager()

    def __str__(self):
        """
        Returns a string representation of this `User`.

        This string is used when a `User` is printed in the console.
        """
        return self.email

    @property
    def token(self):
        """
        Allows us to get a user's token by calling `user.token` instead of
        `user.generate_jwt_token().

        The `@property` decorator above makes this possible. `token` is called
        a "dynamic property".
        """
        return self._generate_jwt_token()

    def get_full_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically this would be the user's first and last name. Since we do
        not store the user's real name, we return their username instead.
        """
        return self.firstname + "" + self.lastname

    def get_short_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically, this would be the user's first name. Since we do not store
        the user's real name, we return their username instead.
        """
        return self.firstname

    def _generate_jwt_token(self):
        """
        Generates a JSON Web Token that stores this user's ID and has an expiry
        date set to 60 days into the future.
        """
        dt = datetime.now() + timedelta(days=60)

        token = jwt.encode({
            'id': self.pk,
            'exp': (dt.replace(tzinfo=timezone.utc).timestamp() * 1000)
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')
