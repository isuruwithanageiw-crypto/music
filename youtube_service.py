from ytmusicapi import YTMusic
from pytubefix import YouTube
import threading

class YouTubeMusicService:
    def __init__(self):
        self.ytmusic = YTMusic()
        
    def search_songs(self, query):
        try:
            results = self.ytmusic.search(query, filter="songs")
            songs = []
            for item in results:
                thumbnail = ""
                if item.get("thumbnails"):
                    thumbnail = item["thumbnails"][-1]["url"]
                
                artist = "Unknown Artist"
                if item.get("artists") and len(item["artists"]) > 0:
                    artist = item["artists"][0]["name"]
                    
                songs.append({
                    "id": item.get("videoId", ""),
                    "title": item.get("title", ""),
                    "artist": artist,
                    "thumbnail": thumbnail,
                    "duration": item.get("duration", "0:00")
                })
            return songs
        except Exception as e:
            print(f"Error searching: {e}")
            return []

    def get_song_url(self, video_id):
        try:
            yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
            audio_stream = yt.streams.get_audio_only()
            if audio_stream:
                return audio_stream.url
            return None
        except Exception as e:
            print(f"URL Fetch Error: {e}")
            return None

    def get_search_suggestions(self, query):
        try:
            return self.ytmusic.get_search_suggestions(query)
        except Exception as e:
            print(f"Suggestions Error: {e}")
            return []

    def get_up_next(self, video_id):
        try:
            watch = self.ytmusic.get_watch_playlist(videoId=video_id)
            tracks = watch.get('tracks', [])
            res = []
            for item in tracks[1:]: # Skip the current track
                thumbnail = ""
                if item.get("thumbnails"):
                    thumbnail = item["thumbnails"][-1]["url"]
                
                artist = "Unknown Artist"
                if item.get("artists") and len(item["artists"]) > 0:
                    artist = item["artists"][0]["name"]
                    
                res.append({
                    "id": item.get("videoId", ""),
                    "title": item.get("title", ""),
                    "artist": artist,
                    "thumbnail": thumbnail,
                })
            return res
        except Exception as e:
            print(f"Watch Playlist Error: {e}")
            return []
