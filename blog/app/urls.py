from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'app'

router = DefaultRouter()
router.register('', views.UserSessionView, basename='session'),
router.register('post', views.PostView, basename='post')
router.register('comment', views.CommentView, basename='comment')
router.register('like', views.LikeView, basename='like')

urlpatterns = [
    path('user/', views.UserView.as_view(), name='user'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('', include(router.urls)),
]
