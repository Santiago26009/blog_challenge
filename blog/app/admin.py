from django.contrib import admin

from app.models import Comment, Like, Post, Profile, User

# Register your models here.
admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
