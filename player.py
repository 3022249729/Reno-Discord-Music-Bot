import discord
from discord.ext import commands
import asyncio
import song as s
from os import environ as env

DISCONNECT_TIMEOUT = int(env.get("AUTO_DISCONNECT_TIMEOUT"))

ffmpegopts = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

c1 = 0x47A7FF #positive
c2 = 0xFF3333 #negative

class Player:
    def __init__(self, ctx, music_cog):
        self.ctx = ctx
        self.queue = []
        self.music_cog = music_cog
        self.now_playing = None
        self.loop_song = False
        self.loop_queue = False
        self.is_paused = False
        asyncio.create_task(self.auto_leave())

    def update_ctx(self,ctx):
        self.ctx = ctx

    def resume(self):
        self.ctx.voice_client.resume()
        self.is_paused = False

    def pause(self):
        self.ctx.voice_client.pause()
        self.is_paused = True

    def update_queue(self, queue):
        self.queue = queue

    async def skip(self):
        self.ctx.voice_client.stop()
        self.is_paused = False

    async def disconnect(self):
        self.ctx.voice_client.stop()
        self.queue = []
        self.now_playing = None
        await self.ctx.voice_client.disconnect()

    async def play_next(self):
        if self.loop_queue and self.now_playing:
            self.queue.append(self.now_playing)

        if not self.loop_song:
            self.now_playing = None 

        if self.queue and not self.loop_song:
            self.now_playing = self.queue.pop(0)
        
        if self.now_playing:
            await self.play(self.now_playing)


    async def play(self, song: s.Song):
        embed=discord.Embed(description=f"**Now playing:** [{song.title}]({song.videolink})   [{song.duration}]", color=c1)
        if self.loop_song:
            embed.set_footer(text="Loop Song: ON")
        if self.loop_queue:
            embed.set_footer(text="Loop Queue: ON")
        await self.ctx.send(embed=embed)

        try:
            source = discord.FFmpegPCMAudio(song.audio, **ffmpegopts)
            self.ctx.voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(), self.ctx.bot.loop))
        except:
            await self.ctx.send(embed=discord.Embed(description=f"An error occured while playing, please try again...", color=c2))

    async def auto_leave(self):
        idle_time = 0
        while True:
            if self.ctx.voice_client is None:
                self.music_cog.remove_player(self.ctx.guild.id)
                break
            if (not self.ctx.voice_client.is_paused() and not self.ctx.voice_client.is_playing()) or len(self.ctx.voice_client.channel.members) < 2:
                idle_time += 2
                if idle_time >= DISCONNECT_TIMEOUT:
                    await self.ctx.voice_client.disconnect()
                    await self.ctx.send(embed=discord.Embed(description=f"It looks like there's nothing I can play for you at the moment. I'm leaving the voice channel, call me back whenever you need!", color=c2))
                    self.music_cog.remove_player(self.ctx.guild.id)
                    break
            else:
                idle_time = 0
            await asyncio.sleep(2)


    async def add_song_to_queue(self, song):
        self.queue.append(song)
        if not self.now_playing:
            await self.play_next()

    def get_queue(self):
        queue = self.queue.copy()
        if self.now_playing:
            queue.insert(0, self.now_playing)
        return queue
    
            