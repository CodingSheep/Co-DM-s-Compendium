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

    # TODO: Get Info from item in SQL server
    # Implement once saving is properly implemented
    @commands.command(name='info')
    async def info(self, ctx, subtype = '', *, name = ''):
        
        subtype = subtype.lower()

        print(self.bot.output)

        # Search through multiple tables based on input?
        # See if better system for searching through table for "thing like" instead of pulling whole table.
        
        # if not subtype or not name:
        #     await ctx.send('subtype and name must not be empty.')
        #     return
        # if subtype not in ['tavern', 'npc', 'city', 'location']:
        #     await ctx.send(f'Subtype "{subtype}" is not valid. Valid Subtypes are: Tavern, NPC, City, Location')
        #     return
        
        # output = self.print_results(subtype, name)
        # await ctx.send(output)
        await ctx.send(self.bot.output)

    # TODO: Expand on saving items to server
    @commands.command(name='save')
    async def save(self, ctx):
        # Delete Command Message
        await ctx.message.delete()
        
        # TODO:
        # 1) Read last 2 messages to gain context of last command sent
        # 2) Check if command was GPT generation (!generate). If so, start processing. Else, ignore
        # 3) Parse text to include at least [Name], [Description]
        # 3.1) NPC Table: [Name], [Race Class], [Description]
        # 3.2) Tavern Table: [Name], [City], [Description]
        # 3.3) City/Locale Table: [Name], [Country], [Description]
        # 3.3.1) Districts can be looped into the description of Cities.
        # 3.4) Bounties do not need to be saved
        # Once the data is saved, output a response saying as much
        await ctx.send('Saved!')
    
    # TODO: Pass Info in for HTML formatting
    # TODO: Move above commands?
    def print_results(self, subtype, name):
        output = f'print_results will look through the {subtype} table and return information on {name} in that table if possible.'
        return output
            
async def setup(client) -> None:
    await client.add_cog(Compendium(client))