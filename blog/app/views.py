from django.contrib.auth import authenticate, logout
from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin,
                                   UpdateModelMixin)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.token_blacklist.models import (BlacklistedToken,
                                                             OutstandingToken)
from rest_framework_simplejwt.tokens import RefreshToken

from app.models import Comment, Like, Post, Profile, User
from app.serializers import (CommentSerializer, CreatePostSerializer,
                             LikeSerializer, LoginUserSerializer,
                             PostSerializer, ProfileSerializer,
                             ShowCommentSerializer, ShowLikeSerializer,
                             UpdateCommentSerializer, UserSerializer)


class UserSessionView(viewsets.GenericViewSet):
    """Views to configure endpoints for sign up, log in and logout for users"""
    permission_classes_by_action = {'signup': [AllowAny], 'login': [AllowAny], 'logout': [IsAuthenticated]}

    @extend_schema(
        request=UserSerializer,
        responses=None,
    )
    @action(detail=False, methods=['post'])
    def signup(self, request):
        user = request.data
        serializer = UserSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data

        return Response(user_data, status=status.HTTP_201_CREATED)

    @extend_schema(
        request=LoginUserSerializer,
        responses=LoginUserSerializer,
    )
    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = LoginUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = request.data.get('username')
        password = request.data.get('password', None)
        authenticate(username=username, password=password)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def logout(self, request, *args, **kwargs):
        if self.request.data.get('all'):
            tokens = OutstandingToken.objects.filter(user=request.user)
            for token in tokens:
                _, _ = BlacklistedToken.objects.get_or_create(token=token)
            logout(request)
            return Response({'status': 'OK, goodbye, all refresh tokens blacklisted'}, status=status.HTTP_200_OK)
        refresh_token = self.request.data.get('refresh_token')
        token = RefreshToken(token=refresh_token)
        token.blacklist()
        logout(request)
        return Response({'status': 'Logout'}, status=status.HTTP_200_OK)


class UserView(generics.RetrieveUpdateDestroyAPIView):
    """Views to configure endpoints for users"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return User.objects.get(id=self.request.user.id)


class ProfileView(generics.RetrieveUpdateDestroyAPIView, generics.CreateAPIView):
    """Views to configure endpoints for profiles"""
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            return Profile.objects.get(user=self.request.user.id)
        except ObjectDoesNotExist:
            raise ValidationError({'detail': 'No profile associated'})

    def create(self, request):
        profile = request.data
        context = {'user': self.request.user}
        serializer = self.serializer_class(data=profile, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=profile, status=status.HTTP_200_OK)


class PostView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    """Views to configure endpoints for posts"""
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=PostSerializer,
    )
    def get_queryset(self):
        queryset = Post.objects.all()
        return queryset

    @extend_schema(
        request=CreatePostSerializer,
        responses=CreatePostSerializer,
    )
    def create(self, request):
        post = request.data
        context = {'author': self.request.user}
        serializer = CreatePostSerializer(data=post, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=post, status=status.HTTP_201_CREATED)

    @extend_schema(
        request=CreatePostSerializer,
        responses=PostSerializer,
    )
    def update(self, request, *args, **kwargs):
        try:
            user = self.request.user
            post_id = kwargs['pk']
            post = Post.objects.get(id=post_id)
            if user == post.author:
                post.title = request.data['title']
                post.content = request.data['content']
                post.publish_date = request.data['publish_date']
                post.category = request.data['category']
                post.tags = request.data['tags']
                post.save()
                return Response(PostSerializer(post).data, status=status.HTTP_200_OK)
            raise ValidationError({'detail': 'You cannot update someone else post'})
        except ObjectDoesNotExist:
            raise ValidationError({'detail': 'No post found'})

    @extend_schema(
        request=CreatePostSerializer,
        responses=PostSerializer,
    )
    def partial_update(self, request, *args, **kwargs):
        try:
            user = self.request.user
            post_id = kwargs['pk']
            post = Post.objects.get(id=post_id)
            if user == post.author:
                Post.objects.filter(id=post_id).update(**request.data)
                return Response(PostSerializer(Post.objects.get(id=post_id)).data, status=status.HTTP_200_OK)
            raise ValidationError({'detail': 'You cannot update someone else post'})
        except ObjectDoesNotExist:
            raise ValidationError({'detail': 'No post found'})

    def destroy(self, request, *args, **kwargs):
        try:
            user = self.request.user
            post_id = kwargs['pk']
            post = Post.objects.get(id=post_id)
            if user == post.author:
                post.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            raise ValidationError({'detail': 'You cannot delete someone else post'})
        except ObjectDoesNotExist:
            raise ValidationError({'detail': 'No post found'})


class CommentView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    """Views to configure endpoints for comments"""
    serializer_class = ShowCommentSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=ShowCommentSerializer,
    )
    def get_queryset(self):
        queryset = Comment.objects.all()
        return queryset

    @extend_schema(
        request=CommentSerializer,
        responses=CommentSerializer,
    )
    def create(self, request):
        comment = request.data
        context = {'user': self.request.user}
        serializer = CommentSerializer(data=comment, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=comment, status=status.HTTP_201_CREATED)

    @extend_schema(
        request=UpdateCommentSerializer,
        responses=ShowCommentSerializer,
    )
    def update(self, request, *args, **kwargs):
        try:
            user = self.request.user
            comment_id = kwargs['pk']
            comment = Comment.objects.get(id=comment_id)
            if user == comment.user:
                comment.text = request.data['text']
                comment.save()
                return Response(ShowCommentSerializer(comment).data, status=status.HTTP_200_OK)
            raise ValidationError({'detail': 'You cannot update someone else comment'})
        except ObjectDoesNotExist:
            raise ValidationError({'detail': 'No comment found'})

    @extend_schema(
        request=UpdateCommentSerializer,
        responses=ShowCommentSerializer,
    )
    def partial_update(self, request, *args, **kwargs):
        try:
            user = self.request.user
            comment_id = kwargs['pk']
            comment = Comment.objects.get(id=comment_id)
            if user == comment.user:
                comment.text = request.data['text']
                comment.save()
                return Response(ShowCommentSerializer(comment).data, status=status.HTTP_200_OK)
            raise ValidationError({'detail': 'You cannot update someone else comment'})
        except ObjectDoesNotExist:
            raise ValidationError({'detail': 'No comment found'})

    def destroy(self, request, *args, **kwargs):
        try:
            user = self.request.user
            comment_id = kwargs['pk']
            comment = Comment.objects.get(id=comment_id)
            if user == comment.user:
                comment.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            raise ValidationError({'detail': 'You cannot delete someone else comment'})
        except ObjectDoesNotExist:
            raise ValidationError({'detail': 'No comment found'})


class LikeView(ListModelMixin, CreateModelMixin, DestroyModelMixin, GenericViewSet):
    """Views to configure endpoints for likes"""
    serializer_class = ShowLikeSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=ShowLikeSerializer,
    )
    def get_queryset(self):
        queryset = Like.objects.all()
        return queryset

    @extend_schema(
        request=LikeSerializer,
    )
    def create(self, request):
        like = request.data
        context = {'user': self.request.user}
        serializer = LikeSerializer(data=like, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=like, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        try:
            user = self.request.user
            like_id = kwargs['pk']
            like = Like.objects.get(id=like_id)
            if user == like.user:
                like.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            raise ValidationError({'detail': 'You cannot delete someone else comment'})
        except ObjectDoesNotExist:
            raise ValidationError({'detail': 'No comment found'})
