from django.db import models

# Create your models here.
# models모듈의 Model 클래스를 상속받는 자식클래스 생성
# 게시글에 필요한 필드는 무엇무엇일까요
class Post(models.Model): 
    title = models.CharField(max_length=50)
    content = models.TextField()
		
	# django model 이 최초 저장(insert) 시에만 현재날짜(date.today()) 를 적용
    # 아예 값 자체가 지금 시간으로 입력되어 들어감(우리가 변경할 필요 없음)
    created_at = models.DateTimeField(auto_now_add=True) 
    # django model 이 save 될 때마다 현재날짜(date.today()) 로 갱신됨
    updated_at = models.DateTimeField(auto_now=True) 

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d/', blank=True)

    # blog/models.py
    def __str__(self):
        return f'[[{self.pk}] {self.title}]'