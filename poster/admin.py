from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import Profile, Post

# Unregister Groups
admin.site.unregister(Group)


# Mix Profile info into User info
class ProfileInline(admin.StackedInline):
    model = Profile


# Extend User Model
class UserAdmin(admin.ModelAdmin):
    model = User
    # Show only username field on admin page
    fields = ['username']
    inlines = [ProfileInline]


# Unregister initial User
admin.site.unregister(User)

# Register User and Profile
admin.site.register(User, UserAdmin)
# admin.site.register(Profile)

# Register posts
admin.site.register(Post)
