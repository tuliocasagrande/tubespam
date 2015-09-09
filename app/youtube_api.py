import os
from apiclient.discovery import build
from apiclient.errors import HttpError
from datetime import datetime

DEVELOPER_KEY = os.environ['TS_YOUTUBE_API_KEY']
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
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
      video_details['title'] = search_result['snippet']['title']
      video_details['channel_id'] = search_result['snippet']['channelId']
      video_details['description'] = search_result['snippet']['description']
      video_details['channelTitle'] = search_result['snippet']['channelTitle']
      video_details['publishedAt'] = datetime.strptime(
        search_result['snippet']['publishedAt'], DATE_FORMAT_YT_API)
      video_details['viewCount'] = search_result['statistics']['viewCount']
      video_details['commentCount'] = search_result['statistics']['commentCount']
    return video_details

  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)


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
      video_details['title'] = search_result['snippet']['title']
      video_details['channelTitle'] =  search_result['snippet']['channelTitle']
      video_details['thumbnail'] =  search_result['snippet']['thumbnails']['medium']['url']
      video_details['viewCount'] =  search_result['statistics']['viewCount']
      video_details['commentCount'] =  search_result['statistics']['commentCount']
      video_details_list.append(video_details)
    return video_details_list

  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)

# Call the commentThreads.list method to retrieve comments of the given video_id.
def get_comment_threads(video_id, next_page_token=None):
  try:
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
      comment['comment_id'] = search_result['id']
      top_level_comment = search_result["snippet"]["topLevelComment"]
      comment['author'] = top_level_comment["snippet"]["authorDisplayName"]
      comment['content'] = top_level_comment["snippet"]["textDisplay"]
      comment['date'] = datetime.strptime(
        top_level_comment['snippet']['publishedAt'], DATE_FORMAT_YT_API)
      comment_list.append(comment)

    return comment_list, search_response['nextPageToken']

  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
