import os
from apiclient.discovery import build
from apiclient.errors import HttpError
from datetime import datetime

DEVELOPER_KEY = os.environ['TS_YOUTUBE_API_KEY']
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
DATE_FORMAT_YT_API = '%Y-%m-%dT%H:%M:%S.%fZ'

# Call the videos.list method to retrieve details for the given video_id.
def get_video_by_id(video_id):
  try:
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
      developerKey=DEVELOPER_KEY)

    search_response = youtube.videos().list(
      part='id,player,snippet,statistics',
      id=video_id
    ).execute()

    video_details = {}
    if 'items' in search_response and len(search_response['items']):
      search_result = search_response['items'][0]
      video_details['video_id'] = video_id
      video_details['player'] = search_result['player']['embedHtml']

      _snippet = search_result['snippet']
      video_details['title'] = _snippet['title']
      video_details['channel_id'] = _snippet['channelId']
      video_details['description'] = _snippet['description']
      video_details['channelTitle'] = _snippet['channelTitle']

      _publishedAt = datetime.strptime(_snippet['publishedAt'], DATE_FORMAT_YT_API)
      video_details['publishedAt'] = _publishedAt

      _statistics = search_result['statistics']
      video_details['viewCount'] = _statistics.get('viewCount', 0)
      video_details['commentCount'] = _statistics.get('commentCount', 0)
    return video_details

  except HttpError, e:
    print 'An HTTP error %d occurred:\n%s' % (e.resp.status, e.content)


# Call the videos.list method to retrieve details for each video.
def get_videos_by_params(params):
  try:
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
      developerKey=DEVELOPER_KEY)

    search_response = youtube.videos().list(**params).execute()

    video_details_list = []
    for search_result in search_response.get('items', []):
      video_details = {}
      video_details['video_id'] = search_result['id']

      _snippet = search_result['snippet']
      video_details['title'] = _snippet['title']
      video_details['channelTitle'] = _snippet['channelTitle']
      video_details['thumbnail'] = _snippet['thumbnails']['medium']['url']

      _statistics = search_result['statistics']
      video_details['viewCount'] = _statistics.get('viewCount', 0)
      video_details['commentCount'] = _statistics.get('commentCount', 0)

      video_details_list.append(video_details)
    return video_details_list

  except HttpError, e:
    print 'An HTTP error %d occurred:\n%s' % (e.resp.status, e.content)

# Call the commentThreads.list method to retrieve comments of the given video_id.
def get_comment_threads(video_id, next_page_token=None):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  search_response = youtube.commentThreads().list(
    part='id,snippet',
    videoId=video_id,
    maxResults=100,
    # searchTerms='visit .co http buy check channel site subscrib',
    pageToken=next_page_token
  ).execute()

  comment_list = []
  for search_result in search_response.get('items', []):
    comment = {}
    comment['id'] = search_result['id']

    _snippet = search_result['snippet']['topLevelComment']['snippet']
    comment['author'] = _snippet['authorDisplayName']
    comment['content'] = _snippet['textDisplay']

    _publishedAt = datetime.strptime(_snippet['publishedAt'], DATE_FORMAT_YT_API)
    comment['date'] = _publishedAt

    comment_list.append(comment)
  return comment_list, search_response.get('nextPageToken', False)
