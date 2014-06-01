from django.shortcuts import render, redirect, get_object_or_404
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

  if (not comment_id or not video_id or not content or not tag or
      (tag != 'spam' and tag != 'ham')):
    return HttpResponse('error!', status=400)

  video = retrieveVideo(video_id)
  try:
    comment = Comment.objects.get(id=comment_id)
  except Comment.DoesNotExist:
    comment = Comment(id=comment_id, video_id=video, content=content)

  if tag == 'spam':
    comment.tag = True
  else:
    comment.tag = False

  video.num_untrd_comments += 1
  video.save()
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
  video_id = request.GET.get('v')
  if not video_id:
    return redirect('index')

  video = get_object_or_404(Video, pk=video_id)
  comments = Comment.objects.filter(video_id=video_id)

  output = {'video_id': video_id, 'len_error': False,
            'clf': classification.getClassifier(video_id)}

  if len(comments) < 20:
     output['len_error'] = True
     return render(request, 'app/classify.html', output)

  elif video.num_untrd_comments < 5 and output['clf'] != None:
    pred = classification.predict(video_id, test())

  else:
    video.acc, video.stddev = classification.train(video_id, comments)
    video.num_untrd_comments = 0
    video.save()
    pred = classification.predict(video_id, test())
    output['clf'] = classification.getClassifier(video_id)


  output['acc'] = video.acc
  output['stddev'] = video.stddev
  output['comments'] = comments
  output['prediction'] = zip(test(), pred)
  return render(request, 'app/classify.html', output)

def test():
  contents = []
  contents.append('imagine na copa')
  contents.append('love cat')
  contents.append('love my cassino')
  contents.append('subscribe my dog')
  contents.append('subscribe my cassino')

  return contents
