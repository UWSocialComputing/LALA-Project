# bot.py
import os
from discord.ext import commands, tasks
import discord
from dotenv import load_dotenv
from discord.ext import commands
from StudySession import StudySession
import datetime
import asyncio
import nest_asyncio
from unsync import unsync

load_dotenv()

# study_session_users = []
study_sessions = []

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix='/', intents=intents)

TOKEN = os.getenv('DISCORD_TOKEN')


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print(discord.__version__)

@client.command(name='schedule',
                help="Schedule a new study session. EX: /schedule 2022-02-23 5pm 1",
                brief="Schedules a study session." )
async def schedule_session(ctx, *args):
    study_session = parse_study_session_request(*args)
    study_sessions.append(study_session)
    await print_study_session_request_response(ctx, study_session)

@client.command(name='startsession',
                help="Starts the study session, follow with the session ID given upon scheduling. EX: /startsession 0",
                brief="Starts a study session." )
async def start_session(ctx, arg):
    # arg = session id
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.guild.me: discord.PermissionOverwrite(read_messages=True)
    }

    channel = await ctx.guild.create_text_channel(f'session-{arg}', overwrites=overwrites)
    user_string = ''
    for user in study_sessions[int(arg)].users:
        user_string += f'<@{user.id}> '
        await channel.set_permissions(user, read_messages=True, send_messages=True)

    await channel.send(user_string + 'your study session is starting now!')
    # TODO: begin internal timer that would go off close to the end of the study session

    user_info = {}
    # send initial check in message
    for user in study_sessions[int(arg)].users:
        member = ctx.guild.get_member(user.id)

        def check(msg):
            return msg.author == user and msg.channel.type is discord.ChannelType.private

        await member.send(f'What is your goal for today\'s study session?' + 
        '\nRespond with your goal by sending your goal for study session ' + arg + '!')
        
        msg = await client.wait_for("message", check=check)
        user_info[user.id] = [msg.content, []]
        await member.send(f'Thanks! Head back to ' + client.get_channel(channel.id).mention)

    # send user goals
    await channel.send("Here are everyone's goals for study session " + arg + ":")
    for key, value in user_info.items():
        await channel.send(f'🔊 <@{key}>' + ": " + value[0])

    send_checkin.start(ctx, arg, user_info)

@tasks.loop(seconds=30, count=2)
async def send_checkin(ctx, arg, user_info):
    # send checkin message 
    for user in study_sessions[int(arg)].users:
        member = ctx.guild.get_member(user.id)
        await member.send('Respond with your progress toward your goal on a scale from 1-5:')
        msg = await client.wait_for("message")
        user_info[user.id][1].append((int(float(msg.content))))
        await member.send('Take a 5-minute break and then head back to the study channel!')
#TODO: recommend new study method if rating in under 3

@client.command(name='endsession')
async def end_session(ctx):
    await ctx.channel.delete()
   
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

async def print_study_session_request_response(message, study_session):
    # TODO: Find a way to format the message so it can @channel
    embed=discord.Embed(title=f'{message.author} has requested a study session on {study_session.date} at {study_session.time} for {study_session.duration} hour',
                         description='Please use the emojis to accept or reject this study session!',
                        color=0xFF5733)
    embed.set_footer(text=f'session id: {study_session.id}')
    
    embedded_msg = await message.channel.send(embed=embed)
    await embedded_msg.add_reaction('✅')
    await embedded_msg.add_reaction('❌')
   

# sends DM with instructions to users who join server
@client.event
async def on_member_join(member):
    await member.send('👋 Welcome to the StudyCafe!\n') 
    await member.send('📅 To schedule a group session use the /schedule command followed by the date [year-month-date] the time in PT followed by am/pm and the duration [1,2,3 hr]\n' +
    '🆕 Example: /schedule 2022-02-23 5pm 1')
    await member.send('🔜 Once your session is scheduled other members of this server can “RSVP” to the session by using the reactions ✅ or ❌\n')
    await member.send('ℹ️ Use /help to see additional commands :)\n')
    await member.send('👨‍💻 Happy studying!')

@client.event
async def on_reaction_add(reaction, user):
    msg = reaction.message
    if user == client.user:
        return

    if len(msg.embeds)>0:
        emb = msg.embeds[0]
        ft = emb.footer
        if ft.text.startswith('session id'):
            session_id = ft.text[12:]
            if reaction.emoji == '✅':
                study_sessions[int(session_id)].users.append(user)
            if reaction.emoji not in ['✅','❌']:
                await reaction.clear()
    

client.run(TOKEN)
