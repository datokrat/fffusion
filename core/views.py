from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Ontology, Post

def dashboard(request):
    return render(request=request, template_name="fffusion/base.html")

def ontology_dashboard(request, ontid):
    ontology = get_object_or_404(Ontology.objects, id=ontid)
    return render(request=request, template_name="fffusion/ontology_dashboard.html", context={"ontology": ontology})

def ontology_post(request, ontid, postid):
    ontology = get_object_or_404(Ontology.objects, id=ontid)
    post = get_object_or_404(Post.objects, id=postid)
    return render(request=request, template_name="fffusion/ontology_post.html", context={"ontology": ontology, "post": post})
