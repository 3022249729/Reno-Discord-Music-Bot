import yt_dlp
import re

class Song:
    def __init__(self, data):
        self.videolink = None
        self.videocode = None
        self.audio = None
        self.uploader = None
        self.title = None
        self.thumbnail = None
        self.duration = None
        self.date = None
        self.views = None
        self.likes = None
        self.dislikes = None
        self.keyword = None
        self.populate_info(data)
        
    
    def populate_info(self, data):
        self.videocode = data.get('id')
        if data.get('_type') != "url":
            self.audio = data.get('url')
        self.uploader = data.get('uploader')
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')

        seconds = data.get('duration') % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60

        if hour > 0:
            self.duration = "%d:%02d:%02d" % (hour, minutes, seconds)
        else:
            self.duration = "%02d:%02d" % ( minutes, seconds)

        self.date = data.get('upload_date')
        self.views = data.get('view_count')
        self.likes = data.get('like_count')
        self.dislikes = data.get('dislike_count')

class Downloader:
    def get_url(self, content):
        regex = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
        regex = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),#]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")

        if re.search(regex, content):
            result = regex.search(content)
            url = result.group(0)
            return url
        else:
            return None
        #get link from user input


    def extract(self, content):
        ytdlopts = {
        'format': 'bestaudio[ext=opus]/bestaudio',
        'logtostderr': False,
        'no_warnings': False, 
        'source_address': '0.0.0.0',
        'skip_download': True,
        'quiet': True, 
        # 'ignoreerrors': True,
        'extract_flat': 'in_playlist',
        'playlist_items': '1-100'
        }

        url = self.get_url(content)
        
        with yt_dlp.YoutubeDL(ytdlopts) as ydl:
            if url:
                meta = ydl.extract_info(url, download=False) # extract all metadata from the url
                ytdlopts.pop("extract_flat")
                ytdlopts['noplaylist'] = True
                # modify ytdlopts to extract audio

                if 'entries' in meta: # url is a playlist
                    song_objects = []

                    first_song_data = ydl.extract_info(url, download=False)
                    first_song = Song(first_song_data)
                    first_song.videolink = url
                    first_song.keyword = first_song_data.get('title')
                    song_objects.append(first_song)

                    for entry in meta['entries'][1:]:
                        song_obj = Song(entry)
                        song_obj.videolink = 'https://www.youtube.com/watch?v=' + entry['id']
                        song_obj.keyword = entry.get('title')
                        song_objects.append(song_obj)

                    return song_objects

                else: # url is not a playlist, extract again for audio
                    data = ydl.extract_info(url, download=False)
                    song = Song(data)
                    song.videolink = url
                    song.keyword = data.get('title')
                    return [song]
                
            else:
                ytdlopts.pop("extract_flat")
                ytdlopts['noplaylist'] = True

                data = ydl.extract_info(f"ytsearch:{content}", download=False)['entries'][0]
                song = Song(data)
                song.videolink = 'https://www.youtube.com/watch?v=' + song.videocode
                song.keyword = content
                return [song]
            

    def extract_and_update(self, song:Song):
        ytdlopts = {
        'format': 'bestaudio[ext=opus]/bestaudio',
        'logtostderr': False,
        'no_warnings': False, 
        'source_address': '0.0.0.0',
        'skip_download': True,
        'quiet': True, 
        'noplaylist': True
        }

        
        with yt_dlp.YoutubeDL(ytdlopts) as ydl:
            meta = ydl.extract_info(song.videolink, download=False)

            song.audio = meta.get('url')
            song.uploader = meta.get('uploader')
            song.thumbnail = meta.get('thumbnail')
            song.date = meta.get('upload_date')
            song.views = meta.get('view_count')
            song.likes = meta.get('like_count')
            song.dislikes = meta.get('dislike_count')


