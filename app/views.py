from django.shortcuts import render, redirect
from django.http import HttpResponse

from app.models import Video, Comment
import app.classification as classification

def index(request):
  return render(request, 'app/index.html', {'videos': Video.objects.all()})

def about(request):
  return render(request, 'app/about.html')

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

def saveComment(request):
  try:
    comment_id = request.POST['comment_id']
    video_id = request.POST['video_id']
    content = request.POST['content']
    tag = request.POST['tag']
  except:
    return HttpResponse('error!', status=400)

  if not comment_id or not video_id or not content or not tag:
    return HttpResponse('error!', status=400)

  try:
    comment = Comment.objects.get(id=comment_id)
  except Comment.DoesNotExist:
    comment = Comment(id=comment_id, video_id=retrieveVideo(video_id), content=content)

  if tag == 'spam':
    comment.tag = True
  else:
    comment.tag = False

  comment.save()
  return HttpResponse('success!')

def retrieveVideo(video_id):
  try:
    video = Video.objects.get(id=video_id)
  except Video.DoesNotExist:
    video = Video(id=video_id)
    video.save()

  return video

def classify(request):
  output = ''

  video_id = request.GET.get('v')
  if video_id:
    comments = Comment.objects.filter(video_id=video_id)
    if len(comments) < 20:
      output = 'At least 20 tagged comments are needed!'
    else:
      output = classification.classify(comments)

  return render(request, 'app/classify.html', {'content': output})
