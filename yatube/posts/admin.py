from django.conf import settings
from django.contrib import admin

from .models import Group, Post, Comment, Follow


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = settings.EMPTY_VALUE_DISPLAY


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'slug',
        'description',
    )
    list_editable = ('slug',)
    search_fields = ('title',)
    list_filter = ('description',)
    empty_value_display = settings.EMPTY_VALUE_DISPLAY


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'post',
        'author',
        'text',
        'created',
    )
    list_editable = ('author',)
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = settings.EMPTY_VALUE_DISPLAY


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'user',
    )
    list_editable = ('user',)
    search_fields = ('user',)
    list_filter = ('user',)
