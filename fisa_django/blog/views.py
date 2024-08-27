from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render
from .models import Post
from django.views.generic import ListView, DetailView, CreateView

class PostCreate(CreateView):
    model = Post
    fields = ["title", "content", "head_image"]

    # CreateView가 내장한 함수 - 오버라이딩 
    # tag는 참조관계이므로 Tag 테이블에 등록된 태그만 쓸 수 있는 상황
    # 임의로 방문자가 form에 Tag를 달아서 보내도록 form_valid()에 결과를 임시로 담아두고
    # 저장된 포스트로 돌아오도록 
    # def form_valid(self, form):
    #     current_user = self.request.user
    #     if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):
    #         form.instance.author = current_user
    #         response = super(PostCreate, self).form_valid(form)

    #         tags_str = self.request.POST.get('tags_str')
    #         if tags_str:
    #             tags_str = tags_str.strip() # 책, 독후감, 작가명

    #             tags_str = tags_str.replace(',', ';')
    #             tags_list = tags_str.split(';')

    #             for t in tags_list:
    #                 t = t.strip()
    #                 tag, is_tag_created = Tag.objects.get_or_create(tag_name=t)
    #                 if is_tag_created:
    #                     tag.slug = slugify(t, allow_unicode=True)
    #                     tag.save()
    #                 self.object.tag.add(tag)


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

def about_me(request): # 함수를 만들고, 그 함수를 도메인 주소 뒤에 달아서 호출하는 구조
    return render(
        request,
        'blog/about_me.html'
    )

class PostDetail(DetailView):
    model = Post 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = '임의로 작성한 새로운 변수'
        return context