import os
import shutil
import json
import functools
import random
import logging
from .song import Song

class Playlist:
    def __init__(self, name=None):
        self.playlist_path = os.path.join(os.environ.get('DATA_PATH'), name)
        self.name = name
        self.songs = []
        self.index = 0
        self.loop = False
        self.load()
        self.fix()

    @staticmethod
    def save(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)

            songs = [song.dict() for song in self.songs]
            with open(os.path.join(self.playlist_path, 'playlist.json'), 'w+') as f:
                json.dump(songs, f, indent=4)

            return result

        return wrapper

    def load(self):
        try:
            with open(os.path.join(self.playlist_path, 'playlist.json')) as f:
                songs = json.load(f)
            self.songs = [Song(**song) for song in songs]

        except FileNotFoundError:
            self.songs = []

        if not self.songs:
            if not os.path.exists(self.playlist_path):
                os.makedirs(self.playlist_path)

            self.songs = [
                Song(
                    title=file.split('.')[0],
                    path=os.path.join(self.playlist_path, file)
                ) for file in os.listdir(self.playlist_path) if not file.endswith('.json')
            ]

    @save
    def fix(self):
        file_names = [file.split('.')[0] for file in os.listdir(self.playlist_path) if not file.endswith('.json')]

        for song in self.songs:
            if song.title not in file_names:
                self.songs.remove(song)

    def get(self, index=None):
        index = index or self.index

        return self.songs[index]

    def get_next(self, index=None, loop=None):
        index = index or self.index
        loop = loop or self.loop

        self.index = index if loop else (self.index + 1) % len(self.songs)

    def get_previous(self, index=None, loop=None):
        index = index or self.index
        loop = loop or self.loop

        self.index = index if loop else (self.index - 1) % len(self.songs)

    @save
    def add(self, song):
        if song not in self.songs:
            self.songs.append(song)

    @save
    def remove(self, index):
        return self.songs.pop(index)

    @save
    def clear(self):
        self.songs.clear()

    def list(self):
        return self.songs

    @save
    def shuffle(self):
        random.shuffle(self.songs)

    @save
    def move(self, from_index, to_index):
        try:
            song = self.songs.pop(from_index)
            self.songs.insert(to_index, song)

        except IndexError:
            logging.error('Index out of range while moving songs.')

    @staticmethod
    def delete(song_path):
        os.remove(song_path)

    def erase(self):
        shutil.rmtree(self.playlist_path)
