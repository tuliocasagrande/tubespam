from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
import json

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

  comments = Comment.objects.filter(video_id=video_id)
  spam_count = comments.filter(tag=True).count()
  ham_count = len(comments) - spam_count

  output = {'video_id': video_id, 'comments': comments,
            'spam_count': spam_count, 'ham_count': ham_count}
  return render(request, 'app/watch.html', output)

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


# With the API v2, this method just render the page
def classify(request):
  video_id = request.GET.get('v')
  if not video_id:
    return redirect('index')

  video = get_object_or_404(Video, pk=video_id)
  comments = Comment.objects.filter(video_id=video_id)
  spam_count = comments.filter(tag=True).count()
  ham_count = len(comments) - spam_count

  output = {'video_id': video_id, 'len_error': False,
            'spam_count': spam_count, 'ham_count': ham_count,
            'clf': classification.getClassifier(video_id)}

  if spam_count < 10 or ham_count < 10:
     output['len_error'] = True
     return render(request, 'app/classify.html', output)

  # Save to use with the API v3 (when available)
  # elif video.num_untrd_comments < 5 and output['clf'] != None:
  #   pred = classification.predict(video_id, test())

  # else:
  #   video.acc, video.stddev = classification.train(video_id, comments)
  #   video.num_untrd_comments = 0
  #   video.save()
  #   pred = classification.predict(video_id, test())
  #   output['clf'] = classification.getClassifier(video_id)


  output['acc'] = video.acc
  output['stddev'] = video.stddev
  output['comments'] = comments
  # output['prediction'] = zip(test(), pred)
  return render(request, 'app/classify.html', output)

def train(request):
  if request.is_ajax():
    if request.method == 'POST':
      output = '{'

      video_id = request.POST['v']
      video = Video.objects.get(id=video_id)
      print request.POST.getlist('comments[]')
      untagged_comments = prepareNewComments(request.POST.getlist('comments[]'))
      comments = Comment.objects.filter(video_id=video_id)
      spam_count = comments.filter(tag=True).count()
      ham_count = len(comments) - spam_count
      clf = classification.getClassifier(video_id)

      if video_id and untagged_comments and spam_count >= 10 and ham_count >= 10:
        if video.num_untrd_comments < 5 and clf != None:
          pred = classification.predict(video_id, untagged_comments)

        else:
          if spam_count + ham_count < 100:
            video.acc, video.stddev = classification.train(video_id, comments, untagged_comments)
          else:
            video.acc, video.stddev = classification.train(video_id, comments, [])

          video.num_untrd_comments = 0
          video.save()
          pred = classification.predict(video_id, untagged_comments)

        json = '"{0}":{{"content":"{1}","tag":"{2}"}}'
        output += ','.join([json.format(untagged_comments[i].id, untagged_comments[i].getEscapedContentJson(), pred[i])
                            for i in range(len(untagged_comments))])
      output += '}'

  return HttpResponse(output)


def export(request):
  video_id = request.POST.get('v')
  if not video_id:
    return redirect('index')

  exportOption = request.POST.get('export-option')
  comments = Comment.objects.filter(video_id=video_id)
  untagged_comments = prepareNewComments(request.POST.getlist('comments'))

  csv = 'COMMENT_ID,CONTENT,TAG\n'
  for each in comments:
    content = each.getEscapedContentCsv()
    tag = 1 if each.tag else 0
    csv += '{0},"{1}",{2}\n'.format(each.id, content, tag)

  if exportOption == 'tu':
    for each in untagged_comments:
      content = each.getEscapedContentCsv()
      csv += '{0},"{1}",-1\n'.format(each.id, content)

  elif exportOption == 'tc':
    # TODO, FIX IT!!!
    # Classify and put proper tag (0, 1)
    for each in untagged_comments:
      content = each.getEscapedContentCsv()
      csv += '{0},"{1}",-1\n'.format(each.id, content)

  response = HttpResponse(csv, content_type='text/plain')
  response['Content-Disposition'] = 'attachment; filename="{0}.csv"'.format(video_id)
  return response

def prepareNewComments(untagged_comments):
  newComments = []

  for each in untagged_comments:
    j = json.loads(each)
    c = Comment(id=j['comment_id'], content=j['content'])

    newComments.append(c)

  return newComments
