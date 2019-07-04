from django.urls import path

from . import views

app_name="core"
urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("post/<int:postid>", views.post, name="post"),
    path("create_reply/to/<int:replytoid>", views.create_reply, name="create_reply"),
    path("moderate/reply/<int:repid>/value/<str:value>", views.moderate_reply, name="moderate_reply"),
    path("moderation_dashboard", views.moderation_dashboard, name="moderation_dashboard"),
]
