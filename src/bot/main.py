import discord
from lib import di

async def main():
    intents = discord.Intents.all()
    intents.message_content = True
    intents.voice_states = True

    bot = di['bot'](command_prefix='!', intents=intents)
    await bot.setup()

    await bot.start(token=di['token'])

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
