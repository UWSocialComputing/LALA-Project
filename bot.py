# bot.py
import os
from discord.ext import commands
import discord
from dotenv import load_dotenv

from StudySession import StudySession
import datetime

load_dotenv()

intents = discord.Intents.default()
intents.members = True

TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client(intents = intents)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print(discord.__version__)

# Triggers every time a message is received
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('/schedule'):
        study_session = parse_study_session_request(message)
        await print_study_session_request_response(message, study_session)

def parse_study_session_request(message):
    study_session_parse_string = message.content.split(' ')

    # Assumes date string is given in the format of YYYY-MM-DD
    study_date = study_session_parse_string[1]
    study_date = datetime.date.fromisoformat(study_date)

    # TODO: parse time correctly
    study_time = study_session_parse_string[2]

    # parse duration: either 1, 2, or 3 hours
    duration = study_session_parse_string[3]

    study_session = StudySession(study_date, study_time, duration)
    return study_session

async def print_study_session_request_response(message, study_session):
    await message.channel.send(f'{message.author} has requested a study session!')
    await message.channel.send(f'on {study_session.date} at {study_session.time} for {study_session.duration} hour')

# sends DM with instructions to users who join server
@client.event
async def on_member_join(member):
    await member.send('Welcome to the StudyCafe!\n\n' + 
    'To Schedule a Group Study Session use the /schedule command followed by the date [year-monthy-date] the time in PST followed by am/pm and the duration [1,2,3 hr]\n' +
    'Example: /schedule 2022-02-23 5pm 1\n\n' +
    'Once your session is scheduled other members of this server can “RSVP” to the session by using the reactions ✅ or ❌\n' +
    'When the study session begins users who reacted ✅  will enter a channel to moderate the session for the elapsed time.\n' +
    'Prompts will help guide your session and promote efficient and effective study time.\n\n' +
    'Happy studying!')
    
client.run(TOKEN)