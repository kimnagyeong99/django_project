from django.urls import path
from . import views

# 앞으로 현재 프로젝트 내에서 blog/ 안에 있는 경로는 모두 blog_app
app_name = 'blog_app' # blog_app:blog -> localhost:8000/blog/post_list
# url 'blog_app:about_me -> localhost:8000/blog/about_me 로 이동 

urlpatterns = [
    # blog 앱 내부의 경로를 지정할 부분
    path('', views.index), # localhost:8000/blog 경로, 경로를 호출하면 실행할 함수의 위치 
    path('post_list', views.PostList.as_view(), name='post_list'), # name = 개발자가 이 주소를 부를 이름. 
    path('about_me', views.about_me, name='about_me'),
    path('<int:pk>', views.PostDetail.as_view()), # <자료형:필드명>
    path('create-post/', views.PostCreate.as_view())
]