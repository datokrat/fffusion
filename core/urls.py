from django.urls import path

from . import views

app_name="core"
urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("post/<int:postid>", views.post, name="post"),
    path("edit_post/<int:postid>", views.edit_post, name="edit_post"),
    path("create_reply/to/<int:replytoid>", views.create_reply, name="create_reply"),
    path("reply_from_clipboard/<int:replytoid>", views.reply_from_clipboard, name="reply_from_clipboard"),
    path("link_reply/to/<int:replytoid>/reply/<int:replyid>", views.link_reply, name="link_reply"),
    path("moderation/reply/<int:repid>/value/<str:value>", views.moderate_reply, name="moderate_reply"),
    path("moderation/dashboard", views.moderation_dashboard, name="moderation_dashboard"),
    path("moderation/moderators", views.moderation_dashboard_moderators, name="moderation_dashboard_moderators"),
    path("moderation/posts", views.moderation_dashboard_posts, name="moderation_dashboard_posts"),
    path("moderation/moderator/<int:modid>", views.moderator_detail, name="moderator_detail"),
    path("moderation/subscribe/<int:modid>", views.moderator_subscribe, name="moderator_subscribe"),
    path("moderation/unsubscribe/<int:modid>", views.moderator_unsubscribe, name="moderator_unsubscribe"),
    path("clibpoard/new_item/<int:postid>", views.add_clipboard_item, name="add_clipboard_item"),
    path("clibpoard/remove_item/<int:postid>", views.remove_clipboard_item, name="remove_clipboard_item"),
]
