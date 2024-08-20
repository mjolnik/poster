from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from poster.models import Profile, Post
from .forms import PostForm, SignUpForm, UpdateUserForm, ProfileUpdateForm, ChangePasswordForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django import forms


def home(request):
    if request.user.is_authenticated:
        form = PostForm(request.POST or None)
        if request.method == 'POST':
            if form.is_valid():
                post = form.save(commit=False)
                post.user = request.user
                post.save()
                messages.success(request, 'Your post has been posted!')
                return redirect('home')

        posts = Post.objects.all().order_by('-created_at')
        return render(request, 'home.html', {'posts': posts, 'form': form})
    else:
        posts = Post.objects.all().order_by('-created_at')
        return render(request, 'home.html', {'posts': posts})


def profile_list(request):
    if request.user.is_authenticated:
        profiles = Profile.objects.all()
        return render(request, 'profile_list.html', {'profiles': profiles})
    else:
        messages.success(request, 'You must be logged in to view this page.')
        return redirect('home')


def unfollow(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=pk)
        request.user.profile.follows.remove(profile)
        request.user.profile.save()
        messages.success(request, f'You have successfully unfollowed {profile.user.username}.')
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        messages.success(request, 'You must be logged in to view this page.')
        return redirect('login')


def follow(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=pk)
        request.user.profile.follows.add(profile)
        request.user.profile.save()
        messages.success(request, f'You have successfully followed {profile.user.username}.')
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        messages.success(request, 'You must be logged in to view this page.')
        return redirect('login')


def profile(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=pk)
        posts = Post.objects.filter(user_id=pk).order_by('-created_at')
        # POST Form logic
        if request.method == 'POST':
            # Get current user
            current_user_profile = request.user.profile
            action = request.POST['follow']
            # Decide to follow or unfollow
            if action == 'unfollow':
                current_user_profile.follows.remove(profile)
            elif action == 'follow':
                current_user_profile.follows.add(profile)
            # Save the profile
            current_user_profile.save()

        return render(request, 'profile.html', {'profile': profile, 'posts': posts})
    else:
        messages.success(request, 'You must be logged in to view this page.')
        return redirect('home')


def profile_followers(request, pk):
    if request.user.is_authenticated:
        if request.user.id == pk:
            profiles = Profile.objects.get(user_id=pk)
            return render(request, 'profile_followers.html', {'profiles': profiles})
    else:
        messages.success(request, 'You must be logged in to view this page.')
        return redirect('login')


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You are logged in!')
            return redirect('home')
        else:
            messages.success(request, 'Error. Please check credentials and try again.')
            return redirect('login')
    else:
        return render(request, 'login.html', {})


def logout_user(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


def register_user(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # first_name = form.cleaned_data['first_name']
            # last_name = form.cleaned_data['last_name']
            # email = form.cleaned_data['email']
            # Log in user
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, 'You have successfully registered!')
            return redirect('home')
    return render(request, 'register.html', {'form': form})


def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        profile_user = Profile.objects.get(user__id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, request.FILES or None, instance=current_user)
        profile_form = ProfileUpdateForm(request.POST or None, request.FILES or None, instance=profile_user)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            login(request, current_user)
            messages.success(request, 'Your Profile information updated successfully!')
        return render(request, 'update_user.html', {'user_form': user_form, 'profile_form': profile_form})
    else:
        messages.success(request, 'You must be logged in to view this page.')
        return redirect('login')


def post_like(request, pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, id=pk)
        if post.likes.filter(id=request.user.id):
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        messages.success(request, 'You must be logged in to view this page.')
        return redirect('login')


def post_page(request, pk):
    post = get_object_or_404(Post, id=pk)
    if post:
        return render(request, 'post_page.html', {'post': post})
    else:
        messages.success(request, 'That post does not exist.')
        return redirect('home')


def delete_post(request, pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, id=pk)
        if request.user.username == post.user.username:
            post.delete()
            messages.success(request, 'The post has been deleted.')
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            messages.success(request, 'You don\'t own this post!')
            return redirect('home')
    else:
        messages.success(request, 'Please log in to continue.')
        return redirect(request.META.get('HTTP_REFERER'))


def edit_post(request, pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, id=pk)
        if request.user.username == post.user.username:
            form = PostForm(request.POST or None, instance=post)
            if request.method == 'POST':
                if form.is_valid():
                    post = form.save(commit=False)
                    post.user = request.user
                    post.save()
                    messages.success(request, 'Your post has been updated!')
                    return redirect('home')
            else:
                return render(request, 'edit_post.html', {'form': form, 'post': post})
        else:
            messages.success(request, 'You don\'t own this post!')
            return redirect('home')
    else:
        messages.success(request, 'Please log in to continue.')
        return redirect(request.META.get('HTTP_REFERER'))


def search_post(request):
    if request.method == 'POST':
        search = request.POST['search']
        searched = Post.objects.filter(body__contains=search)
        return render(request, 'search_post.html', {'search': search, 'searched': searched})
    else:
        return render(request, 'search_post.html', {})


def search_user(request):
    if request.method == 'POST':
        search = request.POST['search']
        searched = User.objects.filter(username__contains=search)
        return render(request, 'search_user.html', {'search': search, 'searched': searched})
    else:
        return render(request, 'search_user.html', {})


def change_password(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = ChangePasswordForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully!')
        else:
            form = ChangePasswordForm(request.user)
        return render(request, 'change_password.html', {'form': form})
    else:
        messages.success(request, 'Please log in to continue.')
        return redirect('login')
