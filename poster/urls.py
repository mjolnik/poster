from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('profile_list/', views.profile_list, name='profile_list'),
    path('profile/<int:pk>', views.profile, name='profile'),
    path('profile_followers/<int:pk>', views.profile_followers, name='profile_followers'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('update_user/', views.update_user, name='update_user'),
    path('post_like/<int:pk>', views.post_like, name='post_like'),
    path('post_page/<int:pk>', views.post_page, name='post_page'),
    path('unfollow/<int:pk>', views.unfollow, name='unfollow'),
    path('follow/<int:pk>', views.follow, name='follow'),
    path('delete_post/<int:pk>', views.delete_post, name='delete_post'),
    path('edit_post/<int:pk>', views.edit_post, name='edit_post'),
    path('search_post/', views.search_post, name='search_post'),
    path('search_user/', views.search_user, name='search_user'),
    path('change_password/', views.change_password, name='change_password'),
]
