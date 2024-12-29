from discord.ext import commands
from . import di

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup(self):
        for cog in di['cogs']:
            await self.add_cog(cog(self))
