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
      if request.user.is_authenticated:
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
  {% if request.resolver_match.url_name == "signup" %}
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
      if request.user.is_authenticated:
          return redirect('reviews:index')

      if request.method == 'POST':
          form = AuthenticationForm(request, request.POST)
          if form.is_valid():
              auth_login(request, form.get_user())
              return redirect('reviews:index')
      else:
          form = AuthenticationForm()
      context = {
          'form' : form,
      }
      return render(request, 'accounts/form.html', context)
  ```

  ```
  <!-- accounts/templates/accounts/login.html -->
  {% extends 'base.html' %}
  {% load bootstrap4 %}

  {% block content %}
  <!-- messages framework 구현(생략) -->
  <h1 class="text-center">Login</h1>
  <hr>
  <form action="" method="POST">
      {% csrf_token %}
      {% bootstrap_form form %}
      {% bootstrap_button "Login" button_type="submit" button_class="btn-primary" %}
  </form>
  {% endblock %}
  ```

- 로그아웃

  ```
  # accounts/views.py
  @login_required # 로그인 안된 상태에서는 로그인 페이지로 이동
  def logout(request):
      auth_logout(request) # GET 방식
      messages.info(request, '로그아웃 되었습니다.')
      return redirect('community:index')
  ```

### community app

- `community/views.py` - `import`

  ```
  from django.shortcuts import render, redirect, get_object_or_404
  from django.contrib.auth import get_user_model # User Model 가져오기
  from django.contrib.auth.decorators import login_required
  from django.views.decorators.http import require_POST # POST 요청만 받음
  from .forms import ReviewForm, CommentForm
  from .models import Review, Comment
  from django.contrib import messages
  ```

- 신규 리뷰 생성

  ```
  # community/views.py
  @login_required
  def create(request):
      if request.method == 'POST': # 완성된 ReviewForm 제출
          form = ReviewForm(request.POST)
          if form.is_valid():
              review = form.save(commit=False) # DB save 지연
              review.user = request.user # 해당 review 객체에 작성자 정보 넣기
              review.save()
              messages.info(request, '글이 생성되었습니다.')
              return redirect('community:detail', review.pk)
      else: # 빈 ReviewForm 요청
          form = ReviewForm()
      context = {
              'form' : form,
          }
      return render(request, 'community/form.html', context)
  ```

  ```
  <!-- community/form.html(생성과 수정이 공유) -->
  {% extends 'base.html' %}
  {% load bootstrap4 %}

  {% block content %}
  <!-- review 생성 / 수정 분기 -->
  {% if request.resolver_match.url_name == "create" %} <!-- 생성 -->
  <h1 class="text-center">New Review</h1>
  {% elif request.resolver_match.url_name == "update" %} <!-- 수정 -->
  <h1 class="text-center">Update Review</h1>
  {% endif %}
  <hr>
  <form action="" method = "POST">
  {% csrf_token %}
  {% bootstrap_form form %}
  {% bootstrap_button "Save" button_type="submit" button_class="btn-primary" %}
  </form>
  {% endblock %}
  ```

- 전체 리뷰 목록 조회

  ```
  # community/views.py
  def index(request):
      if request.method == 'POST': # 사용자가 정렬 기능을 사용했을 경우
          if 'view_sort' in request.POST:
              reviews = Review.objects.order_by('-view_count') # 조회순
          elif 'created_at_sort' in request.POST:
              reviews = Review.objects.order_by('-created_at') # 생성순
          elif 'updated_at_sort' in request.POST:
              reviews = Review.objects.order_by('-updated_at') # 수정순
          elif 'rank_sort' in request.POST:
              reviews = Review.objects.order_by('-rank') # 평점순
      else: # 일반적인 상황(GET 요청)
          reviews = Review.objects.all()
      context = {
          'reviews': reviews,
      }
      return render(request, 'community/review_list.html', context)
  ```

  ```
  <!-- community/reveiw_list.html -->
  {% extends 'base.html' %}
  {% load bootstrap4 %}

  {% block content %}
  <!-- messages framework 구현(생략) -->
  <h1 class="text-center">Reviews</h1>
  <hr>
  <!-- 목록 정렬 기능 구현(각 button 별 name 넘겨주기) -->
  <div class="btn-group" role="group">
    <button id="btnGroupDrop1" type="button" class="btn border-info text-secondary dropdown-toggle mb-1" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
      정렬
    </button>
    <form action="{% url 'community:index' %}" method="POST">
    <div class="dropdown-menu p-0" aria-labelledby="btnGroupDrop1" style="width:10px">
       {% csrf_token %}
      <button class="dropdown-item text-secondary text-center" type="submit" name="view_sort">조회순</button>
      <button class="dropdown-item text-secondary text-center" type="submit" name="rank_sort">평점순</button>
      <button class="dropdown-item text-secondary text-center" type="submit" name="created_at_sort">생성순</button>
      <button class="dropdown-item text-secondary text-center" type="submit" name="updated_at_sort">수정순</button>
      </div>
  </form>
  </div>
  {% if reviews %} <!-- review가 있을 경우 -->
  <table class="table">
    <thead class="thead-dark">
      <tr>
        <th scope="col">#</th>
        <th scope="col">Title</th>
        <th scope="col">Movie</th>
        <th scope="col">Rank</th>
        <th scope="col">Updated_at</th>
        <th scope="col">Author</th>
        <th scope="col">Views</th>
      </tr>
    </thead>
    <tbody>
      {% for review in reviews %}
      <tr>
        <th scope="row">{{ review.pk }}</th>
        <td><a href="{% url 'community:detail' review.pk %}">{{ review.title }}</a></td>
        <td>{{ review.movie_title }}</td>
        <td>{{ review.rank }}</td>
        <td>{{ review.updated_at }}</td>
        <td><a href="{% url 'community:author_search' review.user %}">{{ review.user }}</a></td>
        <td>{{ review.view_count }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% else %} <!-- review가 없을 경우 -->
  <h3 class="text-center">작성된 리뷰가 없습니다.</h3>
  {% endif %}
  {% endblock %}
  ```

- 단일 리뷰 상세 조회 / 댓글 전체 조회 / 댓글 작성 form 표시

  ```
  # community/views.py
  def detail(request, review_pk):
      comment_form = CommentForm()
      review = get_object_or_404(Review, pk=review_pk) # 없을 경우 404 ERROR
      review.view_count += 1 # 조회수 count
      review.save() # 저장을 해줘야 조회수가 업데이트 된다.
      context = {
          'review' : review,
          'comment_form' : comment_form,
      }
      return render(request, 'community/review_detail.html', context)
  ```

  ```
  <!-- community/review_detail.html -->
  {% extends 'base.html' %}
  {% load bootstrap4 %}

  {% block content %}
  <!-- messages framework 구현(생략) -->
  <table class="table">
    <thead class="thead-dark">
      <tr>
        <th scope="col-6" style="font-size:2em; vertical-align:middle;">{{ review.title }}<br>{{ review.movie_title }}</th>
        <th scope="col-3" style="font-size:2em; vertical-align:middle;">평점 : {{ review.rank }}</th>
        <th scope="col-3" style="vertical-align:middle;">작성일 : {{ review.created_at }}<br><br>수정일 : {{ review.updated_at }}<br><br>조회수 : {{ review.view_count }}</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <th scope="row"></th>
        <td></td>
        <td class="text-right">
        	{% if request.user == review.user %} <!-- review 작성자인 경우에만 보이게 -->
  			<a href="{% url 'community:update' review.pk %}">수정</a>
  			<a href="{% url 'community:delete' review.pk %}">삭제</a>
  		{% endif %}
  		    <a href="{% url 'community:index' %}">뒤로가기</a>
        </td>
      </tr>
    </tbody>
  </table>
  {{ review.content }}
  <br>
  <br>
  <h4>댓글 | ({{ review.comment_set.all.count }})</h4>
  <hr>
  {% for comment in review.comment_set.all %}
  <div class="d-flex justify-content-between"><div class="d-inline col-8">{{ comment.content }} </div><div class="d-inline col-4">작성자 : {{ comment.user }}<br>작성일 : {{ comment.created_at }}
  {% if request.user == comment.user %} <!-- comment 작성자인 경우에만 보이게 -->
  <br><a href="{% url 'community:comment_delete' review.pk comment.pk %}">댓글 삭제</a>
  {% endif %}
  </div></div>
  <hr>
  {% empty %}
  <h4>댓글이 없습니다.</h4>
  <hr>
  {% endfor %}
  {% if user.is_authenticated %} <!-- 로그인 된 경우에만 comment 작성 form 보이게 -->
  <form action="{% url 'community:comment_create' review.pk %}" method="POST">
  	{% csrf_token %}
  	{% bootstrap_form comment_form %}
  	<button>댓글 작성</button>
  </form>
  {% endif %}
  {% endblock %}
  ```

- 기존 리뷰 수정

  ```
  # community/views.py
  @login_required
  def update(request, review_pk):
      review = get_object_or_404(Review, pk=review_pk)
      if request.user == review.user: # 해당 유저가 작성자와 일치할 경우
          if request.method == 'POST':
              form = ReviewForm(request.POST, instance=review) # instance!
              if form.is_valid():
                  review = form.save()
                  messages.info(request, '글이 수정되었습니다.')
                  return redirect('community:detail', review.pk)
          else:
              form = ReviewForm(instance=review)
          context = {
                  'form' : form,
              }
          return render(request, 'community/form.html', context)
      else:
          messages.info(request, '해당 글을 수정할 수 없습니다.')
          return redirect('community:detail', review.pk)
  ```

- 기존 리뷰 삭제

  ```
  # community/views.py
  @login_required
  def delete(request, review_pk):
      review = get_object_or_404(Review, pk=review_pk)
      if request.user == review.user: # 해당 유저가 작성자와 일치할 경우
          review.delete()
          messages.info(request, '글이 삭제되었습니다.')
          return redirect('community:index')
      else:
          messages.info(request, '해당 글을 삭제할 수 없습니다.')
          return redirect('community:detail', review.pk)
  ```

- 신규 댓글 생성

  ```
  # community/views.py
  @require_POST # POST 요청만 받을 수 있다
  @login_required # 로그인한 경우에만
  def comment_create(request, review_pk):
      review = get_object_or_404(Review, pk=review_pk)
      form = CommentForm(request.POST)
      if form.is_valid():
          comment = form.save(commit=False) # DB save 지연
          comment.user = request.user # 작성자 정보
          comment.review = review # review 정보
          comment.save()
          messages.info(request, '댓글이 생성되었습니다.')
      return redirect('community:detail', review.pk)
  ```

- 기존 댓글 삭제

  ```
  # community/views.py
  @login_required
  def comment_delete(request, review_pk, comment_pk):
      review = get_object_or_404(Review, pk=review_pk)
      comment = get_object_or_404(Comment, pk=comment_pk)
      if request.user == comment.user: # 해당 유저가 작성자와 일치할 경우
          comment.delete()
          messages.info(request, '댓글이 삭제되었습니다.')
          return redirect('community:detail', review.pk)
      else:
          messages.info(request, '해당 댓글을 삭제할 수 없습니다.')
          return redirect('community:detail', review.pk)
  ```

- 작성자 별 리뷰 목록

  ```
  def author_search(request, author_name):
      User = get_user_model()
      user = User.objects.get(username=author_name)
      if request.method == 'POST':
          if 'view_sort' in request.POST:
              reviews = Review.objects.filter(user=user).order_by('-view_count')
          elif 'created_at_sort' in request.POST:
              reviews = Review.objects.filter(user=user).order_by('-created_at')
          elif 'updated_at_sort' in request.POST:
              reviews = Review.objects.filter(user=user).order_by('-updated_at')
          elif 'rank_sort' in request.POST:
              reviews = Review.objects.filter(user=user).order_by('-rank')
      else:
          reviews = Review.objects.filter(user=user)
      context = {
          'reviews':reviews,
          'author_name':author_name,
      }
      return render(request, 'community/author_search.html', context)
  ```

  ```
  {% extends 'base.html' %}
  {% load bootstrap4 %}

  {% block content %}
  <!-- messages framework 구현(생략) -->
  <h1 class="text-center">{{ author_name }}의 글</h1>
  <hr>
  <div class="btn-group" role="group">
    <button id="btnGroupDrop1" type="button" class="btn border-info text-secondary dropdown-toggle mb-1" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
      정렬
    </button>
    <form action="{% url 'community:author_search' author_name %}" method="POST">
    <div class="dropdown-menu p-0" aria-labelledby="btnGroupDrop1" style="width:10px">
       {% csrf_token %}
      <button class="dropdown-item text-secondary text-center" type="submit" name="view_sort">조회순</button>
      <button class="dropdown-item text-secondary text-center" type="submit" name="rank_sort">평점순</button>
      <button class="dropdown-item text-secondary text-center" type="submit" name="created_at_sort">생성순</button>
      <button class="dropdown-item text-secondary text-center" type="submit" name="updated_at_sort">수정순</button>
      </div>
  </form>
  </div>
  {% if reviews %}
  <table class="table">
    <thead class="thead-dark">
      <tr>
        <th scope="col">#</th>
        <th scope="col">Title</th>
        <th scope="col">Movie</th>
        <th scope="col">Rank</th>
        <th scope="col">Updated_at</th>
        <th scope="col">Author</th>
        <th scope="col">Views</th>
      </tr>
    </thead>
    <tbody>
      {% for review in reviews %}
      <tr>
        <th scope="row">{{ review.pk }}</th>
        <td><a href="{% url 'community:detail' review.pk %}">{{ review.title }}</a></td>
        <td>{{ review.movie_title }}</td>
        <td>{{ review.rank }}</td>
        <td>{{ review.updated_at }}</td>
        <td>{{ review.user }}</td>
        <td>{{ review.view_count }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% else %}
  <h3 class="text-center">작성된 리뷰가 없습니다.</h3>
  {% endif %}
  {% endblock %}
  ```



# 새롭게알게된점

-

# 어려웠던점

-