import discord
from discord.ext import commands
import song as s
import player as p
from datetime import datetime


c1 = 0x47A7FF #positive
c2 = 0xFF3333 #negative

ffmpegopts = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}


class Music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.players = {}

    def init_player(self, ctx):
        if ctx.guild.id not in self.players:
            self.players[ctx.guild.id] = p.Player(ctx, self)
        return self.players[ctx.guild.id]
    
    def remove_player(self, guild_id):
        if guild_id in self.players:
            del self.players[guild_id]

    @commands.command(name='Play', aliases=['pl', 'p'], description="Play audio from the provided URL/keyword.")
    async def _play(self,ctx, *, url=None):
        if ctx.author.voice is None:
            await ctx.send(embed=discord.Embed(description=f"Please join a voice channel to use this command.", color=c2))        
            return
        
        if ctx.voice_client is None and ctx.author.voice is not None:
            voice_channel = ctx.author.voice.channel
            await voice_channel.connect()
            ctx.voice_client.stop()
        #Join a voice channel

        if ctx.voice_client.channel is not ctx.author.voice.channel:
            await ctx.send(embed=discord.Embed(description=f"I'm already in a voice channel.", color=c2))
            return
        
        player = self.init_player(ctx)
        player.update_ctx(ctx)
        
        loading_message = await ctx.send(embed=discord.Embed(description=f"Loading entry...", color=c1))

        try:
            song = s.Song(url)
        except:
            await loading_message.edit(embed=discord.Embed(description=f"Invalid keyword/link, please try again...", color=c2))
            return
        
        await player.add_song_to_queue(song)
        await loading_message.edit(embed=discord.Embed(description=f"**Queued:** [{song.title}]({song.videolink})   [{song.duration}]", color=c1))


    @commands.command(name='Queue', aliases=['q'], description="Shows the list of queued songs.")
    async def _queue(self, ctx, page=1):
        if not await self.command_availability_check(ctx):
            return

        player = self.players.get(ctx.guild.id)
        if not player:
            await ctx.send(embed=discord.Embed(description=f"I'm currently not in a voice channel, use the `play` command to get started.",color=c2))
            return

        if not player.now_playing:
            await ctx.send(embed=discord.Embed(description=f"Nothing is currently playing and the queue is empty.",color=c2))
            return

        queue = player.queue
        total_page = (len(queue) + 10 - 1) // 10
        if page <= 0 or page > total_page and len(queue) > 0:
            await ctx.send(embed=discord.Embed(description="Invalid page.",color=c2))
            return

        embed = discord.Embed(color=c1, title='**Now Playing:**')
        embed.description = f'🎵   {player.now_playing.title}        [{player.now_playing.duration}]({player.now_playing.videolink})\n'

        embed.add_field(name='', value='', inline=False)
        embed.add_field(name='', value='', inline=False)
        #add gap between now playing and queue
        
        if not queue:
            embed.add_field(name='Queue:', value='*(Empty queue)*', inline=False)
            footer = ''
            if player.loop_song:
                footer += 'Loop Song: ON'
            if player.loop_queue:
                footer += 'Loop Queue: ON'
            embed.set_footer(text=footer)
            await ctx.send(embed=embed)
            return
        
        queue_list = ""
        start = (page - 1) * 10
        end = min(start + 10, len(queue))
        for i in range(start, end):
            queue_list += f'\n{i+1})  {queue[i].title}        [{queue[i].duration}]({queue[i].videolink})'

        embed.add_field(name='Queue:', value=queue_list, inline=False)

        footer = f'Page {page}/{total_page}'
        if player.loop_song:
            footer += '  ●  Loop Song: ON'
        if player.loop_queue:
            footer += '  ●  Loop Queue: ON'
        embed.set_footer(text=footer)

        await ctx.send(embed=embed)

              
    @commands.command(name='Leave', aliases=['disconnect','dc'], description="Disconnect from the current voice channel.")
    async def _leave(self, ctx):
        if not await self.command_availability_check(ctx):
            return

        player = self.players.get(ctx.guild.id)
        if player:
            await player.disconnect()
            del self.players[ctx.guild.id]
        else:
            await ctx.send(embed=discord.Embed(description=f"I'm currently not in a voice channel, use the `play` command to get started.", color=c2))


    @commands.command(name='Pause', description="Pause the music.")
    async def _pause(self, ctx):
        if not await self.command_availability_check(ctx):
            return
    
        player = self.players.get(ctx.guild.id)
        if player:
            if not player.now_playing:
                await ctx.send(embed=discord.Embed(description=f"I cannot pause when nothing is playing.", color=c2))
                return
            
            if not player.is_paused:
                player.pause()
                
            await ctx.send(embed=discord.Embed(description=f"⏸ Music paused...", color=c1))
        else:
            await ctx.send(embed=discord.Embed(description=f"I'm currently not in a voice channel, use the `play` command to get started.", color=c2))


    @commands.command(name='Resume', description="Resume the music.")
    async def _resume(self, ctx):
        if not await self.command_availability_check(ctx):
            return
        
        player = self.players.get(ctx.guild.id)
        if player:
            if not player.now_playing:
                await ctx.send(embed=discord.Embed(description=f"I cannot resume when nothing is playing.", color=c2))
                return
            
            if player.is_paused:
                player.resume()

            await ctx.send(embed=discord.Embed(description=f"▶️ Resuming music...", color=c1))
        else:
            await ctx.send(embed=discord.Embed(description=f"I'm currently not in a voice channel, use the `play` command to get started.", color=c2))


    @commands.command(name='Skip', aliases=['next', 's'], description="Skip the current song.")
    async def _skip(self, ctx):
        if not await self.command_availability_check(ctx):
            return
        
        player = self.players.get(ctx.guild.id)
        if player:
            if not player.now_playing:
                await ctx.send(embed=discord.Embed(description=f"I cannot skip when nothing is playing.", color=c2))
                return
            
            await ctx.send(embed=discord.Embed(description=f"**Skipped:** [{player.now_playing.title}]({player.now_playing.videolink})", color=c1))

            await player.skip()
            if player.is_paused:
                player.resume()

        else:
            await ctx.send(embed=discord.Embed(description=f"I'm currently not in a voice channel, use the `play` command to get started.", color=c2))

    @commands.command(name='Remove', aliases=['rm','delete','dl'], description="Remove a song from the queue at the specified index. Use -1 to remove the last song in the queue.")
    async def _remove(self,ctx,index:int):
        if not await self.command_availability_check(ctx):
            return
        
        player = self.players.get(ctx.guild.id)
        if player:
            queue = player.queue
            if index > len(queue) or index == 0 or index < -1:
                await ctx.send(embed=discord.Embed(description=f"Invalid index.", color=c2))
                return
            
            # if index == 1:
            #     removed_song = player.now_playing
            #     await ctx.send(embed=discord.Embed(description=f"**Removed:** [{removed_song.title}]({removed_song.videolink})", color=c1))
            #     await player.skip()
            #     return
            if index == -1:
                # if len(queue) == 1:
                #     removed_song = player.now_playing
                #     await player.skip()
                # else:
                removed_song = queue.pop(-1)
                player.update_queue(queue)
            else:
                removed_song = queue.pop(index - 1)
                player.update_queue(queue)

            await ctx.send(embed=discord.Embed(description=f"**Removed:** [{removed_song.title}]({removed_song.videolink})", color=c1))
            
        else:
            await ctx.send(embed=discord.Embed(description=f"I'm currently not in a voice channel, use the `play` command to get started.", color=c2))

    @commands.command(name='Jump', aliases = ['j'], description="Jump to the song at the specified index. Use -1 to remove the last song in the queue.")
    async def _jump(self,ctx,index:int):
        if not await self.command_availability_check(ctx):
            return

        player = self.players.get(ctx.guild.id)
        if player:
            queue = player.queue()
            if index > len(queue) or index <= 0:
                await ctx.send(embed=discord.Embed(description=f"Invalid index.", color=c2))
                return
            
            if index == -1:
                target_song = queue.pop(-1)
            else:
                target_song = queue.pop(index - 1)
            queue.insert(0,target_song)
            player.update_queue(queue)

            if player.loop_song:
                player.now_playing = queue[0]

            await player.skip()

        else:
            await ctx.send(embed=discord.Embed(description=f"I'm currently not in a voice channel, use the `play` command to get started.", color=c2))

    @commands.command(name='LoopSong', aliases=['ls'], description="Enable/disable loop song.")
    async def _loopsong(self,ctx):
        if not await self.command_availability_check(ctx):
            return
        
        player = self.players.get(ctx.guild.id)
        if player:
            if player.loop_song:
                player.loop_song = False
                await ctx.send(embed=discord.Embed(description=f"Loop Song: **DISABLED**", color=c1))
            else:
                player.loop_song = True
                await ctx.send(embed=discord.Embed(description=f"Loop Song: **ENABLED**", color=c1))

            if player.loop_queue:
                player.loop_queue = False
        else:
            await ctx.send(embed=discord.Embed(description=f"I'm currently not in a voice channel, use the `play` command to get started.", color=c2))


    @commands.command(name='LoopQueue', aliases=['lq'], description="Enable/disable loop queue")
    async def _loopqueue(self,ctx):
        if not await self.command_availability_check(ctx):
            return
        
        player = self.players.get(ctx.guild.id)
        if player:
            if player.loop_queue:
                player.loop_queue = False
                await ctx.send(embed=discord.Embed(description=f"Loop Queue: **DISABLED**", color=c1))
            else:
                player.loop_queue = True
                await ctx.send(embed=discord.Embed(description=f"Loop Queue: **ENABLED**", color=c1))

            if player.loop_song:
                player.loop_song = False
        else:
            await ctx.send(embed=discord.Embed(description=f"I'm currently not in a voice channel, use the `play` command to get started.", color=c2))


    @commands.command(name='NowPlaying',aliases=['np'], description="Show the information about the song currently playing.")
    async def _songInfo(self,ctx):
        if not await self.command_availability_check(ctx):
            return
        
        player = self.players.get(ctx.guild.id)
        if player:
            if not player.now_playing:
                await ctx.send(embed=discord.Embed(description=f"Nothing is currently playing.", color=c2))
                return
            
            song = player.now_playing
        
            embed=discord.Embed(title=song.title,url=song.videolink, color=c1)
            try:
                embed.set_image(url = song.thumbnail)
                embed.add_field(name = 'Publisher:', value=song.uploader, inline=True)
                embed.add_field(name = 'Publish Date:', value=song.date, inline=True)
                embed.add_field(name = 'Duration:', value=song.duration,inline=True)
                embed.add_field(name = 'Views:', value=song.views,inline=True)
                embed.add_field(name = 'Likes:', value=song.likes,inline=True)
                embed.add_field(name = 'Dislikes:', value=song.dislikes,inline=True)
            except:
                pass
            await ctx.send(embed=embed)

        else:
            await ctx.send(embed=discord.Embed(description=f"I'm currently not in a voice channel, use the `play` command to get started.", color=c2))
        
    @commands.command(name='Ping', description="Shows the latency of the bot.")
    async def _ping(self,ctx):
        await ctx.send(embed=discord.Embed(description=f'__{int(self.client.latency*1000)}__ ms', color=c1))


    async def command_availability_check(self,ctx):
        if ctx.author.voice is None:
            await ctx.send(embed=discord.Embed(description=f"Please join a voice channel to use this command.", color=c2))
            return False

        if ctx.voice_client is None:
            await ctx.send(embed=discord.Embed(description=f"I'm currently not in a voice channel, use the `play` command to get started.", color=c2))
            return False

        if ctx.voice_client.channel is not ctx.author.voice.channel:
            await ctx.send(embed=discord.Embed(description=f"Please join the voice channel I'm currently in to use this command.", color=c2))
            return False
        
        return True



async def setup(client):
    await client.add_cog(Music(client))

