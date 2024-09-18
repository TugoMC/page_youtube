from django.shortcuts import render
from googleapiclient.discovery import build
import re
from django.conf import settings
from django.core.paginator import Paginator

API_KEY = settings.YOUTUBE_API_KEY

def extract_channel_id(channel_url):
    patterns = [
        r'channel\/([\w-]+)',
        r'user\/([\w-]+)',
        r'c\/([\w-]+)',
        r'@([\w-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, channel_url)
        if match:
            return match.group(1)
    return None

def get_channel_id(youtube, username_or_id):
    try:
        channel_response = youtube.channels().list(
            part='id',
            id=username_or_id
        ).execute()
        
        if channel_response.get('items'):
            return channel_response['items'][0]['id']
        
        channel_response = youtube.channels().list(
            part='id',
            forUsername=username_or_id
        ).execute()
        
        if channel_response.get('items'):
            return channel_response['items'][0]['id']
        
        search_response = youtube.search().list(
            part='id',
            q=username_or_id,
            type='channel'
        ).execute()
        
        if search_response.get('items'):
            return search_response['items'][0]['id']['channelId']
        
    except Exception as e:
        print(f"Erreur lors de la récupération de l'ID de chaîne: {e}")
    
    return None

def get_videos_from_channel(channel_url, page_token=None):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
   
    channel_identifier = extract_channel_id(channel_url)
    print(f"Identifiant extrait: {channel_identifier}")
   
    if not channel_identifier:
        print("Impossible d'extraire l'identifiant de la chaîne de l'URL")
        return [], None, None
   
    channel_id = get_channel_id(youtube, channel_identifier)
    print(f"ID de chaîne obtenu: {channel_id}")
    
    if not channel_id:
        print("Impossible de trouver l'ID de la chaîne")
        return [], None, None

    try:
        request = youtube.search().list(
            part='snippet',
            channelId=channel_id,
            maxResults=15,  # 15 vidéos par page
            order='date',
            type='video',
            pageToken=page_token
        )
        response = request.execute()
        videos = response.get('items', [])
        
        next_page_token = response.get('nextPageToken')
        prev_page_token = response.get('prevPageToken')
        
        video_ids = [video['id']['videoId'] for video in videos]
        stats_request = youtube.videos().list(
            part='statistics',
            id=','.join(video_ids)
        )
        stats_response = stats_request.execute()
        
        stats_dict = {item['id']: item['statistics'] for item in stats_response['items']}
        
        for video in videos:
            video['statistics'] = stats_dict.get(video['id']['videoId'], {})
        
        return videos, next_page_token, prev_page_token
    except Exception as e:
        print(f"Erreur lors de la récupération des vidéos: {e}")
        return [], None, None

def youtube_videos_view(request):
    channel_url = request.GET.get('channel_url')
    page_token = request.GET.get('page_token')
    page_number = request.GET.get('page', 1)  # Numéro de page, par défaut 1
    videos = []
    next_page_token = None
    prev_page_token = None

    if channel_url:
        videos, next_page_token, prev_page_token = get_videos_from_channel(channel_url, page_token)
        
        # Pagination
        paginator = Paginator(videos, 10)  # 10 vidéos par page
        page_obj = paginator.get_page(page_number)
        
        context = {
            'videos': page_obj.object_list,
            'channel_url': channel_url,
            'next_page_token': next_page_token,
            'prev_page_token': prev_page_token,
            'page_range': paginator.page_range,
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number
        }
    else:
        context = {
            'videos': [],
            'channel_url': channel_url,
            'next_page_token': None,
            'prev_page_token': None,
            'page_range': [],
            'total_pages': 0,
            'current_page': 1
        }

    return render(request, 'videos.html', context)

def video_detail_view(request, video_id):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    
    try:
        video_request = youtube.videos().list(
            part='snippet,statistics',
            id=video_id
        )
        video_response = video_request.execute()
        
        if video_response['items']:
            video = video_response['items'][0]
            return render(request, 'video_detail.html', {'video': video})
        else:
            return render(request, 'video_detail.html', {'error': 'Vidéo non trouvée'})
    except Exception as e:
        print(f"Erreur lors de la récupération des détails de la vidéo: {e}")
        return render(request, 'video_detail.html', {'error': 'Une erreur est survenue'})
    


    