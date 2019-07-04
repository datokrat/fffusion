from django.contrib.auth.models import User
from django.db import models

class UserEx:
    def __init__(self, user, perspective_of_user):
        self.user = user
        self.perspective_of_user = perspective_of_user

    def false_positives(self):
        correct_moderated_replies = self.perspective_of_user.reply_moderations.filter(appropriate=-1).values_list("reply", flat=True)
        my_moderated_replies = self.user.reply_moderations.filter(appropriate=1).values_list("reply", flat=True)

        false_positives = my_moderated_replies.intersection(correct_moderated_replies)
        return false_positives

    def false_negatives(self):
        correct_moderated_replies = self.perspective_of_user.reply_moderations.filter(appropriate=1).values_list("reply", flat=True)
        my_moderated_replies = self.user.reply_moderations.filter(appropriate=-1).values_list("reply", flat=True)

        false_negatives = my_moderated_replies.intersection(correct_moderated_replies)
        return false_negatives

    def positive_moderations(self):
        return self.user.reply_moderations.filter(appropriate=1)

    def negative_moderations(self):
        return self.user.reply_moderations.filter(appropriate=-1)

    def common_moderations(self):
        return self.user.reply_moderations.exclude(appropriate=0)\
            .intersection(self.perspective_of_user.reply_moderations.exclude(appropriate=0))

    def num_correlated_moderations(self):
        return self.common_moderations().count() - self.false_positives().count() - self.false_negatives().count()

    def all_moderations(self):
        return self.user.reply_moderations.exclude(appropriate=0)

    def does_moderate(self):
        return ModeratorSubscription.objects.filter(subscriber=self.perspective_of_user, moderator=self.user).exists()

class ModeratedPost:
    def __init__(self, post, user):
        self.post = post
        self.user = user

    def replies(self):
        return [ ModeratedReply(r, self.user) for r in self.post.replies.all() if r.get_collective_moderation(self.user) == 1 ]

    def id(self):
        return self.post.id

    def title(self):
        return self.post.title

    def content(self):
        return self.post.content

    def creator(self):
        return self.post.creator

    def is_in_clipboard(self):
        return ClipboardItem.objects.filter(owner=self.user, item=self.post).exists()

class ModeratedReply:
    def __init__(self, reply, user):
        self.reply = reply
        self.user = user

    def id(self):
        return self.reply.id

    def my_moderation(self):
        return self.moderation_of(self.user)

    def moderation_of(self, other_user):
        return self.reply.get_my_moderation(other_user)

    def to_post(self):
        return ModeratedPost(self.reply.to_post, self.user)

    def reply_post(self):
        return ModeratedPost(self.reply.reply_post, self.user)
        
    def moderate(self, value):
        if self.reply.moderations.filter(moderator=self.user).exists():
            moderation = self.reply.moderations.get(moderator=self.user)
            moderation.appropriate = value
        else:
            moderation = ReplyModeration(moderator=self.user, reply=self.reply, appropriate=value)

        moderation.full_clean()
        moderation.save()



class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(max_length=65535, blank=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="created_posts", null=True)
    reply_posts = models.ManyToManyField("self", related_name="is_reply_to", symmetrical=False, through="Reply")
    # TODO: versions

class Reply(models.Model):
    to_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="replies")
    reply_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reverse_replies")

    def get_my_moderation(self, user):
        if self.moderations.filter(moderator=user).exists():
            return self.moderations.get(moderator=user).appropriate
        else:
            return 0

    def get_collective_moderation(self, user):
        if self.get_my_moderation(user) == -1:
            return -1

        moderators = user.passive_moderator_subscriptions.values_list("moderator", flat=True) #.values_list("moderator", flat=True).values_list("id", flat=True)
        #positive_votes = self.moderations.in_bulk(moderators, field_name="moderator_id").filter(appropriate=1).count()
        positive_votes = self.moderations.filter(moderator__in=moderators).filter(appropriate=1).count()
        #negative_votes = self.moderations.in_bulk(moderators, field_name="moderator_id").filter(appropriate=-1).count()
        negative_votes = self.moderations.filter(moderator__in=moderators).filter(appropriate=-1).count()

        if negative_votes == 0:
            return 1
        elif positive_votes > 0:
            return 1
        else:
            return -1

# Moderation

class ReplyModeration(models.Model):
    moderator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reply_moderations")
    reply = models.ForeignKey(Reply, on_delete=models.CASCADE, related_name="moderations")
    appropriate = models.IntegerField()

class ModeratorSubscription(models.Model):
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name="passive_moderator_subscriptions")
    moderator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="active_moderator_subscriptions")

# Clipboard

class ClipboardItem(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Post, on_delete=models.CASCADE)

