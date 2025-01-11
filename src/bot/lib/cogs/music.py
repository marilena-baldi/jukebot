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

        embed = discord.Embed(
            title=f'▶\t{self.playlist.index}\t-\t{self.playlist.get().title}',
            color=discord.Color.green()
        )

        await ctx.send(embed=embed)

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

        embed = discord.Embed(
            title=f'❚❚\t{self.playlist.index}\t-\t{self.playlist.get().title}',
            color=discord.Color.yellow()
        )

        await ctx.send(embed=embed)

        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()

    @commands.command(name='resume', help='Resume music.')
    async def resume(self, ctx):
        logging.info('Resuming music.')

        embed = discord.Embed(
            title=f'▶\t{self.playlist.index}\t-\t{self.playlist.get().title}',
            color=discord.Color.green()
        )

        await ctx.send(embed=embed)

        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()

    @commands.command(name='stop', help='Stop music.')
    async def stop(self, ctx):
        logging.info('Stopping music.')

        embed = discord.Embed(
            title=f'◼\t{self.playlist.index}\t-\t{self.playlist.get().title}',
            color=discord.Color.red()
        )

        await ctx.send(embed=embed)

        self.do_stop = True
        self.playlist.index = 0

        ctx.voice_client.stop()

    @commands.command(name='list', help='Show available playlists.')
    async def list(self, ctx):
        logging.info('Showing playlists.')

        playlists = [f"{playlist}" for playlist in self.playlist.list()]

        embed = discord.Embed(
            title='☰\tPlaylists',
            description=f'{"\n".join(playlists)}',
            color=discord.Color.blue()
        )

        await ctx.send(embed=embed)

    @commands.command(name='show', help='Show current playlist songs.')
    async def show(self, ctx):
        logging.info('Showing current song and playlist.')

        current_playlist = [f"{i}\t-\t{song.title}" for i, song in enumerate(self.playlist.show())]

        embed = discord.Embed(
            title=f'☰\tPlaylist: {self.playlist.name}',
            description=f'{"\n".join(current_playlist)}',
            color=discord.Color.blue()
        )

        await ctx.send(embed=embed)

    @commands.command(name='add', help='Add a song to the playlist.')
    async def add(self, ctx, song_name):
        logging.info(f'Adding song {song_name}.')

        song = di['youtube'].get(query=song_name, name=self.playlist.name)

        self.playlist.add(song)

        embed = discord.Embed(
            title=f'+\tAdded {song.title} to {self.playlist.name}',
            color=discord.Color.dark_green()
        )

        await ctx.send(embed=embed)

    @commands.command(name='remove', help='Remove a song from the playlist.')
    async def remove(self, ctx, index):
        logging.info(f'Removing song {index}.')

        index = int(index)

        song = self.playlist.remove(index)

        embed = discord.Embed(
            title=f'✖\tRemoved {song.title} from {self.playlist.name}',
            color=discord.Color.orange()
        )

        await ctx.send(embed=embed)

    @commands.command(name='clear', help='Clear playlist.')
    async def clear(self, ctx):
        logging.info('Clearing playlist.')

        self.playlist.clear()

        embed = discord.Embed(
            title=f'⊘\tCleared {self.playlist.name}',
            color=discord.Color.orange()
        )

        await ctx.send(embed=embed)

    @commands.command(name='delete', help='Delete a song or a playlist.')
    async def delete(self, ctx, index=None):
        if index:
            logging.info(f'Deleting song {index}.')

            index = int(index)
            song = self.playlist.remove(index)
            self.playlist.delete(song.path)

            await self.show(ctx)

        else:
            logging.info('Deleting playlist.')

            self.playlist.clear()
            self.playlist.erase()

            self.list(ctx)

    @commands.command(name='shuffle', help='Shuffle playlist songs.')
    async def shuffle(self, ctx):
        logging.info('Shuffling playlist.')

        self.playlist.shuffle()

        await self.show(ctx)

    @commands.command(name='move', help='Move songs in the playlist.')
    async def move(self, ctx, from_index, to_index):
        logging.info(f'Moving song from index {from_index} to index {to_index}.')

        from_index = int(from_index)
        to_index = int(to_index)

        self.playlist.move(from_index, to_index)

        await self.show(ctx)

    @commands.command(name='next', help='Go to the next song.')
    async def next(self, ctx):
        logging.info('Going to the next song.')

        self.playlist.next()

        ctx.voice_client.pause()

        await self.play(ctx)

    @commands.command(name='prev', help='Go to the previous song.')
    async def prev(self, ctx):
        logging.info('Going to the previous song.')

        self.playlist.previous()

        ctx.voice_client.pause()

        await self.play(ctx)

    @commands.command(name='loop', help='Toggle song loop.')
    async def loop(self, ctx):
        logging.info(f'Toggling song loop.')

        self.playlist.loop = not self.playlist.loop

        embed = discord.Embed(
            title=f'↻\tLoop: {self.playlist.loop}',
            color=discord.Color.magenta()
        )

        await ctx.send(embed=embed)

    @commands.command(name='switch', help='Switch playlist.')
    async def switch(self, ctx, playlist_name):
        logging.info(f'Switching to playlist {playlist_name}.')

        self.playlist = Playlist(name=playlist_name)

        await self.show(ctx)

    @commands.command(name='reload', help='Reload playlist.', hidden=True)
    async def reload(self, ctx):
        logging.info('Reloading playlist.')

        self.playlist.load()
        self.playlist.fix()

    @commands.command(name='reset', help='Reset playlist.', hidden=True)
    async def reset(self, ctx):
        logging.info('Resetting playlist.')

        self.playlist.clear()
        self.playlist.load()
        self.playlist.fix()
