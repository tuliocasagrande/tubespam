from django.shortcuts import render
from django.http import HttpResponse
from app.models import Video

def index(request):
  videos = Video.objects.all()
  output = ', '.join([v.id for v in videos])
  return HttpResponse(output)

def watch(request):
  video_id = request.GET.get('v')
  if not video_id:
    return HttpResponse("Woow. Where's the video_id?")

  return HttpResponse("You're watching the video %s." % video_id)
