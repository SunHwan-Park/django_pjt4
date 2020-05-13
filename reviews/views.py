from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import Movie, Review, Comment
from .forms import ReviewForm, CommentForm
# Create your views here.



def index(request):
    if request.user.is_authenticated:
        User = get_user_model()
        users = User.objects.all()
        followings = request.user.followings.all()
        unfollowings = users.difference(followings)
        if len(unfollowings) >= 5:
            unfollowings = sorted(unfollowings, reverse=True, key=lambda x: x.followings.all().intersection(request.user.followings.all()).count())[:5]

        if 'following_reviews' in request.POST:
            reviews = []
            for following in followings:
                for review in following.reviews.all():
                    reviews.append(review)
        else:
            reviews = Review.objects.order_by('-pk')
        context = {
            'reviews':reviews,
            'unfollowings': unfollowings,
        }
    else:
        reviews = Review.objects.order_by('-pk')
        context = {
            'reviews':reviews,
        }
    return render(request, 'reviews/index.html', context)

@login_required
def create(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
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

def detail(request, review_pk):
    comment_form = CommentForm()
    review = get_object_or_404(Review, pk=review_pk)
    review.view_count += 1
    review.save()
    context = {
        'review':review,
        'comment_form':comment_form,
    }
    return render(request, 'reviews/review_detail.html', context)

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

@login_required
def delete(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    if request.user == review.user:
        review.delete()
        return redirect('reviews:index')
    else:
        return redirect('reviews:detail', review.pk)

@require_POST
@login_required
def comment_create(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.review = review
        comment.save()
    return redirect('reviews:detail', review.pk)

@login_required
def comment_delete(request, review_pk, comment_pk):
    review = get_object_or_404(Review, pk=review_pk)
    comment = get_object_or_404(Comment, pk=comment_pk)
    if review.user == comment.user:
        comment.delete()
    else:
        pass
    return redirect('reviews:detail', review.pk)

@login_required
def like(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    if request.user in review.like_users.all():
        review.like_users.remove(request.user)
    else:
        review.like_users.add(request.user)
    return redirect(request.META.get('HTTP_REFERER'), review.pk)

def tag_search(request, tag_name):
    tag_reviews = Review.objects.filter(tags__name__in=[tag_name]).distinct()

    context = {
        'tag_reviews':tag_reviews,
        'tag_name':tag_name,
    }
    return render(request, 'reviews/tag_reviews.html', context)

def movie_detail(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    context = {
        'movie' : movie,
    }
    return render(request, 'reviews/movie_detail.html', context)