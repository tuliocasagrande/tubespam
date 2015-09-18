from apiclient.errors import HttpError
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.db.models import Count
from json import dumps
from StringIO import StringIO
from unicodecsv import DictWriter

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
    channel_id = request.POST['channel_id']
    author = request.POST['author']
    date = datetime.strptime(request.POST['date'], DATE_FORMAT)
    content = request.POST['content']
    tag = int(request.POST['tag'])
    assert comment_id and video_id and channel_id and author and date and content
    assert tag == 0 or tag == 1
    tag = bool(tag)
  except Exception:
    return HttpResponse(status=400)

  video, created = Video.objects.get_or_create(id=video_id, defaults=
              {'channel_id':channel_id})
  comment, created = Comment.objects.get_or_create(id=comment_id, defaults=
              {'author':author, 'date':date, 'video':video, 'content':content})

  comment.tag = tag
  comment.save()
  video.channel_id = channel_id
  video.save()

  _get_and_fit_classifier(channel_id, [comment])
  _get_and_fit_classifier('default', [comment])

  return HttpResponse()

def predict(request):
  try:
    video_id = request.GET['v']
    channel_id = request.GET['channel_id']
    tag = int(request.GET['tag'])
    assert video_id
    assert tag == 0 or tag == 1
    tag = int(tag)
  except Exception:
    return HttpResponse(status=400)

  next_page_token = request.GET.get('next_page_token', None)
  if next_page_token == 'None':
    next_page_token = None

  classifier = _choose_classifier(channel_id)

  predicted = []
  try:
    while len(predicted) < 10 and next_page_token != False:
      unlabeled_comments, next_page_token = youtube_api.get_comment_threads(
        video_id, next_page_token)
      pred = classification.predict(classifier, unlabeled_comments)
      for idx, each in enumerate(unlabeled_comments):
        each['tag'] = pred[idx]
      predicted.extend([each for each in unlabeled_comments if each['tag'] == tag])
  except HttpError as e:
    return HttpResponse(e.content, status=e.resp.status)

  output = '{{"next_page_token":"{0}","comments":{{'.format(next_page_token)
  json_format = '"{0}":{{"author":{1},"date":"{2}","content":{3}}}'
  output += ','.join([json_format.format(
                        each['id'],
                        dumps(each['author']),
                        each['date'].strftime(DATE_FORMAT),
                        dumps(each['content']))
                      for each in predicted])
  output += '}}'
  return HttpResponse(output)

def _choose_classifier(channel_id):

  # Classifier for the channel
  classifier = _get_or_create_classifier(channel_id, {'video__channel_id': channel_id})
  if classifier: return classifier

  # Most general classifier
  try:
    classifier = Classifier.objects.get(id='default')
    if classification.load_model(classifier):
      return classifier
    raise Classifier.DoesNotExist()
  except Classifier.DoesNotExist:
    raise Classifier.DoesNotExist('Missing default classifier')

def _get_and_fit_classifier(classifier_id, comments):
  try:
    classifier = Classifier.objects.get(id=classifier_id)
    classification.partial_fit(classifier, comments, new_fit=False)
  except Classifier.DoesNotExist:
    # it's ok to ignore partial_fit inside save_comment(request)
    pass

def _get_or_create_classifier(classifier_id, lookup_fields):
  query_set = Classifier.objects.filter(id=classifier_id)
  if query_set and classification.load_model(query_set[0]):
    return query_set[0]

  min_required = 10
  comments = Comment.objects.filter(**lookup_fields)
  spam_count = comments.filter(tag=True).count()
  ham_count = len(comments) - spam_count

  if spam_count >= min_required and ham_count >= min_required:
    classifier = Classifier(id=classifier_id, model_filename=classifier_id+'_model')
    classifier.save()
    classification.partial_fit(classifier, comments, new_fit=True)
    return classifier

  return None

def export(request):
  # Restricting to a POST method just to appropriate django's csrf protection
  # Employing captcha would be an excellent improvement
  if request.method != 'POST':
    return HttpResponse(status=400)

  video_id = request.POST.get('v')
  channel_id = request.POST.get('channel_id')
  export_option = request.POST.get('export-option')

  if not video_id or not channel_id:
    return redirect('index')

  comments = Comment.objects.filter(video=video_id).order_by('date').values('id','author','date','content','tag')

  for c in comments:
    c['date'] = c['date'].isoformat()
    c['tag'] = 1 if c['tag'] else 0

  fieldnames = ['id','author','date','content','tag']
  csvfile = StringIO()
  writer = DictWriter(csvfile, fieldnames=fieldnames, encoding='utf-8')
  writer.writerows(comments)

  # Export options:
  # m  => manually classified only
  # mu => manually classified and unclassified
  if export_option == 'mu':
    export_ext_option = request.POST.get('export-ext-option')
    export_amount = int(request.POST.get('export-amount'))
    if export_amount > 1000: export_amount = 1000;
    if export_amount < 0: export_amount = 0;

    next_page_token = None
    unlabeled_comments = []; batch = []

    while len(unlabeled_comments) < export_amount and next_page_token != False:
      batch, next_page_token = youtube_api.get_comment_threads(
        video_id, next_page_token)
      unlabeled_comments.extend(batch)

    unlabeled_comments = unlabeled_comments[(export_amount * -1):]

    if unlabeled_comments:
      # Export extended options:
      # ec => apply the trained classifier
      # ek => keep comments unclassified
      if export_ext_option == 'ec':
        classifier = _choose_classifier(channel_id)
        tag = classification.predict(classifier, unlabeled_comments)
      elif export_ext_option == 'ek':
        tag = [-1] * len(unlabeled_comments)

      for idx, c in enumerate(unlabeled_comments):
        c['date'] = c['date'].isoformat()
        c['tag'] = tag[idx]

      writer.writerows(unlabeled_comments)

  csv = 'COMMENT_ID,AUTHOR,DATE,CONTENT,CLASS\n' + csvfile.getvalue()
  csvfile.close()

  response = HttpResponse(csv, content_type='text/plain')
  response['Content-Disposition'] = 'attachment; filename="{0}.csv"'.format(video_id)
  return response
