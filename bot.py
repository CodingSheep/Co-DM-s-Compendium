import asyncio
import discord
import os

from discord.ext import commands
from utils.database import Database

# Setup
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(intents=intents, command_prefix='!')
db = Database()
generated_data = {}

@client.event
async def setup_hook() -> None:
    for cog in os.listdir('./cogs'):
        if cog.endswith('.py'):
            extension = f'cogs.{cog[:-3]}'
            print(f'Loading Extension: {extension}...')
            await client.load_extension(extension)

@client.command(name='reload')
async def reload() -> None:
    print('Reloading Co-DM...')
    for cog in os.listdir('./cogs'):
        if cog.endswith('.py'):
            extension = f'cogs.{cog[:-3]}'
            print(f'Reloading Extension: {extension}...')
            await client.reload_extension(extension)
    await ctx.send('Co-DM reloaded!')

# Run the Discord bot
client.run(os.environ['DISCORD_KEY'])