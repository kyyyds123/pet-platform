from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Post, Comment, Like, LostPet, SavedPost, SavedLost


def post_list(request):
    posts = Post.objects.filter(is_approved=True).select_related('author')
    post_type = request.GET.get('type')
    sort = request.GET.get('sort', 'time')
    keyword = request.GET.get('keyword', '')

    if post_type:
        posts = posts.filter(post_type=post_type)
    if keyword:
        posts = posts.filter(
            Q(title__icontains=keyword) | Q(content__icontains=keyword)
        )
    if sort == 'hot':
        posts = posts.order_by('-is_pinned', '-likes_count', '-comments_count')
    else:
        posts = posts.order_by('-is_pinned', '-created_at')

    return render(request, 'community/post_list.html', {
        'posts': posts,
        'current_type': post_type,
        'current_sort': sort,
        'keyword': keyword,
    })


def post_detail(request, pk):
    post = get_object_or_404(Post.objects.select_related('author'), pk=pk)
    # 未审核帖子只有管理员和作者本人可见
    if not post.is_approved and not (
        request.user.is_authenticated and (
            request.user.is_admin_role or post.author == request.user
        )
    ):
        from django.http import Http404
        raise Http404
    comments = post.comments.all().select_related('author')
    user_liked = False
    user_saved = False
    if request.user.is_authenticated:
        user_liked = Like.objects.filter(post=post, user=request.user).exists()
        user_saved = SavedPost.objects.filter(post=post, user=request.user).exists()
    return render(request, 'community/post_detail.html', {
        'post': post,
        'comments': comments,
        'user_liked': user_liked,
        'user_saved': user_saved,
    })


@login_required
def post_create(request):
    if request.method == 'POST':
        post = Post.objects.create(
            author=request.user,
            post_type=request.POST.get('post_type', 'note'),
            title=request.POST['title'],
            content=request.POST['content'],
            image=request.FILES.get('image'),
        )
        messages.success(request, '帖子已提交，审核通过后将公开展示')
        return redirect('community:post_detail', pk=post.pk)
    return render(request, 'community/post_form.html')


@login_required
def my_posts(request):
    """我的帖子（含审核状态）"""
    posts = Post.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'community/my_posts.html', {'posts': posts})


@login_required
def post_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
        post.likes_count = max(0, post.likes_count - 1)
    else:
        post.likes_count += 1
    post.save()
    return JsonResponse({'likes': post.likes_count, 'liked': created})


@login_required
def comment_create(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        Comment.objects.create(
            post=post,
            author=request.user,
            content=request.POST['content'],
        )
        post.comments_count += 1
        post.save()
        messages.success(request, '评论成功')
    return redirect('community:post_detail', pk=pk)


def lost_pet_list(request):
    lost_pets = LostPet.objects.all().select_related('author')
    status = request.GET.get('status')
    if status:
        lost_pets = lost_pets.filter(status=status)
    return render(request, 'community/lost_list.html', {
        'lost_pets': lost_pets,
        'current_status': status,
    })


@login_required
def lost_pet_create(request):
    if request.method == 'POST':
        lost_pet = LostPet.objects.create(
            author=request.user,
            pet_name=request.POST['pet_name'],
            pet_breed=request.POST.get('pet_breed', ''),
            pet_description=request.POST['pet_description'],
            location=request.POST['location'],
            contact=request.POST['contact'],
            image=request.FILES.get('image'),
        )
        messages.success(request, '发布成功')
        return redirect('community:lost_list')
    return render(request, 'community/lost_form.html')


@login_required
def lost_pet_update(request, pk):
    lost_pet = get_object_or_404(LostPet, pk=pk, author=request.user)
    if request.method == 'POST':
        lost_pet.status = request.POST.get('status', 'found')
        lost_pet.save()
        messages.success(request, '状态已更新')
    return redirect('community:lost_list')


@login_required
def post_save(request, pk):
    """收藏帖子"""
    post = get_object_or_404(Post, pk=pk)
    saved, created = SavedPost.objects.get_or_create(post=post, user=request.user)
    if not created:
        saved.delete()
    return JsonResponse({'saved': created})


@login_required
def lost_save(request, pk):
    """收藏走失信息"""
    lost_pet = get_object_or_404(LostPet, pk=pk)
    saved, created = SavedLost.objects.get_or_create(lost_pet=lost_pet, user=request.user)
    if not created:
        saved.delete()
    return JsonResponse({'saved': created})


@login_required
def my_saved_posts(request):
    """我的收藏帖子"""
    saved = SavedPost.objects.filter(user=request.user).select_related('post__author')
    return render(request, 'community/saved_posts.html', {'saved_posts': saved})


@login_required
def my_saved_lost(request):
    """我的收藏走失信息"""
    saved = SavedLost.objects.filter(user=request.user).select_related('lost_pet__author')
    return render(request, 'community/saved_lost.html', {'saved_lost': saved})


# ========== 管理员审核 ==========

@login_required
def admin_post_list(request):
    """管理员：帖子审核列表"""
    if not request.user.is_admin_role:
        messages.error(request, '仅管理员可访问')
        return redirect('index')

    posts = Post.objects.all().select_related('author')
    post_type = request.GET.get('type')
    if post_type:
        posts = posts.filter(post_type=post_type)
    return render(request, 'community/admin_post_list.html', {
        'posts': posts,
        'current_type': post_type,
    })


@login_required
def admin_post_pin(request, pk):
    """管理员：置顶/取消置顶帖子"""
    if not request.user.is_admin_role:
        messages.error(request, '仅管理员可操作')
        return redirect('index')

    post = get_object_or_404(Post, pk=pk)
    post.is_pinned = not post.is_pinned
    post.save()
    status = '置顶' if post.is_pinned else '取消置顶'
    messages.success(request, f'帖子已{status}')
    return redirect('community:admin_posts')


@login_required
def admin_post_approve(request, pk):
    """管理员：审核通过帖子"""
    if not request.user.is_admin_role:
        messages.error(request, '仅管理员可操作')
        return redirect('index')

    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        post.is_approved = True
        post.save()
        messages.success(request, f'帖子「{post.title}」已审核通过')
    return redirect('community:admin_posts')


@login_required
def admin_post_reject(request, pk):
    """管理员：拒绝帖子"""
    if not request.user.is_admin_role:
        messages.error(request, '仅管理员可操作')
        return redirect('index')

    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        post.is_approved = False
        post.save()
        messages.success(request, f'帖子「{post.title}」已拒绝')
    return redirect('community:admin_posts')


@login_required
def admin_post_delete(request, pk):
    """管理员：删除帖子"""
    if not request.user.is_admin_role:
        messages.error(request, '仅管理员可操作')
        return redirect('index')

    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        title = post.title
        post.delete()
        messages.success(request, f'帖子「{title}」已删除')
    return redirect('community:admin_posts')


@login_required
def admin_comment_list(request):
    """管理员：评论审核列表"""
    if not request.user.is_admin_role:
        messages.error(request, '仅管理员可访问')
        return redirect('index')

    comments = Comment.objects.all().select_related('author', 'post')
    return render(request, 'community/admin_comment_list.html', {'comments': comments})


@login_required
def admin_comment_delete(request, pk):
    """管理员：删除评论"""
    if not request.user.is_admin_role:
        messages.error(request, '仅管理员可操作')
        return redirect('index')

    comment = get_object_or_404(Comment, pk=pk)
    if request.method == 'POST':
        post = comment.post
        post.comments_count = max(0, post.comments_count - 1)
        post.save()
        comment.delete()
        messages.success(request, '评论已删除')
    return redirect('community:admin_comments')


@login_required
def admin_lost_list(request):
    """管理员：走失信息管理"""
    if not request.user.is_admin_role:
        messages.error(request, '仅管理员可访问')
        return redirect('index')

    lost_pets = LostPet.objects.all().select_related('author')
    return render(request, 'community/admin_lost_list.html', {'lost_pets': lost_pets})


@login_required
def admin_lost_delete(request, pk):
    """管理员：删除走失信息"""
    if not request.user.is_admin_role:
        messages.error(request, '仅管理员可操作')
        return redirect('index')

    lost_pet = get_object_or_404(LostPet, pk=pk)
    if request.method == 'POST':
        lost_pet.delete()
        messages.success(request, '信息已删除')
    return redirect('community:admin_lost')
