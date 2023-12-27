import asyncio
import discord
import os
import time

from discord.ext import commands
from openai import OpenAI

class GPT(commands.Cog, name='gpt'):
    def __init__(self, bot):
        self.bot = bot
        
        # OpenAI setup
        self.client = OpenAI()
        self.assistant = self.client.beta.assistants.retrieve(os.environ['CODM'])
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
        
        
    @commands.command(name='generate')
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
                    
                    The output must be in the following format:
                    
                    Tavern Name: **[Name]**
                    [Description]

                    For each NPC, use the following format
                    
                    NPC: [Name], [Role, if any] ([Race] [Class])
                    - [Description]
                    '''
            case 'npc':
                request = f'''
                    Generate a NPC, limiting the description to 2-3 sentences. {context}
                    
                    The output must be in the following format:
                    
                    NPC: [Name], [Role, if any] ([Race] [Class])
                    - [Description]
                    '''
            case 'bounty':
                request = f'''
                    Generate a bounty. {context}

                    The output must be in the following format:

                    Quest: [Name]
                    - Reward: [Reward]
                    - [Description]
                    '''
            case 'city':
                if len(context) == 0:
                    await ctx.send(f'To generate a city, please provide context.')
                    return
                request = f'''
                    Generate districts for the following city: {context}

                    The output must be in the following format:

                    District 1: [Name]
                    - [Description]
                    District 2: [Name]
                    - [Description]
                    ...
                    '''
            case 'location':
                if len(context) == 0:
                    await ctx.send(f'To generate a description for a location, please provide context.')
                    return
                request = f'''
                    Generate a description for the following locale: {context}

                    The output must be in the following format:

                    [Name]
                    - [Description]
                    '''
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
        # If no error, check if output is longer than what Discord allows.
        # Use premade formats to react accordingly
        elif len(res) > 2000:
            sections = res.split('\n\n')
            for section in sections:
                await ctx.send(section)
        else:
            await ctx.send(res)
            
async def setup(client) -> None:
    await client.add_cog(GPT(client))