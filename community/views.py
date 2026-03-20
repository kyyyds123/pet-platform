from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Post, Comment, Like, LostPet


def post_list(request):
    posts = Post.objects.all().select_related('author')
    post_type = request.GET.get('type')
    if post_type:
        posts = posts.filter(post_type=post_type)
    return render(request, 'community/post_list.html', {
        'posts': posts,
        'current_type': post_type,
    })


def post_detail(request, pk):
    post = get_object_or_404(Post.objects.select_related('author'), pk=pk)
    comments = post.comments.all().select_related('author')
    user_liked = False
    if request.user.is_authenticated:
        user_liked = Like.objects.filter(post=post, user=request.user).exists()
    return render(request, 'community/post_detail.html', {
        'post': post,
        'comments': comments,
        'user_liked': user_liked,
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
        messages.success(request, '发布成功')
        return redirect('community:post_detail', pk=post.pk)
    return render(request, 'community/post_form.html')


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
