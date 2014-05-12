from django.contrib import admin
from django.contrib import admin
from app.models import Video, Comment

class CommentInline(admin.TabularInline):
  model = Comment

class VideoAdmin(admin.ModelAdmin):
  inlines = [CommentInline]

admin.site.register(Video, VideoAdmin)

