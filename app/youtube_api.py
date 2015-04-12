import os
from apiclient.discovery import build
from apiclient.errors import HttpError

DEVELOPER_KEY = os.environ['YOUTUBE_API_KEY']
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def get_video_by_id(video_id):
  try:
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
      developerKey=DEVELOPER_KEY)

    search_response = youtube.videos().list(
      part='id,player,snippet,statistics',
      id=video_id
    ).execute()

    video_details = {}
    if search_response.get('items', []):
      search_result = search_response.get('items', [])[0]
      video_details['video_id'] = video_id
      video_details['player'] = search_result['player']['embedHtml']
      video_details['title'] = search_result['snippet']['title']
      video_details['description'] = search_result['snippet']['description']
      video_details['channelTitle'] = search_result['snippet']['channelTitle']
      video_details['publishedAt'] = search_result['snippet']['publishedAt']
      video_details['viewCount'] = search_result['statistics']['viewCount']
      video_details['commentCount'] = search_result['statistics']['commentCount']
    return video_details

  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)


def get_videos_by_params(params):
  try:
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
      developerKey=DEVELOPER_KEY)

    search_response = youtube.videos().list(**params).execute()

    video_list_details = []
    for search_result in search_response.get('items', []):
      video_details = {}
      video_details['video_id'] = search_result['id']
      video_details['title'] = search_result['snippet']['title']
      video_details['channelTitle'] =  search_result['snippet']['channelTitle']
      video_details['thumbnail'] =  search_result['snippet']['thumbnails']['medium']['url']
      video_details['viewCount'] =  search_result['statistics']['viewCount']
      video_details['commentCount'] =  search_result['statistics']['commentCount']
      video_list_details.append(video_details)
    return video_list_details

  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
