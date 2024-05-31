import asyncio
import discord
import google.generativeai as genai
import json
import os
import time

# from bot import generated_data
from discord.ext import commands

class Gemini(commands.Cog, name='gemini'):
    def __init__(self, bot):
        self.bot = bot
        
        # Gemini setup
        genai.configure(api_key=self.bot.config['GEMINI_KEY'])
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')

    def send_request(self, request):
        response = self.model.generate_content(request)
        return response.text, False

        # TODO: Figure out how to do an error check with Gemini. API's not exactly being helpful here.
    
        # if response.status == "success":
        #     return response.text, False
        # return f"Request failed with status: {response.status}", True

    def check_markdown(self, res):
        if res.startswith("```") and res.endswith("```"):
            res = res[3:-3].strip()
            if res.startswith("json"):
                res = res[4:].strip()
        return res
        
    @commands.command(name='generate_gemini')
    async def generate(self, ctx, subtype='tavern', *, context=''):
        subtype = subtype.lower()
        
        match subtype:
            case 'tavern': # DONE
                request = f'''
                    Generate a Tavern as a JSON object with the keys Name, Location, and Description.
                    Limit the Location as the name of a City, Country, or Geographical Location.
                    Additionally, generate 3 NPCs found at this tavern as a JSON object with the keys Name, Role, and Description.
                    Limit all descriptions to 2-3 sentences.
                    Text: {context}
                    '''
                table='locations'
            case 'npc':
                request = f'''
                    Generate a NPC as a JSON object with the keys Name, Role, Location, and Description.
                    Limit the description to 2-3 sentences.
                    Limit the Location as the name of a City, Country, or Geographical Location.
                    Text: {context}
                    '''
                table='npcs'
            case 'bounty':
                request = f'''
                    Generate a bounty as a JSON object with the keys Quest, Recommended Level, and Description.
                    Text: {context}
                    '''
                table = ''
            case 'city':
                if len(context) == 0:
                    await ctx.send(f'To generate a city, please provide context.')
                    return
                request = f'''
                    Generate a City as a JSON object with the keys Name, Location, Description, and (if applicable) Districts.
                    Limit the Location as the name of a Country or Geographical Location.
                    If Districts are applicable, each District must be a tuple with the keys Name and Description.
                    Limit all descriptions to 2-3 sentences.
                    Text: {context}
                    '''
                table='cities'
            case 'location':
                if len(context) == 0:
                    await ctx.send(f'To generate a description for a location, please provide context.')
                    return
                request = f'''
                    Generate a Location as a JSON object with the keys Name, Location, and Description.
                    Limit the Location as the name of a Country.
                    Limit all descriptions to 2-3 sentences.
                    Text: {context}
                    '''
                table='locations'
            case default:
                await ctx.send(f"Subtype \"{subtype}\" does not exist. Valid Subtypes are: Tavern, NPC, Bounty, City, Location.")
                return

        # While processing, send a processing message. Delete when processing is finished.
        processing_msg = await ctx.send('Processing...')
        res, err = self.send_request(request)
        await processing_msg.delete()

        # Check for Error
        if err:
            await ctx.send(f'Error: {res}')
            return

        # Sanity Check 1: If no Error, ensure GPT output isn't surrounded in Markdown before translating to JSON Object
        res = self.check_markdown(res)
        # To save later
        self.bot.generated_data = {table: json.loads(res)}

        if len(res) <= 2000:
            # TEMPORARY: Ensure Markdown wrapping for res
            res = f'```json\n{res}\n```'
            await ctx.send(res)
        else:
            res = json.loads(res)
            for key in res.keys():
                await ctx.send(f'```json\n{key}: {res[key]}```')
            
async def setup(client) -> None:
    await client.add_cog(Gemini(client))