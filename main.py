import discord
from discord.ext import commands
import music
import help
import asyncio
import ctypes
from os import environ as env

TOKEN = env.get("BOT_TOKEN")

client = commands.Bot(command_prefix='.', case_insensitive=True, intents = discord.Intents.all())

cogs = [music]

client.help_command = help.Help()

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f".help"))  
    path = ctypes.util.find_library('opus')
    if not path:
        raise Exception("Opus not detected, please refer to README and install Opus before running the bot.")
    discord.opus.load_opus(path)

async def main():
    for i in range(len(cogs)):
        await cogs[i].setup(client)


asyncio.run(main())
client.run(TOKEN)
