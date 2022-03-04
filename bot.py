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
import random
import time

load_dotenv()

study_sessions = []
user_info = {}
study_tips = [
    '🎧 Try listening to some lofi music to help you focus in this time! Here is a playlist on Spotify: https://open.spotify.com/playlist/37i9dQZF1DX8Uebhn9wzrS?si=PXwNN9oaSea2KxBfAgrR-g',
    '⏱ For the next 30 minutes try using the time blocking method, here is a guide https://www.betterup.com/blog/time-blocking#:~:text=Time%20blocking%20is%20a%20planning,but%20when%20to%20do%20it', 
    '📚 Try using the Pomodoro technique for the next 30 minutes, here is a guide https://francescocirillo.com/pages/pomodoro-technique',
    '📑 Make a to-do list for what you want to accomplish in the next 30 minutes and see how much we can get done by the next check-in!',
    '🖥 Try playing this cafe video to focus in https://www.youtube.com/watch?v=VMAPTo7RVCo',
    '🧙‍♀️ Try transporting to study in Hogwarts for the next 30 minutes! https://www.youtube.com/watch?v=BQrxsyGTztM',
    '⛔ Take yourself offline for the next 30 minutes. Turn off your phone and silence incomming notifications',
    '🤓 Organize a prioritized to-do list based off of due dates to get ahead on your deadlines!',
    '💻 Try using Notion to organize your thoughts! https://www.notion.so/product'
    ]

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix='/', intents=intents)

TOKEN = os.getenv('DISCORD_TOKEN')


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print(discord.__version__)

# Schedules a study session
@client.command(name='schedule',
                help="Schedule a new study session. EX: /schedule 2022-02-23 5pm 1",
                brief="Schedules a study session.")
async def schedule_session(ctx, *args):
    study_session = parse_study_session_request(*args)
    study_sessions.append(study_session)
    await print_study_session_request_response(ctx, study_session)

# Starts a study session
@client.command(name='startsession',
                help="Starts the study session, follow with the session ID given upon scheduling. EX: /startsession 0",
                brief="Starts a study session.")
async def start_session(ctx, arg):
    # arg = session id
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.guild.me: discord.PermissionOverwrite(read_messages=True)
    }
    channel = await ctx.guild.create_text_channel(f'session-{arg}', overwrites=overwrites)

    await startsession.start(ctx, arg, channel)
    #channel_name = discord.utils.get(ctx.guild.channels, name=f'session-{arg}')
    await channel.send('Your session has ended now! Use /endsession to leave or feel free to stay on and keep working!')
    #await end_session(ctx, channel_name, channel)

# start session loop
@tasks.loop(seconds=120, count=1)
async def startsession(ctx, arg, channel):
    user_string = ''
    for user in study_sessions[int(arg)].users:
        user_string += f'<@{user.id}> '
        await channel.set_permissions(user, read_messages=True, send_messages=True)

    await channel.send(user_string + 'your study session is starting now!')

    # send initial check in message
    for user in study_sessions[int(arg)].users:
        member = ctx.guild.get_member(user.id)

        def check(msg):
            return msg.author == user and msg.channel.type is discord.ChannelType.private

        embed=discord.Embed(title=f'What is your goal for today\'s study session?',
            description=f'Respond with your goal by sending your goal for study session {arg}!',
            color=0xFF5733)
        await member.send(embed=embed)
        
        msg = await client.wait_for("message", check=check)
        user_info[user.id] = [msg.content, []]
        await member.send(f'Thanks! Head back to ' + client.get_channel(channel.id).mention)

    # send user goals
    await channel.send("Here are everyone's goals for study session " + arg + ":")
    for key, value in user_info.items():
        await channel.send(f'🔊 <@{key}>: {value[0]}')

    # Wait 10 seconds before sending the first check in
    await asyncio.sleep(10)
    send_checkin.start(ctx, arg, user_info, channel)

# send check ins
@tasks.loop(seconds=10, count=2)
async def send_checkin(ctx, arg, user_info, channel):
    # send checkin message 
    low_progress_flags = {}
    for user in study_sessions[int(arg)].users:
        def check(msg):
            return msg.author == user and msg.channel.type is discord.ChannelType.private

        member = ctx.guild.get_member(user.id)
        embed=discord.Embed(title=f'Progress check in!',
            description=f'Respond with your progress toward your goal on a scale from 1-5',
            color=0xFF5733)
        embed.set_footer(text=f'ratings')
        await member.send(embed=embed)

        msg = await client.wait_for("message", check=check)
        progress = (int(float(msg.content)))

        print(f'user id in checkin : {user.id}')

        user_info[user.id][1].append(progress)
        
        if (progress < 3):
            low_progress_flags[user.id] = True
        else:
            low_progress_flags[user.id] = False

        await member.send(f'Take a 5-minute break and then head back to <#{channel.id}>')

    await asyncio.sleep(5)  # for demo purposes. otherwise would be 5 * 60 seconds
    for user_id in low_progress_flags:
        length = len(user_info[user_id][1])
        if low_progress_flags[user_id] == True:
            await channel.send(f'<@{user_id}> rated a {user_info[user_id][1][length - 1]} - {study_tips[random.randrange(len(study_tips))]}')
        else:
            await channel.send(f'<@{user_id}> rated a {user_info[user_id][1][length - 1]} - Keep up the great work!')

def aggregate_user_trend(ratings):
    # non-decreasing
    if all(x<=y for x, y in zip(ratings, ratings[1:])):
        return 1

    # non-increasing
    if all(x>=y for x, y in zip(ratings, ratings[1:])):
        return -1

    # constant ratings
        return 0

@client.command(name='endsession',
                help="Ends the study session channel that the command is made in. EX: /endsession",
                brief="Ends a study session by closing the channel.")
async def end_session(ctx):
    for member in ctx.channel.members:
        print(f'id: {member}, {member.name}, {member.id}')
        if member.id in user_info.keys():
            trend = aggregate_user_trend(user_info[member.id][1])
            trend_description = ''
            if trend == 1:
                trend_description = 'more'
            elif trend == -1:
                trend_description = 'less'
            await ctx.channel.send(f'<@{member.id}> has become {trend_description} productive over this session!')
            if trend <= 0:
                await ctx.channel.send(f'Cheer {member} on! They weren\'t as productive as they wanted to be today')

    await asyncio.sleep(15)
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
