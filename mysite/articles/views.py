from django.shortcuts import render, redirect, get_object_or_404
# DVDH
# django가 주는 views에서 쓸 decorators http를 위한
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Article, Comment
from .forms import ArticleForm, CommentForm
from IPython import embed
from django.contrib import messages
from django.core.paginator import Paginator

# Create your views here.
def index(request):
    articles = Article.objects.all()
    # 1. Paginator(전체리스트, 한 페이지당 갯수)
    paginator = Paginator(articles, 3)
    # 2. 몇 번째 페이지를 보여줄 것인지 GET으로 받기
    page = request.GET.get('page')# 'articles/?page=3'     url이 이런 식으로 됨
    # 3. 해당하는 페이지의 게시글만 가져오기
    articles = paginator.get_page(page)  # articles에 재할당
    context = {
        'articles': articles
    }
    return render(request, 'articles/index.html', context)

def detail(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)
    comment_form = CommentForm()
    # 1은 N을 보장할 수 없기 때문에 querySet(comment_set)형태로 조회 해야한다
    comments = article.comment_set.all()
    context = {
        'article': article,
        'comment_form' : comment_form,
        'comments' : comments,
    }
    return render(request, 'articles/detail.html', context)

@require_POST
def comment_create(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)
    comment_form = CommentForm(request.POST)
    if comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.article = article
        comment.user_id = request.user.pk
        comment.save()
        return redirect('articles:detail', article.pk)
    else:
        context = {
            'comment_form' : comment_form,
            'article' : article,
        }
    return redirect('articles:detail', context)

@require_POST
def comment_delete(request, article_pk, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    comment.delete()
    return redirect('articles:detail', article_pk)

@login_required
def create(request):
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.user_id = request.user.pk
            article.save()
            messages.success(request, '게시글 작성 완료!')
            return redirect('articles:detail', article.pk)
        else:
            messages.error(request, '잘못된 데이터 입력')
    else:
        form = ArticleForm()
    context = {
        'form': form
    }
    return render(request, 'articles/form.html', context)

@login_required
def update(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)
    if article.user == request.user:
        if request.method == "POST":
            form = ArticleForm(request.POST, request.FILES, instance=article)
            if form.is_valid():
                article = form.save()
                return redirect('articles:detail', article.pk)
        else:
            form = ArticleForm(instance=article)
    context = {
        'form': form
    }
    return render(request, 'articles/form.html', context)

@require_POST
def delete(request, article_pk):
    if request.user.is_authenticated:
        article = get_object_or_404(Article, pk=article_pk)
        if article.user == request.user:
            article.delete()
            return redirect('articles:index')
        else:
            return redirect('articles:detail', article.pk)
    return redirect('articles:detail', article.pk)

@login_required
def like(request, article_pk):
    # 특정 게시물에 대한 정보
    article = get_object_or_404(Article, pk=article_pk)
    # 좋아요를 누른 유저에 대한 정보
    user = request.user
    # 사용자가 게시글의 좋아요 목록에 있으면 true리턴
    if user in article.like_users.all():
        article.like_users.remove(user)
        liked = False
    else:
        article.like_users.add(user)
        liked = True
    context = {
        'liked' : liked,
        'count' : article.like_users.count()
    }
    return JsonResponse(context)

@login_required
def recommend(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)
    user = request.user
    if user in article.recommend_users.all():
        article.recommend_users.remove(user)
    else:
        article.recommend_users.add(user)
    return redirect('articles:index')