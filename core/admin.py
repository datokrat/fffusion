from django.contrib import admin

from .models import Post, Reply, Ontology

admin.site.register(Post)
admin.site.register(Reply)
admin.site.register(Ontology)
