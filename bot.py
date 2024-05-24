# import asyncio
import discord
import json
import os
import time

from discord.ext import commands
from utils.database import Database

# Config Setup
with open('config.json', 'r+') as f:
    config = json.load(f)
    TOKEN = config['TOKEN']

# Client setup
class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=discord.Intents.all())
        self.generated_data = {}

    async def setup_hook(self) -> None:
        print(f'{time.strftime("%H:%M:%S UTC", time.gmtime())}')
        print(f'Logged in as {client.user.name}')
        print(f'Bot ID: {str(client.user.id)}')
        print(f'Discord Version: {discord.__version__}')

        self.command_cogs = [f'cogs.{cog[:-3]}' for cog in os.listdir('./cogs') if cog.endswith('.py')]
        self.db = Database(config)

        for cog in self.command_cogs:
            print(f'Loading Extension: {cog}...')
            await self.load_extension(cog)

client = Client()

# Add a reload command for all cogs
@client.command(name='reload')
async def reload(ctx):
    print('Reloading Co-DM...')
    for cog in client.command_cogs:
        print(f'Reloading Extension: {cog}...')
        await client.reload_extension(cog)
    await ctx.send('Co-DM reloaded!')

client.run(TOKEN)