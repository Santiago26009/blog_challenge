from django.contrib.auth import authenticate, get_user_model
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, ValidationError

from app.models import Comment, Like, Post, Profile


class LoginUserSerializer(serializers.ModelSerializer):
    """Serializer for the login"""
    username = serializers.CharField(max_length=17)
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    tokens = serializers.SerializerMethodField()

    def get_tokens(self, obj):
        user = get_user_model().objects.get(username=obj['username'])
        return {
            'access': user.tokens()['access'],
            'refresh': user.tokens()['refresh']
        }

    class Meta:
        model = get_user_model()
        fields = ('username', 'password', 'tokens')
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def validate(self, attrs):
        username = attrs.get('username', None)
        password = attrs.get('password', None)
        user = authenticate(username=username, password=password)
        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        return {
            'username': username,
            'tokens': user.tokens()
        }


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user object"""

    class Meta:
        model = get_user_model()
        fields = ('email', 'first_name', 'last_name', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 6}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for profile object"""

    class Meta:
        model = Profile
        fields = ('biography', 'profile_image')

    def create(self, validated_data):
        """Create profile"""
        try:
            user = self.context['user']
            biography = validated_data.pop('biography')
            profile_image = validated_data.pop('profile_image')

            return Profile.objects.create(user=user, biography=biography, profile_image=profile_image)
        except IntegrityError:
            raise ValidationError({'detail': 'Profile exists'})


class PostSerializer(serializers.ModelSerializer):
    """Serializer for post object"""

    class Meta:
        model = Post
        fields = ('id', 'author', 'title', 'content', 'publish_date', 'category', 'tags')


class CreatePostSerializer(serializers.ModelSerializer):
    """Serializer for create update post object"""

    class Meta:
        model = Post
        fields = ('title', 'content', 'publish_date', 'category', 'tags')

    def create(self, validated_data):
        """Create post"""
        author = self.context['author']
        title = validated_data.pop('title')
        content = validated_data.pop('content')
        publish_date = validated_data.pop('publish_date')
        category = validated_data.pop('category')
        tags = validated_data.pop('tags')

        return Post.objects.create(
            author=author, title=title, content=content, publish_date=publish_date, category=category, tags=tags
        )


class ShowCommentSerializer(serializers.ModelSerializer):
    """Serializer for comment object"""

    class Meta:
        model = Comment
        fields = ('id', 'user', 'post', 'text')


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comment object"""

    class Meta:
        model = Comment
        fields = ('post', 'text')

    def create(self, validated_data):
        """Create comment"""
        user = self.context['user']
        post = Post.objects.get(id=validated_data.pop('post').id)
        text = validated_data.pop('text')
        return Comment.objects.create(user=user, post=post, text=text)


class UpdateCommentSerializer(serializers.ModelSerializer):
    """Serializer for comment object"""

    class Meta:
        model = Comment
        fields = ('text',)


class LikeSerializer(serializers.ModelSerializer):
    """Serializer for like object"""

    class Meta:
        model = Like
        fields = ('post', 'comment')

    def create(self, validated_data):
        """Create like"""
        user = self.context['user']
        if 'post' in validated_data and 'comment' in validated_data:
            raise ValidationError({'detail': 'You cannot like a comment and a post at the same time'})
        elif 'comment' in validated_data:
            comment = Comment.objects.get(id=validated_data.pop('comment').id)
            previous_like = Like.objects.filter(user=user, comment=comment).count()
            if previous_like == 1:
                raise ValidationError({'detail': 'You already liked this comment'})
            Like.objects.create(user=user, comment=comment)
        elif 'post' in validated_data:
            post = Post.objects.get(id=validated_data.pop('post').id)
            previous_like = Like.objects.filter(user=user, post=post).count()
            if previous_like == 1:
                raise ValidationError({'detail': 'You already liked this post'})
            Like.objects.create(user=user, post=post)
        else:
            raise ValidationError({'detail': 'You did not set the object you like'})
        return {'detail': 'Liked'}


class ShowLikeSerializer(serializers.ModelSerializer):
    """Serializer for show like"""

    class Meta:
        model = Like
        fields = ('id', 'user', 'post', 'comment')
