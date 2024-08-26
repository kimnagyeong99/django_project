from django.shortcuts import render
from .models import Post
from django.views.generic import ListView

class PostList(ListView):   # post_list.html, post-list
    model = Post 
    # template_name = 'blog/index.html' 
    ordering = '-pk' 
    context_object_name = 'post_list'

# Create your views here.
def index(request): # 함수를 만들고, 그 함수를 도메인 주소 뒤에 달아서 호출하는 구조
    posts = Post.objects.all()
    return render(
        request,
        'blog/index.html',{
            'posts':posts, 'my_list': ["apple", "banana", "cherry"], 'my_text': "첫번째 줄 \n 두번째 줄", 'content' : '<img src="고양이.jpg"/>',
        } # 없는 index.html을 호출하고 있음
    )

# class about_me(ListView):   # post_list.html, post-list
#     model = Post 
#     template_name = 'blog/about_me.html' 
#     # ordering = '-pk' 
#     context_object_name = 'Single_pages/about_me'

def about_me(request): # 함수를 만들고, 그 함수를 도메인 주소 뒤에 달아서 호출하는 구조
    return render(
        request,
        'blog/about_me.html'
    )