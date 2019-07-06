from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from .forms import CreatePostForm
from .models import Post, Reply, ModeratedPost, ModeratedReply, UserEx, ReplyModeration, ModeratorSubscription, ClipboardItem

def dashboard(request):
    return render(request=request, template_name="fffusion/intro.html")

def post(request, postid):
    post = ModeratedPost(get_object_or_404(Post.objects, id=postid), request.user)
    if request.user.is_authenticated:
        clipboard_items = ClipboardItem.objects.filter(owner=request.user).all()
    else:
        clipboard_items = False

    return render(request=request, template_name="fffusion/post.html", context={"post": post, "clipboard_items": clipboard_items})

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

def reply_from_clipboard(request, replytoid):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    reply_to = get_object_or_404(Post.objects, id=replytoid)

    clipboard_items = ClipboardItem.objects.filter(owner=request.user).all()

    return render(request=request, template_name="fffusion/reply_from_clipboard.html", context={"clipboard_items": clipboard_items, "reply_to":reply_to})

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
            return HttpResponse("Der Moderationswert ist ungültig!")

        return HttpResponseRedirect(reverse("core:post", kwargs={"postid": reply.to_post().id()}))
    else:
        return HttpResponseRedirect(reverse("login"))

def moderation_dashboard(request):
    return HttpResponseRedirect(reverse("core:moderation_dashboard_moderators"))

def moderation_dashboard_moderators(request):
    # TODO: asymptotic performance
    # TODO: only when logged in
    moderator_candidates = [ UserEx(u, request.user) for u in User.objects.all() if not UserEx(u, request.user).does_moderate() ]

    num_all = lambda u: u.common_moderations().count()
    num_fp = lambda u: u.false_positives().count()
    num_fn = lambda u: u.false_negatives().count()
    moderator_candidates.sort(key=lambda u: (num_all(u) * ((num_all(u) - num_fp(u) - 3 * num_fn(u)) / num_all(u))**3 if num_all(u) > 0 else -1))

    moderators = [ UserEx(s.moderator, request.user) for s in request.user.passive_moderator_subscriptions.all() ]

    return render(request=request, template_name="fffusion/moderation_dashboard.html", context={"moderator_candidates": moderator_candidates, "moderators": moderators})

def moderation_dashboard_posts(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    me = UserEx(request.user, request.user)

    my_moderations = me.all_moderations().all()
    return render(request=request, template_name="fffusion/moderation_dashboard_posts.html", context={"my_moderations": my_moderations})

def moderator_detail(request, modid):
    # TODO: only when logged in
    moderator = UserEx(get_object_or_404(User.objects, id=modid), request.user)

    moderated_replies = [ ModeratedReply(moderation.reply, request.user) for moderation in moderator.all_moderations().all() ]
    dissent_replies = [ (reply, reply.moderation_of(moderator.user), reply.moderation_of(request.user)) for reply in moderated_replies if reply.moderation_of(request.user) != reply.moderation_of(moderator.user) ]
    consent_replies = [ (reply, reply.moderation_of(moderator.user), reply.moderation_of(request.user)) for reply in moderated_replies if reply.moderation_of(request.user) == reply.moderation_of(moderator.user) ]

    return render(request=request, template_name="fffusion/moderator_detail.html", context={"moderator": moderator, "dissent_replies": dissent_replies, "consent_replies": consent_replies})

def moderator_subscribe(request, modid):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    moderator = UserEx(get_object_or_404(User.objects, id=modid), request.user)

    if not moderator.does_moderate():
        subscription = ModeratorSubscription(subscriber=request.user, moderator=moderator.user)
        subscription.full_clean()
        subscription.save()

    return HttpResponseRedirect(reverse("core:moderator_detail", kwargs={"modid":modid}))

def moderator_unsubscribe(request, modid):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    moderator = UserEx(get_object_or_404(User.objects, id=modid), request.user)

    ModeratorSubscription.objects.filter(subscriber=request.user, moderator=moderator.user).delete()

    return HttpResponseRedirect(reverse("core:moderator_detail", kwargs={"modid":modid}))

def edit_post(request, postid):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    post = get_object_or_404(Post.objects, id=postid)
    
    if request.user.id != post.creator.id:
        return HttpResponseRedirect(reverse("login"))

    if request.method == "POST":
        form = CreatePostForm(request.POST)
        if form.is_valid():
            ReplyModeration.objects.filter(reply__to_post=post).delete()
            ReplyModeration.objects.filter(reply__reply_post=post).delete()
            post.title = form.cleaned_data["title"]
            post.content = form.cleaned_data["content"]
            post.full_clean()
            post.save()

            return HttpResponseRedirect(reverse("core:post", kwargs={"postid": postid}))
        print(form)
        return HttpResponse("Fehler?")

    return render(request=request, template_name="fffusion/edit_post.html", context={"post": post})

def add_clipboard_item(request, postid):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    post = get_object_or_404(Post.objects, id=postid)

    if not ClipboardItem.objects.filter(owner=request.user, item=post).exists():
        item = ClipboardItem(owner=request.user, item=post)
        item.full_clean()
        item.save()

    return HttpResponseRedirect(reverse("core:post", kwargs={"postid": postid}))

def remove_clipboard_item(request, postid):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    post = get_object_or_404(Post.objects, id=postid)
    ClipboardItem.objects.filter(owner=request.user, item=post).delete()

    return HttpResponseRedirect(reverse("core:post", kwargs={"postid": postid}))

def link_reply(request, replytoid, replyid):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    to_post = get_object_or_404(Post.objects, id=replytoid)
    reply_post = get_object_or_404(Post.objects, id=replyid)

    if not Reply.objects.filter(to_post=to_post, reply_post=reply_post).exists():
        reply = Reply(to_post=to_post, reply_post=reply_post)
        reply.full_clean()
        reply.save()

    return HttpResponseRedirect(reverse("core:post", kwargs={"postid": replytoid}))
