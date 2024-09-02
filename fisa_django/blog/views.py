from typing import Any
from django.db.models.query import QuerySet, Q # 장고 orm에서 쿼리문처럼 or and 조건을 좀 더 편하게 쓰게 만들어놓은 클래스
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Post, Tag, Comment
from .forms import CommentForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.utils.text import slugify


# 회원탈퇴
from django.views.decorators.http import require_POST # POST 방식으로만 접근해야하는 함수 앞에 적어줌
from django.contrib.auth import logout as auth_logout #logout 담당 함수
from django.contrib.auth.decorators import login_required # 인증을 확인해서 로그인 상태에서만 접근할 수 있게 허가하는 데코레이터
from django.contrib.auth import authenticate, login # authenticate : 인가, login : 인증 담당
from django.core.exceptions import PermissionDenied  #인가 - 권한이 없으면 예외...
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages  # 예외나 상황에 대한 메시지 처리 

# Mixin이라는 부가 기능들을 확인하기 위해 다중상속으로 주 기능을 확장하는 별도의 클래스
# 주기능을 가진 클래스보다 앞에 작성해줍니다. 
# Mixin은 상속이라기 보다는 포함, 확장이라는 개념으로 생각할 수 있다.
# 장고의 Mixin
class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    fields = ["title", "content", "head_image", "file_upload"]

    # CreateView가 내장한 함수 - 오버라이딩 
    # tag는 참조관계이므로 Tag 테이블에 등록된 태그만 쓸 수 있는 상황
    # 임의로 방문자가 form에 Tag를 달아서 보내도록 form_valid()에 결과를 임시로 담아두고
    # 저장된 포스트로 돌아오도록 
    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated and (current_user.is_active):
            form.instance.author = current_user
            response = super(PostCreate, self).form_valid(form)

            tags_str = self.request.POST.get('tags_str')
            if tags_str:
                tags_str = tags_str.strip() # 책; 독후감, 작가명

                tags_str = tags_str.replace(',', ';')
                tags_list = tags_str.split(';')

                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(tag_name=t)
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tag.add(tag)
            return response

        else:
                return redirect('/blog/')

class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ["title", "content", "head_image", "file_upload"]

    # 로그인한 상태에서 작성자(request.user)가 글의author와 일치하는지 확인
    # 방문자가 GET/POST 요청 등을 동작 수행 전에 가로채서 확인하는 기능 
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied #403 error
    # 이미 있는 글을 불러와서 원본에서 수정한 내용을 변경
    def get_context_data(self, **kwargs):
        context = super(PostUpdate, self).get_context_data()
        if self.object.tag.exists():
            tags_str_list = list()
            for t in self.object.tag.all():
                tags_str_list.append(t.tag_name)
            context['tags_str_default'] = '; '.join(tags_str_list)
        return context
    
    # 포스트에 태그를 추가하려면 이미 데이터베이스에 저장된 pk를 부여받아서 수정해야 함, 
    # 그래서 form_valid()를 통해 결과를 response 변수에 임시 담아두고
    # 서로 저장된 포스트를 self.object로 저장함.

    def form_valid(self, form):
        response = super(PostUpdate, self).form_valid(form)
        self.object.tag.clear()

        tags_str = self.request.POST.get('tags_str')
        if tags_str:
            tags_str = tags_str.strip()
            tags_str = tags_str.replace(',', ';')
            tags_list = tags_str.split(';')

            for t in tags_list:
                t = t.strip()
                tag, is_tag_created = Tag.objects.get_or_create(tag_name=t)
                if is_tag_created:
                    tag.slug = slugify(t, allow_unicode=True)
                    tag.save()
                self.object.tag.add(tag)

        return response
        
class PostDelete(LoginRequiredMixin, DeleteView):
    model = Post 
    success_url = '/blog/post_list'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.author == request.user:
            success_url = self.get_success_url()
            self.object.delete()
            return redirect(success_url)
        else:
            raise PermissionDenied 

class PostList(ListView):   # post_list.html, post-list
    model = Post 
    # template_name = 'blog/index.html' 
    ordering = '-pk' 
    context_object_name = 'post_list'

class PostSearch(PostList):
    paginate_by = None
    def get_queryset(self):
        q = self.kwargs['q'] # q = 'new'
        # title에 있거나, content에 있거나, tag에 있거나 // and & // or |
        post_list = Post.objects.filter(Q(title__contains=q) | Q(content__contains=q) | Q(tag__tag_name__contains=q))\
            .select_related('author')    
        return post_list

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
        context["comment_form"] = CommentForm

        return context
    
@login_required
def user_delete(request):
    # 로그인 상태 확인
    if request.user.is_authenticated:
        # user_delete()호출
        request.user.delete()
        
        # 로그아웃
        auth_logout(request) #세션 지우기
        # 원래 페이지로 로그인 안된 상태로 원상복귀
        return redirect('blog_app:about_me')
    
#태그(slug)가 일치하는 글을 함께 출력
def tag_posts(request, slug): # URL로 전달받은 slug변수를 아규먼트로 사용
    # 태그가 없는 경우
    if slug =="no-tag":
        posts = Post.objects.filter(tag=None)
    # 태그가 있는 경우
    else:
        tag = Tag.objects.get(slug=slug) # tag를 포함한 object를 추려냄
        # posts = Post.objects.filter(tag=tag)
        # 쿼리 최적화를 위해서 foreignKey나 일대일 관계로 연결된 테이블 데이터를 미리 가져오는 메서드
        # 한번에 데이터를 저장해놓고 필요할 때 가져다 쓸 수 있습니다. 
        posts = Post.objects.filter(tag=tag).select_related('author')

    return render(request, 'blog/post_list.html', {'post_list' : posts}) # 템플릿 재사용


def create_comment(request, pk):
    # GET/ POST 서로 다른 결과 return
    # 로그인 상태 확인
    if request.user.is_authenticated:
        post = Post.objects.get(pk=pk)
        # POST 리턴 -> comment 테이블에 값 업데이트
        if request.method == 'POST':
            comment_form = CommentForm(request.POST) # 작성한 content
            if comment_form.is_valid():
                comment = comment_form.save(commit=False) # 객체는 만들었으나, 아직 DB에 반영하지 않은 상태
                comment.post = post # 임시저장상태로 필드로 입력받지 않은 값들을 추가 
                comment.author = request.user # 임시저장상태로 필드로 입력받지 않은 값들을 추가
                comment.save()
                return redirect(comment.get_absolute_url())
        else:
            return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied


class CommentUpdate(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm

    # 로그인한 상태에서 작성자(request.user)가 글의author와 일치하는지 확인
    # 방문자가 GET/POST 요청 등을 동작 수행 전에 가로채서 확인하는 기능 
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(CommentUpdate, self).dispatch(request, *args, **kwargs) # dispatch(self) 유무의 차이가 뭐지?
        else:
            raise PermissionDenied #403 error 

def delete_comment(request, pk):
    comment = Comment.objects.get(pk = pk) # comment객체 가져옴
    post = comment.post

    # 로그인 된 상태이고, comment.author이면 

    if request.user.is_authenticated and request.user == comment.author:
        comment.delete()
        return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied
    
