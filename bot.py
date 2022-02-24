# bot.py
import os
from discord.ext import commands
import discord
from dotenv import load_dotenv
from discord.ext import commands
from StudySession import StudySession
import datetime

load_dotenv()

study_session_users = []

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix='/', intents=intents)

TOKEN = os.getenv('DISCORD_TOKEN')


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print(discord.__version__)

@client.command(name='schedule')
async def schedule_session(ctx, *args):
    study_session = parse_study_session_request(*args)
    await print_study_session_request_response(ctx, study_session)

@client.command(name='startsession')
async def start_session(ctx, arg):
    channel = await ctx.guild.create_text_channel(arg)
    user_string = ''
    for user in study_session_users:
        user_string += f'<@{user.id}> '
    await channel.send(user_string + 'your study session is starting now!')
  

def parse_study_session_request(*message):
    print(*message)

    # Assumes date string is given in the format of YYYY-MM-DD
    study_date = message[0]
    study_date = datetime.date.fromisoformat(study_date)

    # TODO: parse time correctly
    study_time = message[1]

    # parse duration: either 1, 2, or 3 hours
    duration = message[2]

    study_session = StudySession(study_date, study_time, duration)
    return study_session


# TODO: Method to start the study session
def start_study_session():
    return

async def print_study_session_request_response(message, study_session):
    # TODO: Find a way to format the message so it can @channel
    embed=discord.Embed(title=f'{message.author} has requested a study session on {study_session.date} at {study_session.time} for {study_session.duration} hour',
                         description='Please use the emojis to accept or reject this study session!',
                        color=0xFF5733)
    embed.set_footer(text="schedule poll")
    await message.channel.send(embed=embed)
   

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

@client.event
async def on_reaction_add(reaction, user):
    msg = reaction.message
    if len(msg.embeds)>0:
        emb = msg.embeds[0]
        ft = emb.footer
        if ft.text.startswith('schedule poll'):
            if reaction.emoji == '✅':
                study_session_users.append(user)
                print(user)

    
client.run(TOKEN)