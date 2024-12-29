import os
from kink import inject
from pytubefix import Search, YouTube
from .song import Song

@inject
class Youtube:
    def __init__(self, data_path):
        self.data_path = data_path

    def get(self, query, name):
        url = self.search(query=query)
        title, path = self.download(url=url, name=name)

        return Song(title=title, path=path)

    def search(self, query):
        search = Search(query=query)
        video_id = search.videos[0].video_id

        return f'https://www.youtube.com/watch?v={video_id}'

    def download(self, url, name):
        yt = YouTube(url)
        stream = yt.streams.filter(only_audio=True, file_extension="mp4").first()
        path = stream.download(output_path=os.path.join(self.data_path, name))

        return yt.title, path
