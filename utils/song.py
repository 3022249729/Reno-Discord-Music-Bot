class Song:
    def __init__(self, data):
        # self.videolink = None
        # self.videocode = None
        # self.audio = None
        # self.uploader = None
        # self.title = None
        # self.thumbnail = None
        # self.duration = None
        # self.date = None
        # self.views = None
        # self.likes = None
        # self.dislikes = None
        # self.keyword = None

        self.populate_info(data)
        
    
    def populate_info(self, data):
        self.videocode = data.get('id')

        if "music.163.com" == data.get("webpage_url_domain"):
            self.audio = data.get('formats')[-1].get('url')
        elif data.get('_type') != "url":
            self.audio = data.get('url')
            if "youtube.com" == data.get("webpage_url_domain"):
                self.videolink = "https://www.youtube.com/watch?v=" + data.get('id')
        else:
            self.videolink = data.get('url')
            self.audio = None

        self.uploader = data.get('uploader')
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')

        if data.get('duration') is not None:
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