# SSAFY_django_pjt4 [서울 / 3기 / 박선환]

- [프로젝트 흐름 정리](#프로젝트흐름정리)
- [새롭게 알게 된 점](#새롭게알게된점)
- [어려웠던 점](#어려웠던점)

# 프로젝트흐름정리

## 1. Start Project

- ```bash
  $ django-admin startproject django_pjt4
  $ cd django_pjt4

  $ python manage.py startapp accounts
  $ python manage.py startapp reviews
  ```

- `.gitignore` 생성

  ```
  ...
  venv/
  ```

- 가상 환경 설정

  ```bash
  $ python -m venv venv
  $ source venv/bin/activate

  (venv) $ pip install django==2.1.15
  (venv) $ pip install django-bootstrap4
  (venv) $ pip install django-taggit
  ```

- `django_pjt4/settings.py` 설정

  ```python
  ALLOWED_HOSTS = ['*']

  INSTALLED_APPS = [
      'bootstrap4',
      'taggit',
      ...
      'accounts',
      'reviews',
  ]

  TEMPLAGES = [{
      ...
      'DIRS': [os.path.join(BASE_DIR, 'templates')] # base.html 사용하기 위해
      ...
  }]

  LANGUAGE_CODE = 'ko-kr'
  TIME_ZONE = 'Asia/Seoul'

  AUTH_USER_MODEL = 'accounts.USER' # Custom User 사용하기 위해

  TAGGIT_CASE_INSENSITIVE = True # 태그 대소문자 구별 안하기 위해
  ```

- `django_pjt4/urls.py` 설정

  ```python
  from django.contrib import admin
  from django.urls import path, include

  urlpatterns = [
      path('admin/', admin.site.urls),
      path('accounts/', include('accounts.urls')),
      path('reviews/', include('reviews.urls')),
  ]
  ```

## 2. Model

- `accounts/models.py`

  ```python
  from django.db import models
  from django.contrib.auth.models import AbstractUser
  from django.conf import settings

  # Custom User model 생성
  # settings.py => AUTH_USER_MODEL = 'accounts.USER' 설정

  class User(AbstractUser):
      followers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='followings')
  ```

- `reviews/models.py`

  ```python
  from django.db import models
  from django.conf import settings
  from taggit.managers import TaggableManager # 태그 필드 만들기 위해 import

  class Movie(models.Model):
      title = models.CharField(max_length=30)
      director = models.CharField(max_length=30)
      actors = models.TextField()
      description = models.TextField()
      poster_url = models.TextField()
      open_date = models.DateTimeField()
      audience_num = models.IntegerField(default=0)
      def __str__(self): # Movie 객체를 불러올 때 바로 title을 반환
          return self.title

  class Review(models.Model):
      title = models.CharField(max_length=30)
      content = models.TextField()
      rank = models.IntegerField(default=5)
      created_at = models.DateTimeField(auto_now_add=True)
      updated_at = models.DateTimeField(auto_now=True)
      movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
      user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
      view_count = models.IntegerField(default=0)
      like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_reivews')
      tags = TaggableManager() # tag field

  class Comment(models.Model):
      content = models.TextField()
      created_at = models.DateTimeField(auto_now_add=True)
      updated_at = models.DateTimeField(auto_now=True)
      review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments')
      user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
  ```

- `accounts/admin.py`

  ```python
  from django.contrib import admin
  from .models import User

  admin.site.register(User)
  ```

- `reviews/admin.py`

  ```python
  from django.contrib import admin
  from .models import Movie, Review, Comment

  admin.site.register(Movie)
  admin.site.register(Review)
  admin.site.register(Comment)
  ```

- ```bash
  $ python manage.py makemigrations
  $ python manage.py migrate
  $ python manage.py createsuperuser
  ```

## 3. Form

- `accounts/forms.py`

  ```python
  from django.contrib.auth.forms import UserCreationForm
  from django.contrib.auth import get_user_model

  class CustomUserCreationForm(UserCreationForm):
      class Meta(UserCreationForm.Meta):
          model = get_user_model()
  ```

- `reviews/forms.py`

  ```python
  from django import forms
  from .models import Review, Comment

  class ReviewForm(forms.ModelForm):
      class Meta:
          model = Review
          fields = ['title', 'content', 'movie', 'rank', 'tags']

  class CommentForm(forms.ModelForm):
      class Meta:
          model = Comment
          fields = ['content']
  ```

## 4. URL

- `accounts/urls.py`

  ```python
  from django.urls import path
  from . import views

  app_name = 'accounts'

  urlpatterns = [
      path('signup/', views.signup, name='signup'),
      path('login/', views.login, name='login'),
      path('logout/', views.logout, name='logout'),
      path('<username>/', views.profile, name='profile'),
      path('<username>/follow/', views.follow, name='follow'),
  ]
  ```

- `reviews/urls.py`

  ```python
  from django.urls import path
  from . import views

  app_name='reviews'

  urlpatterns = [
      path('', views.index , name='index'),
      path('create/', views.create, name='create'),
      path('movie/<int:movie_pk>/', views.movie_detail, name='movie_detail'),
      path('<int:review_pk>/', views.detail, name='detail'),
      path('<int:review_pk>/update/', views.update, name='update'),
      path('<int:review_pk>/delete/', views.delete, name='delete'),
      path('<int:review_pk>/comments/', views.comment_create, name='comment_create'),
      path('<int:review_pk>/comments/<int:comment_pk>/delete/', views.comment_delete, name='comment_delete'),
      path('<int:review_pk>/like/', views.like, name='like'),
      path('<str:tag_name>/', views.tag_search, name='tag_search'),
  ]
  ```

## 5. View & Template

### base.html

- bootstrap4 사용 위한 setting

  - `{% load bootstrap4 %}`
  - `{% bootstrap_css %}`
  - `{% bootstrap_javascript jquery='full' %}`

- block

  ```html
  <body>
      <!-- navbar 구현 -->
  	{% block content %}
  	{% endblock %}
      <!-- footer 구현 -->
  </body>
  ```

- 사용자 인증여부에 따라 분기한 UI 구성

  ```html
  {% if user.is_authenticated %}
  {% else %}
  {% endif %}
  ```

### accounts app

- `accounts/views.py` - `import`

  ```python
  from django.shortcuts import render, redirect, get_object_or_404
  from django.contrib.auth.forms import AuthenticationForm
  from django.contrib.auth.decorators import login_required
  from django.contrib.auth import login as auth_login, logout as auth_logout, get_user_model
  from .models import User
  from .forms import CustomUserCreationForm
  ```

- 회원가입

  ```python
  # accounts/views.py
  def signup(request):
      if request.user.is_authenticated: # 이미 로그인한 유저의 경우
          return redirect('reviews:index')

      if request.method == 'POST': # 완성된 가입 form 제출
          form = CustomUserCreationForm(request.POST)
          if form.is_valid(): # 유효성 검증
              user = form.save()
              auth_login(request, user) # 가입과 동시에 로그인
              return redirect('reviews:index')
      else:
          form = CustomUserCreationForm()
      context = {
          'form' : form,
      }
      return render(request, 'accounts/form.html', context)
  ```

  ```html
  <!-- accounts/templates/accounts/form.html signup/login 공유!-->
  {% extends 'base.html' %}
  {% load bootstrap4 %}

  {% block content %}
  {% if request.resolver_match.url_name == "signup" %} <!-- urlname 이용해 분기! -->
  <h1 class="text-center">Signup</h1>
  {% elif request.resolver_match.url_name == "login" %}
  <h1 class="text-center">Login</h1>
  {% endif %}
  <hr>
  <form action="" method = "POST">
  {% csrf_token %}
  {% bootstrap_form form %}
  {% bootstrap_button "저장" button_type="submit" button_class="btn-primary" %}
  </form>
  {% endblock %}
  ```

- 로그인

  ```python
  # accounts/views.py
  def login(request):
      if request.user.is_authenticated: # 이미 로그인한 유저의 경우
          return redirect('reviews:index')

      if request.method == 'POST': # 완성된 가입 form 제출
          form = AuthenticationForm(request, request.POST)
          if form.is_valid(): # 유효성 검증
              auth_login(request, form.get_user()) # 로그인
              return redirect('reviews:index')
      else:
          form = AuthenticationForm()
      context = {
          'form' : form,
      }
      return render(request, 'accounts/form.html', context)
  ```

- 로그아웃

  ```python
  # accounts/views.py
  @login_required # 로그인 상태의 경우에만
  def logout(request):
      auth_logout(request)
      return redirect('reviews:index')
  ```

- 유저 프로필

  ```python
  # accounts/views.py
  @login_required
  def profile(request, username):
      person = get_object_or_404(User, username=username)
      context = {
          'person' : person,
      }
      return render(request, 'accounts/profile.html', context)
  ```

  ```html
  <!-- accounts/templates/accounts/profile.html -->
  - 유저 팔로우/언팔로우 버튼 => 자기 프로필 페이지일 경우 안보이게(조건 분기)
  - 팔로워 / 팔로잉 수
  	- dropdown 활용 => 팔로워, 팔로잉 유저 목록 반환 => 클릭시 해당 유저 프로필 페이지로
  - 유저의 글 목록
  ```

- 팔로우/언팔로우

  ```python
  # accounts/views.py
  def follow(request, username):
      person = get_object_or_404(User, username=username)
      user = request.user
      if user != person: # 스스로는 팔로우/언팔로우 할 수 없음
          if user in person.followers.all():
              person.followers.remove(user) # 언팔로우
          else:
              person.followers.add(user) # 팔로우
      return redirect('accounts:profile', person.username)
  ```

### reviews app

- `reviews /views.py` - `import`

  ```python
  from django.shortcuts import render, redirect, get_object_or_404
  from django.contrib.auth import get_user_model
  from django.contrib.auth.decorators import login_required
  from django.views.decorators.http import require_POST

  from .models import Movie, Review, Comment
  from .forms import ReviewForm, CommentForm
  ```

- 전체 리뷰 목록 조회

  ```python
  # reviews/views.py
  def index(request):
      if request.user.is_authenticated: # 로그인한 유저라면
          User = get_user_model()
          users = User.objects.all()
          followings = request.user.followings.all() # 해당 유저가 팔로우 하는 유저들
          unfollowings = users.difference(followings) # 해당 유저가 팔로우 하지 않는 유저들
          if len(unfollowings) >= 5: # 팔로우 하지 않는 유저가 5명 이상일 경우에만 랜덤 소팅
              unfollowings = sorted(unfollowings, reverse=True, key=lambda x: x.followings.all().intersection(request.user.followings.all()).count())[:5]

          if 'following_reviews' in request.POST: # 친구의 글만 보고자 요청했을 때
              reviews = []
              for following in followings:
                  for review in following.reviews.all():
                      reviews.append(review)
          else: # 모든 글을 보고자 요청했을 때(default)
              reviews = Review.objects.order_by('-pk')
          context = {
              'reviews':reviews,
              'unfollowings': unfollowings,
          }
      else: # 로그인 하지 않은 경우
          reviews = Review.objects.order_by('-pk')
          context = {
              'reviews':reviews,
          }
      return render(request, 'reviews/index.html', context)
  ```

  ```html
  <!-- reviews/index.html -->
  - 팔로우 추천 기능(로그인 한 유저에만 노출)
  - Content Selector 기능(모든 글 or 팔로우 한 유저 글)
  - 카드 형태의 글 모음
  	- 포스터
  	- 영화명
  	- 글제목
  	- 작성자
  	- 작성시간
  	- 좋아요(수)
  ```

- 신규 리뷰 생성

  ```python
  # reviews/views.py
  @login_required
  def create(request):
      if request.method == 'POST':
          form = ReviewForm(request.POST)
          if form.is_valid():
              review = form.save(commit=False) # user 정보 넣어주기 위해
              review.user = request.user
              review.save()
              form.save_m2m()
              return redirect('reviews:detail', review.pk)
      else:
          form = ReviewForm()
      context = {
          'form':form,
      }
      return render(request, 'reviews/form.html', context)
  ```

  ```html
  <!-- reviews/templates/reviews/form.html create와 update가 공유!-->
  {% extends 'base.html' %}
  {% load bootstrap4 %}

  {% block content %}
  {% if request.resolver_match.url_name == "create" %}
  <h1 class="text-center">New Review</h1>
  {% elif request.resolver_match.url_name == "update" %}
  <h1 class="text-center">Update Review</h1>
  {% endif %}
  <hr>
  <form action="" method = "POST">
  {% csrf_token %}
  {% bootstrap_form form %}
  {% bootstrap_button "저장" button_type="submit" button_class="btn-primary" %}
  </form>
  {% endblock %}
  ```

- 단일 리뷰 상세 조회 / 댓글 전체 조회 / 댓글 작성 form 표시

  ```python
  # reviews/views.py
  def detail(request, review_pk):
      comment_form = CommentForm() # 댓글 작성 form
      review = get_object_or_404(Review, pk=review_pk)
      review.view_count += 1 # 조회수
      review.save()
      context = {
          'review':review,
          'comment_form':comment_form,
      }
      return render(request, 'reviews/review_detail.html', context)
  ```

  ```html
  <!-- reviews/templates/reviews/review_detail.html -->
  - 리뷰 상세정보
      - 글제목
      - 평점
      - 작성일
      - 수정일
      - 조회수
      - 영화명
      - 포스터
  - 글 작성자에게만 보이는 수정/삭제 버튼
  - 좋아요 기능
  - 댓글 작성 form(로그인 한 사람에게만 보임)
  - 댓글 리스트(글 작성자에게만 삭제 버튼 보임)
  ```

- 기존 리뷰 수정

  ```python
  # reviews/views.py
  @login_required
  def update(request, review_pk):
      review = get_object_or_404(Review, pk=review_pk)
      if request.user == review.user:
          if request.method == 'POST':
              form = ReviewForm(request.POST, instance=review)
              if form.is_valid():
                  form.save()
                  return redirect('reviews:detail', review.pk)
          else:
              form = ReviewForm(instance=review)
          context = {
              'form':form,
          }
          return render(request, 'reviews/form.html', context)
      else:
          return redirect('reviews:detail', review.pk)
  ```

- 기존 리뷰 삭제

  ```python
  # reviews/views.py
  @login_required
  def delete(request, review_pk):
      review = get_object_or_404(Review, pk=review_pk)
      if request.user == review.user:
          review.delete()
          return redirect('reviews:index')
      else:
          return redirect('reviews:detail', review.pk)
  ```

- 신규 댓글 생성

  ```python
  # reviews/views.py
  @require_POST
  @login_required
  def comment_create(request, review_pk):
      review = get_object_or_404(Review, pk=review_pk)
      form = CommentForm(request.POST)
      if form.is_valid():
          comment = form.save(commit=False)
          comment.user = request.user # 작성자
          comment.review = review # 리뷰글
          comment.save()
      return redirect('reviews:detail', review.pk)
  ```

- 기존 댓글 삭제

  ```python
  # reviews/views.py
  @login_required
  def comment_delete(request, review_pk, comment_pk):
      review = get_object_or_404(Review, pk=review_pk)
      comment = get_object_or_404(Comment, pk=comment_pk)
      if review.user == comment.user: # 글 작성자인 경우에만
          comment.delete()
      else:
          pass
      return redirect('reviews:detail', review.pk)
  ```

- 좋아요/좋아요 취소

  ```python
  # reviews/views.py
  @login_required
  def like(request, review_pk):
      review = get_object_or_404(Review, pk=review_pk)
      if request.user in review.like_users.all():
          review.like_users.remove(request.user) # 좋아요 취소
      else:
          review.like_users.add(request.user) # 좋아요
      # 요청이 온 url 주소로 다시 redirect
      return redirect(request.META.get('HTTP_REFERER'), review.pk)
  ```

- 태그 검색

  ```python
  # reviews/views.py
  def tag_search(request, tag_name):
      # 특정 태그가 걸려있는 게시물 찾기
      tag_reviews = Review.objects.filter(tags__name__in=[tag_name]).distinct()

      context = {
          'tag_reviews':tag_reviews,
          'tag_name':tag_name,
      }
      return render(request, 'reviews/tag_reviews.html', context)
  ```

  ```html
  <!-- reviews/templates/reviews/tag_reviews.html -->
  - tag_name을 title로 (h1)
  - 해당 태그가 걸려있는 게시물 반환
  ```

- 영화 디테일 정보 조회

  ```python
  # reviews/views.py
  def movie_detail(request, movie_pk):
      movie = get_object_or_404(Movie, pk=movie_pk)
      context = {
          'movie' : movie,
      }
      return render(request, 'reviews/movie_detail.html', context)
  ```

  ```html
  <!-- reviews/templates/reviews/movie_detail.html -->
  - 영화명
  - 감독
  - 배우
  - 개봉일
  - 관객수
  - 줄거리
  - 포스터
  - 해당 영화를 리뷰한 글 리스트
  ```



# 새롭게알게된점

### 가상 환경 설정

- `python -m venv venv`
- `source venv/bin/activate`
- `deactivate`
- `django` 비롯한 필요한 library 새롭게 설치해야한다.
- `pip freeze > requirements.txt`로 설치 library 정보 저장
  - 프로젝트 다른 곳에서 가져올 때 가상환경 상태에서 `pip install -r requirements.txt`로 필요한 라이브러리 설치

### 해쉬태그 검색 기능 구현

- [django-taggit](https://django-taggit.readthedocs.io/en/latest/index.html) 라이브러리를 활용

1. 환경설정

   ```bash
   $ pip install django-taggit
   ```

   ```python
   # settings.py
   ...
   INSTALLED_APPS = [
   	...
       'taggit',
   ]

   # 만약 태그의 대소문자를 구별하고 싶지 않을 경우 다음과 같이 설정해준다.
   TAGGIT_CASE_INSENSITIVE = True
   ```

2. model에 태그 필드 생성

   ```python
   # models.py
   from django.db import models
   from django.conf import settings
   from taggit.managers import TaggableManager # import

   class Review(models.Model):
   	...
       tags = TaggableManager() # tags field 생성
   ```

3. form 관련 설정 - `form.save_m2m()`

   ```python
   # views.py
   def create(request):
       if request.method == 'POST':
           form = ReviewForm(request.POST)
           if form.is_valid():
               review = form.save(commit=False)
               review.user = request.user
               review.save()
               form.save_m2m() # 이렇게 해줘야 태그 정보가 저장됨!
               return redirect('reviews:detail', review.pk)
       else:
           form = ReviewForm()
       context = {
           'form':form,
       }
       return render(request, 'reviews/form.html', context)
   ```

4. url 설정

   ```python
   # urls.py
   from django.urls import path
   from . import views

   app_name = 'reviews'

   urlpatterns = [
       ...
       ### hashtag 검색 요청 url 주소
       path('<str:tag_name>/', views.tag_search, name='tag_search'),
   ]
   ```

5. view 설정

   ```python
   # views.py
   def tag_search(request, tag_name):
       # 특정 태그가 걸려있는 게시물 찾기
       tag_reviews = Review.objects.filter(tags__name__in=[tag_name]).distinct()

       context = {
           'tag_reviews':tag_reviews,
           'tag_name':tag_name,
       }
       return render(request, 'reviews/tag_reviews.html', context)
   ```

6. template 설정

   ```html
   <!-- index.html -->
   ...
   <!-- 해당 글의 전체 태그를 하나씩 순회하며 출력 -->
   {% for tag in review.tags.all %}
   	<!-- 해당 태그를 클릭하면 태그 검색 page로 -->
   	<a href="{% url 'reviews:tag_search' tag.name %}" class="card-text d-inline">#{{ tag }} </a>
   {% endfor %}
   ...
   ```

   ```html
   {% extends 'base.html' %}

   {% block content %}
   <div class="container">
       <div class="row">
           <div class="col-12 d-flex flex-column align-items-center">
             <!-- 해당 태그 이름을 Title로 -->
             <h1 class="text-center">#{{ tag_name }}</h1>
           </div>
           <hr>
           <!-- 해당 태그를 지닌 글들을 순회하며 정보 출력 -->
           {% for review in tag_reviews %}
   			...
           {% endfor %}
       </div>
   </div>
   {% endblock %}
   ```



# 어려웠던점

- django 잠깐 놓아다고 그새 까먹는 나의 뇌 🤯
  - 반복적인 프로젝트로 극복해보쟈

- 아직 해결하지 못한 배포...