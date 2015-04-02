import os
from apiclient.discovery import build
from apiclient.errors import HttpError

DEVELOPER_KEY = os.environ['YOUTUBE_API_KEY']
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def search_by_id(video_id):
  try:
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
      developerKey=DEVELOPER_KEY)

    search_response = youtube.videos().list(
      part='id,snippet,statistics',
      id=video_id
    ).execute()

    video_info = {}
    if search_response.get('items', []):
      search_result = search_response.get('items', [])[0]
      video_info['video_id'] = video_id
      video_info['title'] = search_result['snippet']['title']
      video_info['description'] = search_result['snippet']['description']
      video_info['channelTitle'] = search_result['snippet']['channelTitle']
      video_info['publishedAt'] = search_result['snippet']['publishedAt']
      video_info['viewCount'] = search_result['statistics']['viewCount']
      video_info['commentCount'] = search_result['statistics']['commentCount']
    return video_info

  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)


def append_to_query(query_list):
  try:
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
      developerKey=DEVELOPER_KEY)

    ids_string = ','.join([video['video_id'] for video in query_list])

    search_response = youtube.videos().list(
      part='id,snippet,statistics',
      id=ids_string
    ).execute()

    for idx,search_result in enumerate(search_response.get('items', [])):
      query_list[idx]['title'] = search_result['snippet']['title']
      query_list[idx]['channelTitle'] =  search_result['snippet']['channelTitle']
      query_list[idx]['thumbnail'] =  search_result['snippet']['thumbnails']['medium']['url']
      query_list[idx]['viewCount'] =  search_result['statistics']['viewCount']
      query_list[idx]['commentCount'] =  search_result['statistics']['commentCount']

  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
