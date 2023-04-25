import asyncio
import discord
import mysql.connector
import nacl

from difflib import get_close_matches
from discord import FFmpegPCMAudio, PCMVolumeTransformer
from discord.ext import commands
from mysql.connector import Error

DISCORD_KEY = os.environ['DISCORD_KEY']
SQL_HOST = os.environ['SQL_HOST']
SQL_DB = os.environ['SQL_DB']
SQL_USER = os.environ['SQL_USER']
SQL_PASS = os.environ['SQL_PASS']

# Connect to the SQL server
try:
    connection = mysql.connector.connect(host=SQL_HOST,
                                         database=SQL_DB,
                                         user=SQL_USER,
                                         password=SQL_PASS)
except Error as e:
    print(f"Error while connecting to MySQL: {e}")
    exit()

# Create the Discord bot
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!',intents=intents)
voice_client = None


# Define a command to join the voice channel
@client.command(name='join')
async def join(ctx):
    global voice_client
    if ctx.author.voice is None:
        await ctx.send("You are not in a voice channel.")
        return
    elif voice_client is not None:
        await ctx.send("I am already in a voice channel.")
        return
    
    voice_channel = ctx.author.voice.channel
    voice_client = await voice_channel.connect()
    await ctx.send(f"Joined voice channel {voice_channel.name}.")

# Define a command to leave the voice channel
@client.command(name='leave')
async def leave(ctx):
    global voice_client
    if voice_client is None:
        await ctx.send("I am not currently in a voice channel.")
        return
    
    await voice_client.disconnect()
    voice_client = None
    await ctx.send("Left voice channel.")

# Define a command to play a specific mp3 file
@client.command(name='play_sound')
async def play_sound(ctx, creature_name, subset=None):
    global voice_client
    
    if voice_client is None:
        await ctx.send('I am not currently in a voice channel. Use !join for me to join a voice channel.')
        return
    
    # Set input to lowercase
    creature_name = creature_name.lower()
    if subset:
        subset = subset.lower()
    
    cursor = connection.cursor()
    query = f'SELECT file_path FROM sounds WHERE creature_name="{creature_name}"'
    if subset:
        query += f' AND sound_type="{subset}"'
        
    cursor.execute(query)
    result = cursor.fetchall()
    
    # If no result
    if len(result) == 0:
        # Check if the creature name is misspelled
        cursor.execute('SELECT creature_name FROM sounds')
        creature_names = sorted(list(set([row[0] for row in cursor.fetchall()])))
        
        # If spelled correctly, the sound type is wrong
        if creature_name in creature_names:
            cursor.execute(f'SELECT sound_type FROM sounds WHERE creature_name="{creature_name}"')
            subsets = [row[0] for row in cursor.fetchall()]
            subset_str = ", ".join(subsets)
            await ctx.send(f'No subset "{subset}" found. Available subsets for "{creature_name}": {subset_str}')
            return
            
        # If not spelled correctly
        matches = get_close_matches(creature_name, creature_names, cutoff=0.6)
        if matches:
            match_str = ', '.join(matches)
            await ctx.send(f'No sound file exists for "{creature_name}". Did you mean one of the following: {match_str}?')
        else:
            await ctx.send(f'No sound file found for creature "{creature_name}" and subset "{subset}".')
        return
    
    # If multiple results
    if len(result) > 1:
        print('\n-->1 result!--\n')
        cursor.execute(f'SELECT sound_type FROM sounds WHERE creature_name="{creature_name}"')
        subsets = [row[0] for row in cursor.fetchall()]
        subset_str = ", ".join(subsets)
        await ctx.send(f'No subset specified. Available subsets for "{creature_name}": {subset_str}')
        return
        
    # All errors handled    
    filepath = result[0][0]
    await ctx.send(f'Playing {filepath}.')
    
    # Check if the bot is already in a voice channel
    source = PCMVolumeTransformer(FFmpegPCMAudio(filepath), volume=0.6)
    voice_client.play(source)
    while voice_client.is_playing():
        await asyncio.sleep(1)

# Run the Discord bot
client.run(const.discordKey)
