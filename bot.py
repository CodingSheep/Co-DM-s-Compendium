import asyncio
import discord
import os

from discord.ext import commands


# Setup
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(intents=intents, command_prefix='!')

@client.event
async def setup_hook() -> None:
    await client.load_extension('cogs.play_sound')


# Run the Discord bot
client.run(os.environ['DISCORD_KEY'])