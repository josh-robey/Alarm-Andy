# Discord bot to ping friends every 1 minute they're late
import os
import discord
import asyncio
import timeformat

from dotenv import load_dotenv
from discord.ext import commands

# loads token from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='/', intents=intents, help_command=commands.DefaultHelpCommand())

# users that have confirmed to join or have canceled will appear here in absent or agreed
absent = {}
agreed = {}


@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if not message.guild:
        try:
            if message.content.lower() == "n" and message.author.id not in absent:
                await message.channel.send("Wtf man")
                absent[message.author.id] = True

            elif message.content.lower() == "n" and message.author.id in absent or message.author.id in agreed:
                await message.channel.send("You have already gave an answer.")

            elif message.content.lower() == "y" and message.author.id not in agreed and message.author.id not in absent:
                await message.channel.send("Lets GOOO, I'm gonna like ping you when it's time and stuff")
                agreed[message.author.id] = True

            elif message.content.lower() == "y" and message.author.id in agreed or message.author.id in absent:
                await message.channel.send("You have already gave an answer.")

        except discord.errors.Forbidden:
            pass
    else:
        pass

    await client.process_commands(message)


@client.command(name='sesh', help='Time of sesh(in EST), mentioned users. '
                                  'Ex: /sesh 15:30 @Zombie @Gohan')
async def sesh(ctx, time, users: commands.Greedy[discord.User]):
    time = time.split(":")
    names = []
    inviter = ctx.message.author.display_name
    print(f"invite command sent from {ctx.message.author.display_name} of {ctx.message.guild}")
    # creates list of users (purely for display)
    for i in users:
        names = names + [i.display_name]
        asyncio.create_task(late_dm(ctx, time, i, inviter))
    try:
        if not users:
            await ctx.channel.send("Please enter any amount of valid users.")
            return
        await ctx.channel.send(f"You have sent an invite to {', '.join(names)} for a sesh starting at "
                               f"{time[0]}:{time[1]} EST.")
    except Exception as e:
        print(e)
        await ctx.channel.send(f"{e}. Please enter a valid time.")
        return


@client.event
async def late_dm(ctx, time, i, inviter):
    minutes_late = 0
    count = 0
    minutes_interval = 5

    clear_dicts(i)

    await i.create_dm()
    message = await i.dm_channel.send(
        f"{i.display_name}, you've been invited by {inviter} to hang out at {time[0]}:{time[1]} EST in "
        f"{ctx.message.guild}! Let them know if you'll make it by replying 'Y' to confirm or 'N' to decline.")
    message_id = message.id
    print(f"invite sent to {i.display_name}")

    while not i.voice and i.id not in absent:
        try:
            await asyncio.sleep(0.01)
            if count == 0 and i.id in agreed:
                await ctx.channel.send(f"{i.display_name} has agreed to join the sesh.")
                print(f"{i.display_name} confirmed invite")
                count = 1

            if not i.voice and i.id not in absent and i.id in agreed:
                if timeformat.update_time()[0] >= int(time[0]) and timeformat.update_time()[1] >= int(time[1]):
                    await asyncio.sleep(60 * minutes_interval)
                    minutes_late += minutes_interval

                    await i.create_dm()
                    await i.dm_channel.send(
                        f"{i.display_name}, you are {minutes_late} minute late! Reply with 'N' to cancel."
                        if minutes_late == 1 else f"{i.display_name},"
                                                  f" you are {minutes_late} minutes late! Reply with 'N' to cancel.")
                    print(f"{minutes_late} min late message sent to {i.display_name}")

            elif i.id in absent and count == 0:
                await ctx.channel.send(f"{i.display_name} will not be joining us.")
                print(f"{i.display_name} denied invite")
                break
            elif timeformat.update_time()[0] == int(time[0]) and timeformat.update_time()[1] == int(
                    time[1]) and i.id not in absent and i.id not in agreed and count == 0:
                await i.create_dm()
                await i.dm_channel.send(f"Just a reminder that there's a sesh in "
                                        f"{ctx.message.guild} right now!")
                count = 1

        except Exception as e:
            print(e)

    clear_dicts(i)


def clear_dicts(i):
    if i.id in absent:
        del absent[i.id]
    if i.id in agreed:
        del agreed[i.id]


client.run(TOKEN)
