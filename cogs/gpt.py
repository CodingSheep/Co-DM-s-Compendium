import asyncio
import discord
import json
import os
import time

# from bot import generated_data
from discord.ext import commands
from openai import OpenAI

class GPT(commands.Cog, name='gpt'):
    def __init__(self, bot):
        self.bot = bot
        
        # OpenAI setup
        self.client = OpenAI()
        self.assistant = self.client.beta.assistants.retrieve(bot.config['GPT_KEY'])
        self.thread = self.client.beta.threads.create()
        
    def send_request(self, request):
        message = self.client.beta.threads.messages.create(
            thread_id = self.thread.id,
            role = 'user',
            content = request
        )
        
        run = self.client.beta.threads.runs.create(
            thread_id = self.thread.id,
            assistant_id = self.assistant.id
        )
        
        while run.status == 'queued' or run.status == 'in_progress':
            time.sleep(5)
            run = self.client.beta.threads.runs.retrieve(
              thread_id = self.thread.id,
              run_id = run.id
            )

        # Catch Errors just in case as well as the intended output
        match run.status:
            case 'completed':
                response = self.client.beta.threads.messages.list(thread_id = self.thread.id)
                return response.data[0].content[0].text.value, False
            case 'failed':
                return 'Request failed to process.', True
            case 'cancelled':
                return 'Request cancelled.', True
            case 'expired':
                return 'Request expired.', True
            case default:
                return f'Unknown status: {run.status}', True

    def check_markdown(self, res):
        if res.startswith("```") and res.endswith("```"):
            res = res[3:-3].strip()
            if res.startswith("json"):
                res = res[4:].strip()
        return res
        
    @commands.command(name='generate_gpt')
    async def generate(self, ctx, subtype='tavern', *, context=''):
        subtype = subtype.lower()

        # Create request based on subtype of generation
        # TODO: Clarify Cities (Districts?)
        # TODO: Clarify Location (Historic Landmarks? Is this needed?)
        # TODO: Finetune Bounty generation to better specify rewards.
        match subtype:
            case 'tavern':
                request = f'''
                    Generate a Tavern with 3 NPCs. {context}

                    Format the output as a list of 2 objects: The Tavern and the NPCs.
                    For the Tavern, format the output as a JSON object with the keys Name, Location, and Description.
                    For each NPC, format the output as a JSON object with the keys Name, Role, and Description.

                    Limit the Location value for the Tavern as the name of a City, Country, or Geographical Location.
                    '''
                table='locations'
            case 'npc':
                request = f'''
                    Generate a NPC, limiting the description to 2-3 sentences. {context}
                    
                    Format the output as a JSON object with the keys Name, Role, Location, and Description.
                    Limit the Location value for the NPC as the name of a City, Country, or Geographical Location.
                    '''
                table='npcs'
            case 'bounty':
                request = f'''
                    Generate a bounty. {context}

                    Format the output as a JSON object with the keys Quest, Recommended Level, and Description.
                    '''
                table = ''
            case 'city':
                if len(context) == 0:
                    await ctx.send(f'To generate a city, please provide context.')
                    return
                request = f'''
                    Generate a description and districts for the following city: {context}

                    Format the output as a JSON object with the keys Name, Location, Description, and (if applicable) Districts.
                    If Districts are applicable, the Districts object must be a list of tuples with the keys Name and Description.
                    Limit the Location value for the City as the name of a Country or Geographical Location.
                    '''
                table='cities'
            case 'location':
                if len(context) == 0:
                    await ctx.send(f'To generate a description for a location, please provide context.')
                    return
                request = f'''
                    Generate a description for the following locale: {context}

                    Format the output as a JSON object with the keys Name, Location, and Description.
                    Limit the Location value for the Tavern as the name of a Country.
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
    await client.add_cog(GPT(client))