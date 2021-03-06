from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
import json
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Post, Comment, Like, Notification
from .forms import PostForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
import datetime

# Create your views here.
def profile(request):
    if request.user.is_authenticated:
        return render(request, 'blog/profile.html') 
    else:
        return HttpResponseRedirect('/login')

def home(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user_id =request.user.id).order_by("-id")
        posts_list = Post.objects.all().order_by("-timestamp")
        searchquery = request.GET.get("searchquery")
        if searchquery:
            posts_list = posts_list.filter(Q(tags=searchquery)| Q(title=searchquery)| Q(author_name=searchquery)).distinct()
        paginator = Paginator(posts_list,5)
        page = request.GET.get('page')
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        context = {
            'room_name_json': request.user.id,
            'user_name': mark_safe(json.dumps(request.user.username)),
            'notifications': notifications,
            'posts': posts
        }
        return render(request, 'blog/home.html',context)
    else:
        return HttpResponseRedirect('/login')

def addblog(request):
    if request.user.is_authenticated:
        form = PostForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author_id = request.user.id
            instance.author_name = request.user.username
            instance.save()
            return HttpResponseRedirect('/home/')
        context = {
            'form':form,
        }
        return render(request, 'blog/post_form.html', context)
    else:
        return HttpResponseRedirect('/login')

def blog(request, id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            comment = request.POST['comment-text']
            post_id = id
            post = Post.objects.get(id = id)
            comment_author = request.user.username
            comment_to_post_author_id = post.author_id
            com = Comment(comment = comment, post_id = post_id, comment_author = comment_author, comment_to_post_author_id =comment_to_post_author_id)
            com.save()
            postid = int(id)
            like_author = request.user.username
            like_to_post_author_id = post.author_id
            likes, created = Like.objects.get_or_create(like_post_id = postid, like_author_id = request.user.id,like_author = like_author ,like_to_post_author_id = like_to_post_author_id )
            likes.save()
            link = '/home/blog/' + str(int(id))
            return redirect(link)
        else:
            post_id = str(id)
            post = Post.objects.get(id = post_id)
            comments = Comment.objects.filter(post_id = id)
            postid = int(id)
            like_author = request.user.username
            like_to_post_author_id = post.author_id
            likes, created = Like.objects.get_or_create(like_post_id = postid, like_author_id = request.user.id,like_author = like_author ,like_to_post_author_id = like_to_post_author_id ) 
            context = {
                'post':post,
                'comments':comments,
                'likes':likes
            }
            return render(request, 'blog/blog.html', context)
    else:
        return HttpResponseRedirect('/login')

def chat(request,room_name):
    if request.user.is_authenticated:
        chatroomname = request.GET.get("chatroomname")
        time_now = datetime.datetime.now()
        if chatroomname:
            link = '/home/chat/' + chatroomname
            return HttpResponseRedirect(link, {'room_name_json': mark_safe(json.dumps(room_name)),'user_name': mark_safe(json.dumps(request.user.username)), 'chat_room': chatroomname, 'time_now':time_now} ) 
        else:
            return render(request, 'blog/chat.html', {'room_name_json': mark_safe(json.dumps(room_name)),'user_name': mark_safe(json.dumps(request.user.username)), 'chat_room': chatroomname, 'time_now':time_now})
    else:
        return HttpResponseRedirect('/login')


def editblog(request, id):
    if request.user.is_authenticated:
        post_id = int(id)
        print(post_id)
        post = Post.objects.get(id = post_id)
        form = PostForm(request.POST or None, request.FILES or None,instance = post)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author_id = request.user.id
            instance.author_name = request.user.username
            instance.save()
            link = '/home/blog/' + str(post_id)
            return HttpResponseRedirect(link)
        context = {
            'post':post,
            'form':form,
        }
        return render(request, 'blog/post_form.html', context)
    else:
        return HttpResponseRedirect('/login')

def like(request, id):
    if request.user.is_authenticated:
        post_id = int(id)
        likes = Like.objects.get(like_author_id = request.user.id, like_post_id = post_id)
        likes.like_flag = True
        likes.save()
        notify, created = Notification.objects.get_or_create(user_id = likes.like_to_post_author_id, title="Like-Notification",message=" has liked ", by=likes.like_author)
        notify.save()
        post = Post.objects.get(id = post_id)
        post.likes += 1
        post.save()
        link = '/home/blog/' + str(int(id) )
        return redirect(link)
    else:
        return HttpResponseRedirect('/login/')

def shownotification(request,room_name):
    if request.user.is_authenticated:
        if request.user.id == int(room_name):
            notifications = Notification.objects.filter(user_id =request.user.id)
            context = {
                'room_name_json': mark_safe(json.dumps(room_name)),
                'user_name': mark_safe(json.dumps(request.user.username)),
                'notifications': notifications
            }
            return render(request, 'blog/notifications.html', context)
        else:
            return HttpResponseRedirect('/blog/profile')
    else:
        return HttpResponseRedirect('/blog/')