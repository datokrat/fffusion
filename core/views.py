from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from .forms import CreatePostForm
from .models import Post, Reply, ModeratedPost, ModeratedReply, UserEx

def dashboard(request):
    return render(request=request, template_name="fffusion/base.html")

def post(request, postid):
    post = ModeratedPost(get_object_or_404(Post.objects, id=postid), request.user)
    #replies = [ {"res": r, "mod": r.get_my_moderation(request.user)} for r in post.replies.all() if r.get_collective_moderation(request.user) == 1 ]
    return render(request=request, template_name="fffusion/post.html", context={"post": post })

def create_reply(request, replytoid):
    reply_to = get_object_or_404(Post.objects, id=replytoid)

    if request.method == "POST":
        if request.user.is_authenticated:
            form = CreatePostForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                post.creator = request.user
                post.full_clean()
                post.save()
                
                reply = Reply(to_post=reply_to, reply_post=post)
                reply.full_clean()
                reply.save()

                return HttpResponseRedirect(reverse("core:post", kwargs={"postid": post.id}))
        else:
            return HttpResponse("Du musst angemeldet sein, um Beiträge zu schreiben.")
    return render(request=request, template_name="fffusion/create_post.html", context={"reply_to": reply_to})

def moderate_reply(request, repid, value):
    if request.user.is_authenticated:
        reply = ModeratedReply(Reply.objects.get(id=repid), request.user)

        if value == "positive":
            reply.moderate(1)
        elif value == "negative":
            reply.moderate(-1)
        elif value == "neutral":
            reply.moderate(0)
        else:
            return HttpResponseRedirect("Der Moderationswert ist ungültig!")

        return HttpResponseRedirect(reverse("core:post", kwargs={"postid": reply.to_post().id()}))
    else:
        return HttpResponseRedirect(reverse("login"))

def moderation_dashboard(request):
    # TODO: asymptotic performance
    moderator_candidates = [ UserEx(u, request.user) for u in User.objects.all() if not UserEx(u, request.user).does_moderate() ]

    num_all = lambda u: u.common_moderations().count()
    num_fp = lambda u: u.false_positives().count()
    num_fn = lambda u: u.false_negatives().count()
    moderator_candidates.sort(key=lambda u: (num_all(u) * ((num_all(u) - num_fp(u) - 3 * num_fn(u)) / num_all(u))**3 if num_all(u) > 0 else -1))

    moderators = [ UserEx(u, request.user) for u in request.user.passive_moderator_subscriptions.values_list("moderator", flat=True) ]

    return render(request=request, template_name="fffusion/moderation_dashboard.html", context={"moderator_candidates": moderator_candidates, "moderators": moderators})
