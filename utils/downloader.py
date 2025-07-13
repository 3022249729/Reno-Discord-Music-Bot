import yt_dlp
import re
from utils.song import Song

class Downloader:
    def get_url(self, content):
        regex = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),#]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")

        if re.search(regex, content):
            result = regex.search(content)
            url = result.group(0)
            return url
        else:
            return None
        #get link from user input


    def extract_flat(self, content):
        ytdlopts = {
            'format': 'bestaudio[ext=opus]/bestaudio',
            'logtostderr': False,
            'no_warnings': False, 
            'skip_download': True,
            'quiet': True, 
            'extract_flat': True,
            # 'playlist_items': '1-200',
            'source_address': '0.0.0.0',
            # 'ignoreerrors': True,
            
            }
        
        contentUrl = self.get_url(content)
        
        with yt_dlp.YoutubeDL(ytdlopts) as ydl:
            # if url not provided, search for the first available content on youtube
            if not contentUrl:
                ytdlopts['noplaylist'] = True

                data = ydl.extract_info(f"ytsearch:{content}", download=False)['entries'][0]
                song = Song(data)
                song.keyword = content
                return [song]
            
            # if url provided, just extract flat for all videos
            songs = []

            if "music.163.com" in contentUrl and "song" in contentUrl:
                song = Song({})
                song.duration = 0
                song.videolink = contentUrl

                songs.append(song)
                return songs

            data = ydl.extract_info(contentUrl, download=False)

            if 'entries' in data:
                for entry in data['entries']:
                    song = Song(entry)
                    song.keyword = entry.get('title')
                    songs.append(song)
            else:
                song = Song(data)
                song.keyword = data.get('title')
                songs.append(song)

            return songs


    def extract_audio(self, song:Song):
        ytdlopts = {
        'format': 'bestaudio[ext=opus]/bestaudio',
        'logtostderr': False,
        'no_warnings': False, 
        'skip_download': True,
        'quiet': True, 
        'noplaylist': True
        }
        with yt_dlp.YoutubeDL(ytdlopts) as ydl:
            data = ydl.extract_info(song.videolink, download=False)
            song.populate_info(data)


