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

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!embed'):
        embed=discord.Embed(title="Sample Embed", url="https://realdrewdata.medium.com/", description="This is an embed that will show how to build an embed and the different components", color=0xFF5733)
        embed.set_footer(text="poll")
        await message.channel.send(embed=embed)

allowed_reacts = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
@client.event
async def on_reaction_add(reaction, user):
    msg = reaction.message
    if len(msg.embeds)>0:
        emb = msg.embeds[0]
        ft = emb.footer
        if ft.text.startswith('poll'):
            print('This is a poll')
            await msg.channel.send("got a reaction")
            if reaction.emoji not in allowed_reacts:
                print('invalid')
                await reaction.clear()
            else:
                print('valid emoji')

client.run(TOKEN)
