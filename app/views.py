from django.shortcuts import render, redirect
from django.http import HttpResponse

from app.models import Video, Comment

def index(request):
  return render(request, 'app/index.html', {'videos': Video.objects.all()})

def watch(request):
  video_id = request.GET.get('v')
  if not video_id:
    return redirect('index')

  return render(request, 'app/watch.html', {'video_id': video_id})

def getTaggedComments(request):
  output = '{'

  video_id = request.GET.get('v')
  if video_id:
    comments = Comment.objects.filter(video_id=video_id)
    json = '"{0}":{{"content":"{1}","tag":"{2}"}}'
    output += ', '.join([json.format(c.id, c.getEscapedContent(), c.getTag()) for c in comments])

  output += '}'
  return HttpResponse(output)
