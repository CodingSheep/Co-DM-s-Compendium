import asyncio
import discord
import os


from difflib import get_close_matches
from discord import FFmpegPCMAudio, PCMVolumeTransformer
from discord.ext import commands

class Sounds(commands.Cog, name='sounds'):
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None

        # Database connection
        self.connection = self.bot.db.connection
        self.cursor = self.bot.db.cursor
    
    @commands.command(name='join')
    async def join(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("You are not in a voice channel.")
            return
        elif self.voice_client is not None:
            await ctx.send("I am already in a voice channel.")
            return

        voice_channel = ctx.author.voice.channel
        self.voice_client = await voice_channel.connect()
        await ctx.guild.change_voice_state(channel=voice_channel, self_mute=False, self_deaf=True)
        await ctx.send(f"Joined voice channel {voice_channel.name}.")
    
    @commands.command(name='leave')
    async def leave(self, ctx):
        if self.voice_client is None:
            await ctx.send("I am not currently in a voice channel.")
            return

        await self.voice_client.disconnect()
        self.voice_client = None
        await ctx.send("Left voice channel.")

    # Define a command to play a specific mp3 file
    @commands.command(name='play_sound')
    async def play_sound(self, ctx, creature_name, *, subset=None):
        if self.voice_client is None:
            await ctx.send('I am not currently in a voice channel. Use !join for me to join a voice channel.')
            return

        # Set input to lowercase
        creature_name = creature_name.lower()
        if subset:
            subset = subset.lower()

        cursor = self.connection.cursor()
        
        query = "SELECT file_path FROM sounds WHERE creature_name = %(creature_name)s"
        insert = {'creature_name': creature_name}
        if subset:
            query += " AND sound_type = %(sound_type)s"
            insert['sound_type'] = subset

        cursor.execute(query, insert)
        result = cursor.fetchall()
        
        # If no result
        if len(result) == 0:
            # Check if the creature name is misspelled
            cursor.execute('SELECT creature_name FROM sounds')
            creature_names = sorted(list(set([row[0] for row in cursor.fetchall()])))

            # If spelled correctly, the sound type is wrong
            if creature_name in creature_names:
                cursor.execute("SELECT sound_type FROM sounds WHERE creature_name = %(creature_name)s", {'creature_name': creature_name})
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
            cursor.execute("SELECT sound_type FROM sounds WHERE creature_name = %(creature_name)s", {'creature_name': creature_name})
            subsets = [row[0] for row in cursor.fetchall()]
            subset_str = ", ".join(subsets)
            await ctx.send(f'No subset specified. Available subsets for "{creature_name}": {subset_str}')
            return

        # All errors handled    
        filepath = result[0][0]
        await ctx.send(f'Playing {filepath}.')

        # Check if the bot is already in a voice channel
        source = PCMVolumeTransformer(FFmpegPCMAudio(filepath), volume=0.5)
        
        self.voice_client.play(source)
        while self.voice_client.is_playing():
            await asyncio.sleep(1)

async def setup(client) -> None:
    await client.add_cog(Sounds(client))