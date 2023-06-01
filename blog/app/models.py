from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.contrib.postgres.fields import ArrayField
from django.db import IntegrityError, models
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken


class BaseModel(models.Model):
    """ BaseModel base model.
        BaseModel acts as an abstract base class from which every
        other model in the project will inherit. This class provides
        every table with the following attributes:
            + created (DateTime): Store the datetime the object was created.
            + modified (DateTime): Store the last datetime the object was modified.
    """

    created = models.DateTimeField(
        'created at',
        auto_now_add=True,
        help_text='Date time on which the object was created.'
    )
    modified = models.DateTimeField(
        'modified at',
        auto_now=True,
        help_text='Date time on which the object was last modified.'
    )

    class Meta:
        """Meta option."""

        abstract = True

        get_latest_by = 'created'
        ordering = ['-created', '-modified']


class UserManager(BaseUserManager):
    """Creates and saves the users"""

    def create_user(self, email=None, first_name=None, last_name=None, password=None, **extra_fields):
        """Create and save a user with the given email and password."""
        if not email:
            raise ValueError("Users must have an email address or phone number")
        try:
            user = self.model(email=self.normalize_email(email), first_name=first_name, last_name=last_name, **extra_fields)
            user.set_password(password)
            user.save(using=self._db)
        except IntegrityError:
            raise ValidationError('A user with that email already exists.')
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        'email address',
        unique=True,
        null=True,
        error_messages={
            'unique': 'A user with that email already exists.'
        }
    )
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, unique=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'

    def get_short_name(self):
        """Return username"""
        return self.username

    def tokens(self):
        refresh = RefreshToken.for_user(self)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }


class Profile(BaseModel):
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    biography = models.TextField(max_length=255, blank=True)
    profile_image = models.ImageField(upload_to='uploads/')

    def __str__(self):
        """Return profile's str representation."""
        return str(self.user)


class Post(BaseModel):
    author = models.ForeignKey('User', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField(max_length=255, blank=True)
    publish_date = models.DateTimeField(null=True)
    category = models.CharField(max_length=255)
    tags = ArrayField(models.CharField(max_length=255, blank=True))


class Comment(BaseModel):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    text = models.TextField(max_length=255, blank=True)


class Like(BaseModel):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, null=True, blank=True)
