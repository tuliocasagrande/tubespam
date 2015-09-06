from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.db.models import Count
import json

from app.models import Classifier, Comment, Video
import app.classification as classification
import app.youtube_api as youtube_api

DATE_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"

def index(request):
  query_set = Comment.objects.values('video').annotate(num_comments=Count('id')).order_by('-num_comments')[:4]
  d = dict(part='id,snippet,statistics',
           id=','.join([query['video'] for query in query_set]))
  classified_videos = youtube_api.get_videos_by_params(d)

  for idx, each in enumerate(query_set):
    each.update(classified_videos[idx])

  d = dict(part='id,snippet,statistics',
           chart='mostPopular',
           maxResults=4)
  yt_most_popular = youtube_api.get_videos_by_params(d)

  return render(request, 'app/index.html',
    {'classified_videos': query_set, 'yt_most_popular': yt_most_popular})

def about(request):
  return render(request, 'app/about.html')

def video(request):
  video_id = request.GET.get('v')
  if not video_id:
    return redirect('index')

  video_details = youtube_api.get_video_by_id(video_id)
  if not video_details:
    raise Http404('This video does not exist.')

  comments = Comment.objects.filter(video=video_id).order_by('-date')
  spam_count = comments.filter(tag=True).count()
  ham_count = len(comments) - spam_count

  output = {'v': video_details, 'comments': comments,
            'spam_count': spam_count, 'ham_count': ham_count}
  return render(request, 'app'+request.path_info+'.html', output)

def save_comment(request):
  if request.method != 'POST':
    return HttpResponse(status=400)

  try:
    comment_id = request.POST['comment_id']
    video_id = request.POST['v']
    category_id = request.POST['category_id']
    author = request.POST['author']
    date = datetime.strptime(request.POST['date'], DATE_FORMAT)
    content = request.POST['content']
    tag = int(request.POST['tag'])
    assert comment_id and video_id and category_id and author and date and content
    assert tag == 0 or tag == 1
    tag = bool(tag)
  except Exception:
    return HttpResponse(status=400)

  video, created = Video.objects.get_or_create(id=video_id, defaults=
              {'category_id':category_id})
  comment, created = Comment.objects.get_or_create(id=comment_id, defaults=
              {'author':author, 'date':date, 'video':video, 'content':content})

  comment.tag = tag
  comment.save()
  video.category_id = category_id
  video.save()

  _get_and_fit_classifier(video_id, [comment])
  _get_and_fit_classifier(category_id, [comment])

  return HttpResponse()

def predict(request):
  try:
    video_id = request.GET['v']
    category_id = request.GET['category_id']
    tag = int(request.GET['tag'])
    assert video_id
    assert tag == 0 or tag == 1
    tag = int(tag)
  except Exception:
    return HttpResponse(status=400)

  next_page_token = request.GET.get('next_page_token', None)
  if next_page_token == 'None':
    next_page_token = None

  classifier = _choose_classifier(video_id, category_id)

  predicted = []
  while len(predicted) < 10:
    unlabeled_comments, next_page_token = youtube_api.get_comment_threads(
      video_id, next_page_token)
    pred = classification.predict(classifier, unlabeled_comments)
    for idx, each in enumerate(unlabeled_comments):
      each['tag'] = pred[idx]
    predicted.extend([each for each in unlabeled_comments if each['tag'] == tag])

  output = '{{"next_page_token":"{0}","comments":{{'.format(next_page_token)
  json_format = '"{0}":{{"author":{1},"date":"{2}","content":{3}}}'
  output += ','.join([json_format.format(
                        each['comment_id'],
                        json.dumps(each['author']),
                        each['date'].strftime(DATE_FORMAT),
                        json.dumps(each['content']))
                      for each in predicted])
  output += '}}'
  return HttpResponse(output)

def _choose_classifier(video_id, category_id):

  # Most specialized classifier, only for this video
  classifier = _get_or_create_classifier(video_id, {'video': video_id})
  if classifier: return classifier

  # Classifier for the entire category
  classifier = _get_or_create_classifier(category_id, {'video__category_id': category_id})
  if classifier: return classifier

  # Most general classifier
  query_set = Classifier.objects.get(id=0)
  if query_set and classification.load_model(query_set[0]): return query_set[0]

  return None

def _get_and_fit_classifier(classifier_id, comments):
  try:
    classifier = Classifier.objects.get(id=classifier_id)
    classification.partial_fit(classifier, comments, new_fit=False)
  except Exception:
    pass

def _get_or_create_classifier(classifier_id, lookup_fields):
  query_set = Classifier.objects.filter(id=classifier_id)
  if query_set and classification.load_model(query_set[0]):
    return query_set[0]

  min_required = 10
  comments = Comment.objects.filter(**lookup_fields).order_by('-date')
  spam_count = comments.filter(tag=True).count()
  ham_count = len(comments) - spam_count

  if spam_count >= min_required and ham_count >= min_required:
    classifier = Classifier(id=classifier_id, model_filename=classifier_id+'_model')
    classifier.save()
    classification.partial_fit(classifier, comments, new_fit=True)
    return classifier

  return None

def export(request):
  video_id = request.POST.get('v')
  if not video_id:
    return redirect('index')

  exportOption = request.POST.get('export-option')
  comments = Comment.objects.filter(video=video_id).order_by('date')

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
    unlabeled_comments = prepareNewComments(request.POST.getlist('comments'))
    unlabeled_comments.sort(key=lambda comment: comment.date)
    unlabeled_comments = unlabeled_comments[(export_amount * -1):]

    # Export extended options:
    # ec => apply the trained classifier
    # ek => keep comments unclassified
    if exportExtOption == 'ec':
      tag = classification.predict(video_id, unlabeled_comments)
    elif exportExtOption == 'ek':
      tag = [-1] * len(unlabeled_comments)

    csv += ''.join([csv_format.format(
                      each.id,
                      each.toCsv('author'),
                      each.date.isoformat(),
                      each.toCsv('content'),
                      tag[i])
                    for i, each in enumerate(unlabeled_comments)])

  response = HttpResponse(csv, content_type='text/plain')
  response['Content-Disposition'] = 'attachment; filename="{0}.csv"'.format(video_id)
  return response
