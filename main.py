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

    opus_path = ctypes.util.find_library('opus')
    if not opus_path:
        raise RuntimeError("Opus library not detected. Please install Opus as per the README instructions.")
    
    try:
        discord.opus.load_opus(opus_path)
    except:
        raise RuntimeError("Failed to load Opus.")
    

async def main():
    for cog in cogs:
        await cog.setup(client)


asyncio.run(main())
client.run(TOKEN)
