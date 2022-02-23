# bot.py
import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print(discord.__version__)

@client.event
async def on_member_join(member):
    await member.send("Welcome! TEST")
    
client.run(TOKEN)
