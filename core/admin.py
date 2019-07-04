from django.contrib import admin

from .models import Post, Reply, ReplyModeration, ModeratorSubscription

admin.site.register(Post)
admin.site.register(Reply)
admin.site.register(ReplyModeration)
admin.site.register(ModeratorSubscription)
