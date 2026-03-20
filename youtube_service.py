from ytmusicapi import YTMusic
import yt_dlp
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

    def download_song(self, video_id):
        try:
            import os
            
            # Use absolute paths specifically to avoid any CWD/Windows WinError 5 issues
            base_dir = os.path.dirname(os.path.abspath(__file__))
            assets_dir = os.path.join(base_dir, "assets")
            os.makedirs(assets_dir, exist_ok=True)
            
            # Check if M4A file exists
            if os.path.exists(os.path.join(assets_dir, f"{video_id}.m4a")):
                return f"{video_id}.m4a"

            ydl_opts = {
                'format': '140', # 140 guarantees native AAC `.m4a` file without FFmpeg
                'paths': {'home': assets_dir},
                'outtmpl': {'default': f'{video_id}.m4a'},
                'quiet': True,
                'no_warnings': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=True)
                return f"{video_id}.m4a"
        except Exception as e:
            print(f"Download Error: {e}")
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
