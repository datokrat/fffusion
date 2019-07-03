from django.urls import path

from . import views

app_name="core"
urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("ontology/<int:ontid>", views.ontology_dashboard, name="ontology_dashboard"),
    path("ontology/<int:ontid>/post/<int:postid>", views.ontology_post, name="ontology_post"),
]
