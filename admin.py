from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Post, Comment, Favourites, Like, File, Contacts, Profile, Advert, Gallary
from django.contrib.admin import ModelAdmin, site
from .models import MessageModel


class MessageModelAdmin(ModelAdmin):
    readonly_fields = ('timestamp',)
    search_fields = ('id', 'body', 'user__username', 'recipient__username')
    list_display = ('id', 'user', 'recipient', 'timestamp', 'characters')
    list_display_links = ('id',)
    list_filter = ('user', 'recipient')
    date_hierarchy = 'timestamp'


site.register(MessageModel, MessageModelAdmin)


class UserModel(UserAdmin):
    pass

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Favourites)
admin.site.register(Like)
admin.site.register(File)
admin.site.register(Contacts)
admin.site.register(Profile)
admin.site.register(Advert)
admin.site.register(Gallary)
# Register your models here.
