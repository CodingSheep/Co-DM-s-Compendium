import asyncio
import discord
import json
import mysql.connector
import os

from discord.ext import commands
from utils.infocard import InfoCard

class Compendium(commands.Cog, name='compendium'):
    def __init__(self, bot: commands.Bot):
        self.client = bot
        self.db = bot.db

    # TODO: Get Info from item in SQL server
    # Implement once saving is properly implemented
    @commands.command(name='info')
    async def info(self, ctx, *, name = ''):
        res = self.db.search(name)
        if list(res.keys())[0] == 'message':
            await ctx.send(res)
            return
        
        card = InfoCard(res)
        await ctx.send(embed=card.info())

    @commands.command(name='check')
    async def check(self, ctx):
        await ctx.send(self.client.generated_data)

    # TODO: Expand on saving items to server
    @commands.command(name='save')
    async def save(self, ctx):
        # Delete Command Message
        await ctx.message.delete()

        # Check if we have a saved object in memory
        data = self.client.generated_data
        if data:
            # If not city with districts, we're fine and can continue as normal
            if list(data.keys())[0] is not 'cities':
                table = list(self.client.generated_data.keys())[0]
                object = list(self.client.generated_data.values())[0]
    
                if not table:
                    await ctx.send('Bounties are not saved currently.')
                    return
                res = self.db.save(table, object)
                await ctx.send(f'Saving {object["Name"]} to Table {table}.')
            else:
                object = {
                    'Name': data['cities']['Name'],
                    'Location': data['cities']['Location'],
                    'Description': data['cities']['Description']
                }
                res = self.db.save('cities', object)
                await ctx.send(f'Saving {object["Name"]} to Table cities.')

                # Now we deal with districts
                city_id = self.db.cursor.lastrowid
                for district in data['cities']['Districts']:
                    district['CityID'] = city_id
                    res = self.db.save('districts', district)
                    await ctx.send(f'Saving {district["Name"]} to Table districts.')
        else:
            await ctx.send('No Generated Object currently in memory! Please provide something')
    
    # TODO: Pass Info in for HTML formatting
    # TODO: Move above commands?
    def print_results(self, subtype, name):
        output = f'print_results will look through the {subtype} table and return information on {name} in that table if possible.'
        return output
            
async def setup(client) -> None:
    await client.add_cog(Compendium(client))