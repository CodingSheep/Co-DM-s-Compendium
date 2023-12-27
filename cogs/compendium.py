import asyncio
import discord
import mysql.connector
import os

from discord.ext import commands

class Compendium(commands.Cog, name='compendium'):
    def __init__(self, bot):
        self.bot = bot
        
        
        # Connect to the SQL server
        try:
            self.connection = mysql.connector.connect(host=os.environ['SQL_HOST'],
                                                      database=os.environ['SQL_DB'],
                                                      user=os.environ['SQL_USER'],
                                                      password=os.environ['SQL_PASS'])
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
            exit()
        
    @commands.command(name='info')
    async def info(self, ctx, subtype = '', *, name = ''):
        
        subtype = subtype.lower()
        
        if not subtype or not name:
            await ctx.send('subtype and name must not be empty.')
            return
        if subtype not in ['tavern', 'npc', 'city', 'location']:
            await ctx.send(f'Subtype "{subtype}" is not valid. Valid Subtypes are: Tavern, NPC, City, Location')
            return
        
        output = self.print_results(subtype, name)
        await ctx.send(output)
        await ctx.send('Hey look! Valid inputs!')
    
    # Pass Info in for HTML formatting
    def print_results(self, subtype, name):
        output = f'print_results will look through the {subtype} table and return information on {name} in that table if possible.'
        return output
            
async def setup(client) -> None:
    await client.add_cog(Compendium(client))