import discord
from discord.ext import commands
import logging
from ..playlist import Playlist
from .. import di
import asyncio

class Music(commands.Cog, name='Music'):
    def __init__(self, bot):
        self.bot = bot
        self.playlist = Playlist(name='default')
        self.do_stop = False

    @commands.command(name='play', help='Play music.')
    async def play(self, ctx, index=None):
        self.playlist.index = self.playlist.index if index is None else int(index)
        self.do_stop = False

        logging.info(f'Playing song {self.playlist.index} - {self.playlist.get().title}. Loop: {self.playlist.loop}.')

        def after(ctx):
            if not ctx.voice_client.is_playing() and not self.do_stop:
                self.playlist.next()

                coro = self.play(ctx)
                asyncio.run_coroutine_threadsafe(coro, self.bot.loop)

        ctx.voice_client.play(
            discord.FFmpegPCMAudio(self.playlist.get().path),
            after=lambda e: after(ctx)
        )

    @commands.command(name='pause', help='Pause music.')
    async def pause(self, ctx):
        logging.info('Pausing music.')

        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()

    @commands.command(name='resume', help='Resume music.')
    async def resume(self, ctx):
        logging.info('Resuming music.')

        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()

    @commands.command(name='stop', help='Stop music.')
    async def stop(self, ctx):
        logging.info('Stopping music.')

        self.do_stop = True
        self.playlist.index = 0

        ctx.voice_client.stop()

    @commands.command(name='list', help='Show available playlists.')
    async def list(self, ctx):
        logging.info('Showing playlists.')

        playlists = [f"{playlist}" for playlist in self.playlist.list()]

        await ctx.send(f'{"\n".join(playlists)}')

    @commands.command(name='show', help='Show current playlist songs.')
    async def show(self, ctx):
        logging.info('Showing current song and playlist.')

        current_playlist = [f"{i}\t-\t{song.title}" for i, song in enumerate(self.playlist.show())]

        await ctx.send(f'Current playlist: {self.playlist.name}\n\n{"\n".join(current_playlist)}')

    @commands.command(name='add', help='Add a song to the playlist.')
    async def add(self, ctx, song_name):
        song = di['youtube'].get(query=song_name, name=self.playlist.name)

        self.playlist.add(song)

        logging.info(f'Added {song.title} to the playlist.')

    @commands.command(name='remove', help='This command removes a song from the playlist.')
    async def remove(self, ctx, index):
        index = int(index)

        song = self.playlist.remove(index)

        logging.info(f'Removed song {index}. {song.title}.')

    @commands.command(name='clear', help='Clear playlist.')
    async def clear(self, ctx):
        self.playlist.clear()

        logging.info('Playlist cleared.')

    @commands.command(name='delete', help='Delete a song or a playlist.')
    async def delete(self, ctx, index=None):
        if index:
            index = int(index)
            song = self.playlist.remove(index)
            self.playlist.delete(song.path)

        else:
            self.playlist.clear()
            self.playlist.erase()

        logging.info(f'Deleted song {index}. {song.title}.')

    @commands.command(name='shuffle', help='Shuffle playlist songs.')
    async def shuffle(self, ctx):
        self.playlist.shuffle()

        logging.info('Shuffled playlist songs.')

    @commands.command(name='move', help='Move songs in the playlist.')
    async def move(self, ctx, from_index, to_index):
        from_index = int(from_index)
        to_index = int(to_index)

        self.playlist.move(from_index, to_index)

        logging.info(f'Moving song from index {from_index} to index {to_index}.')

    @commands.command(name='next', help='Go to the next song.')
    async def next(self, ctx):
        logging.info('Going to the next song.')

        self.do_stop = True
        self.playlist.next()

        ctx.voice_client.stop()

        await self.play(ctx)

    @commands.command(name='prev', help='Go to the previous song.')
    async def prev(self, ctx):
        logging.info('Going to the previous song.')

        self.do_stop = True
        self.playlist.previous()

        ctx.voice_client.stop()

        await self.play(ctx)

    @commands.command(name='loop', help='Toggle song loop.')
    async def loop(self, ctx):
        self.playlist.loop = not self.playlist.loop

        logging.info(f'Loop: {self.playlist.loop}.')

    @commands.command(name='switch', help='Switch playlist.')
    async def switch(self, ctx, playlist_name):
        self.playlist = Playlist(name=playlist_name)

        logging.info(f'Switching to playlist {playlist_name}.')

    @commands.command(name='reload', help='Reload playlist.', hidden=True)
    async def reload(self, ctx):
        self.playlist.load()
        self.playlist.fix()

        logging.info('Playlist reloaded.')

    @commands.command(name='reset', help='Reset playlist.', hidden=True)
    async def reset(self, ctx):
        self.playlist.clear()
        self.playlist.load()
        self.playlist.fix()

        logging.info('Playlist reset.')
