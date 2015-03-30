import os
from apiclient.discovery import build
from apiclient.errors import HttpError

DEVELOPER_KEY = os.environ['YOUTUBE_API_KEY']
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def search_by_ids(query_list):
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
