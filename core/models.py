from django.db import models

# Create your models here.
class Ontology(models.Model):
    title = models.CharField(max_length=255)
    root = models.ForeignKey("Post", on_delete=models.SET_NULL, null=True, blank=True)
    contained_replies = models.ManyToManyField("Reply", related_name="belongs_to_ontologies", blank=True)

class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(max_length=65535, blank=True)
    reply_posts = models.ManyToManyField("self", related_name="is_reply_to", symmetrical=False, through="Reply")
    # TODO: versions

class Reply(models.Model):
    to_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="replies")
    reply_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reverse_replies")

