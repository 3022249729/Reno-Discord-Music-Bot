import yt_dlp
import re

ytdlopts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'logtostderr': False,
    'no_warnings': False, 
    'source_address': '0.0.0.0'
    # 'default_search': 'auto',
    # 'quiet': True, 
    # 'nocheckcertificate': True,
    # 'ignoreerrors': False,
    # 'restrictfilenames': True,
}



class Song:
    def __init__(self, keyword):
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
        self.extract(keyword)

    def get_url(self, content):
        regex = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")

        if re.search(regex, content):
            result = regex.search(content)
            url = result.group(0)
            return url
        else:
            return None
        #get link from user input


    def extract(self, content):
        global songInfo

        url = self.get_url(content)
        
        with yt_dlp.YoutubeDL(ytdlopts) as ydl:
            if url:    
                r = ydl.extract_info(url, download=False)
                self.videolink = url
                self.videocode = r.get('id')
                self.keyword = r.get('title')
            else: 
                r = ydl.extract_info(f"ytsearch:{content}", download=False)['entries'][0]
                self.videocode = r.get('id')
                self.videolink = 'https://www.youtube.com/watch?v=' + self.videocode
                self.keyword = content

        self.audio = r.get('url')
        self.uploader = r.get('uploader')
        self.title = r.get('title')
        self.thumbnail = r.get('thumbnail')

        seconds = r.get('duration') % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60

        if hour > 0:
            self.duration = "%d:%02d:%02d" % (hour, minutes, seconds)
        else:
            self.duration = "%02d:%02d" % ( minutes, seconds)

        self.date = r.get('upload_date')
        self.views = r.get('view_count')
        self.likes = r.get('like_count')
        self.dislikes = r.get('dislike_count')
