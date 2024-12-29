import discord
from discord.ext import commands
import logging

class Admin(commands.Cog, name='Admin'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='join', help='This command makes the bot join the voice channel.')
    async def join(self, ctx, channel_name=None):
        channel = discord.utils.get(ctx.guild.channels, name=channel_name) or ctx.author.voice.channel
        logging.info(f'Joining {channel}')

        await channel.connect()

    @commands.command(name='leave', help='This command makes the bot leave the voice channel.')
    async def leave(self, ctx):
        channel = ctx.voice_client.channel
        logging.info(f'Leaving {channel}')

        await ctx.voice_client.disconnect()
