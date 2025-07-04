import requests
from youtubesearchpython import VideosSearch
import yt_dlp
import pandas as pd

# Spotify API credentials (replace with your actual credentials)
client_id = "YOUR_SPOTIFY_CLIENT_ID"
client_secret = "YOUR_SPOTIFY_CLIENT_SECRET"
playlist_id = 'YOUR_SPOTIFY_PLAYLIST_ID'

# Function to get Spotify access token using client credentials
def get_access_token(client_id, client_secret):
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })
    auth_response_data = auth_response.json()
    return auth_response_data['access_token']

# Function to fetch all tracks from a Spotify playlist (recursive for pagination)
def get_playlist_tracks_recursive(playlist_id, access_token, url=None):
    if url is None:
        url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    response = requests.get(url, headers=headers)
    data = response.json()
    
    tracks = []
    for item in data.get('items', []): 
        track = item.get('track')
        if track:
            track_name = track.get('name', 'Unknown Track')
            artists = ", ".join([artist['name'] for artist in track.get('artists', [])])
            track_info = f"{track_name} by {artists}"
            tracks.append(track_info)
    
    # Recursively get next page of tracks
    if data.get('next'):
        tracks.extend(get_playlist_tracks_recursive(playlist_id, access_token, data['next']))
    
    return tracks

# Get access token and playlist songs
access_token = get_access_token(client_id, client_secret)
songs = get_playlist_tracks_recursive(playlist_id, access_token)

# Save song list to Excel
df = pd.DataFrame(songs)
df.to_excel("songs_list.xlsx", index=False, engine='openpyxl')

# Read song list back from Excel
df2 = pd.read_excel(open('songs_list.xlsx', 'rb'))
print(df2)

# Convert DataFrame column to list of song names
songs = df2[0].tolist()

# Function to search YouTube for a song and return video URL
def search_youtube(song_name):
    videos_search = VideosSearch(song_name, limit=1)
    results = videos_search.result()
    if results['result']:
        video_url = 'https://www.youtube.com/watch?v=' + results['result'][0]['id']
        return video_url
    return None

# Function to download audio from YouTube video as MP3
def download_audio(video_url, song_name):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{song_name}.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_o
