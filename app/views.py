from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Count
import json

from app.models import Video, Comment
import app.classification as classification

DATE_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"

def index(request):
  #q = Video.objects.all()
  q = Comment.objects.values('video_id').annotate(num_comments=Count('id')).order_by('-num_comments')
  return render(request, 'app/index.html', {'videos': q})

def about(request):
  return render(request, 'app/about.html')

def watch(request):
  video_id = request.GET.get('v')
  if not video_id:
    return redirect('index')

  comments = Comment.objects.filter(video_id=video_id).order_by('-date')
  spam_count = comments.filter(tag=True).count()
  ham_count = len(comments) - spam_count

  output = {'video_id': video_id, 'comments': comments,
            'spam_count': spam_count, 'ham_count': ham_count}
  return render(request, 'app/watch.html', output)

def saveComment(request):
  try:
    comment_id = request.POST['comment_id']
    video_id = request.POST['video_id']
    author = request.POST['author']
    date = datetime.strptime(request.POST['date'], DATE_FORMAT)
    content = request.POST['content']
    tag = request.POST['tag']
  except Exception as e:
    print 'ERROR!', e
    return HttpResponse(('ERROR! ', e), status=400)

  if (not comment_id or not video_id or not content or not tag or
      (tag != 'spam' and tag != 'ham')):
    return HttpResponse('ERROR! Missing values!', status=400)

  video = retrieveVideo(video_id)
  try:
    comment = Comment.objects.get(id=comment_id)
  except Comment.DoesNotExist:
    comment = Comment(id=comment_id, author=author, date=date, video_id=video, content=content)

  if tag == 'spam':
    comment.tag = True
  else:
    comment.tag = False

  video.num_untrd_comments += 1
  video.save()
  comment.save()
  return HttpResponse(video.num_untrd_comments)


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
  comments = Comment.objects.filter(video_id=video_id).order_by('-date')
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
  output = '{'
  if request.is_ajax():
    if request.method == 'POST':

      video_id = request.POST['v']
      video = Video.objects.get(id=video_id)
      untagged_comments = prepareNewComments(request.POST.getlist('comments[]'))
      comments = Comment.objects.filter(video_id=video_id)
      spam_count = comments.filter(tag=True).count()
      ham_count = len(comments) - spam_count
      clf = classification.getClassifier(video_id)

      if video_id and untagged_comments and spam_count >= 10 and ham_count >= 10:
        if video.num_untrd_comments < 5 and clf != None:
          pred = classification.predict(video_id, untagged_comments)

        else:
          # FIX SEMI-SUPERVISED
          if spam_count + ham_count < 100:
            video.acc, video.stddev = classification.train(video_id, comments, untagged_comments)
          else:
            video.acc, video.stddev = classification.train(video_id, comments, [])

          video.num_untrd_comments = 0
          video.save()
          pred = classification.predict(video_id, untagged_comments)

        json_format = '"{0}":{{"author":"{1}","date":"{2}","content":"{3}","tag":"{4}"}}'
        output += ','.join([json_format.format(
                              each.id,
                              each.toJson('author'),
                              each.date.strftime(DATE_FORMAT),
                              each.toJson('content'),
                              pred[i])
                            for i, each in enumerate(untagged_comments)])

  output += '}'
  return HttpResponse(output)

def reloadClassifierInfo(request):
  output = ''

  video_id = request.GET['v']
  video = Video.objects.get(id=video_id)
  clf = classification.getClassifier(video_id)
  if video and clf:
    output = '<hr/><div class="pulse">' \
             '<div><strong>Classifier:</strong> {} (c: {})</div>' \
             '<div><strong>Accuracy:</strong> {:.2f}% &#177; {:.2f}%</div>' \
             '</div><hr/>'.format(clf.__class__.__name__, clf.get_params()['C'], video.acc, video.stddev)
  return HttpResponse(output)

def export(request):
  video_id = request.POST.get('v')
  if not video_id:
    return redirect('index')

  exportOption = request.POST.get('export-option')
  comments = Comment.objects.filter(video_id=video_id).order_by('date')

  csv_format = '{0},"{1}","{2}","{3}",{4}\n'
  csv = 'COMMENT_ID,AUTHOR,DATE,CONTENT,TAG\n'
  csv += ''.join([csv_format.format(
                    each.id,
                    each.toCsv('author'),
                    each.date.isoformat(),
                    each.toCsv('content'),
                    1 if each.tag else 0)
                  for each in comments])

  # Export options:
  # m  => manually classified only
  # mu => manually classified and unclassified
  if exportOption == 'mu':

    exportExtOption = request.POST.get('export-ext-option')
    export_amount = int(request.POST.get('export-amount'))
    untagged_comments = prepareNewComments(request.POST.getlist('comments'))
    untagged_comments.sort(key=lambda comment: comment.date)
    untagged_comments = untagged_comments[(export_amount * -1):]

    # Export extended options:
    # ec => apply the trained classifier
    # ek => keep comments unclassified
    if exportExtOption == 'ec':
      tag = classification.predict(video_id, untagged_comments)
    elif exportExtOption == 'ek':
      tag = [-1] * len(untagged_comments)

    csv += ''.join([csv_format.format(
                      each.id,
                      each.toCsv('author'),
                      each.date.isoformat(),
                      each.toCsv('content'),
                      tag[i])
                    for i, each in enumerate(untagged_comments)])

  response = HttpResponse(csv, content_type='text/plain')
  response['Content-Disposition'] = 'attachment; filename="{0}.csv"'.format(video_id)
  return response

def prepareNewComments(untagged_comments):
  newComments = []

  for each in untagged_comments:
    j = json.loads(each)
    c = Comment(id=j['comment_id'], author=j['author'],
                date=datetime.strptime(j['date'], DATE_FORMAT), content=j['content'])

    newComments.append(c)

  return newComments
