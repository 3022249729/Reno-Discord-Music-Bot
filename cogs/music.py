import discord
from discord.ext import commands
from os import environ as env
from utils.downloader import Downloader
from utils.player import Player
from utils.lyrics import get_lyrics_genius

GENIUS_ACCESS_TOKEN = env.get("GENIUS_ACCESS_TOKEN")

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
            self.players[ctx.guild.id] = Player(ctx, self)
        return self.players[ctx.guild.id]
    
    def remove_player(self, guild_id):
        if guild_id in self.players:
            del self.players[guild_id]

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
    
    async def get_player_and_check(self, ctx):
        if not await self.command_availability_check(ctx):
            return None
        
        player = self.players.get(ctx.guild.id)
        if not player:
            await ctx.send(embed=discord.Embed(description=f"I'm not in a voice channel, use the `play` command to get started.", color=c2))
            return None
        
        player.update_ctx(ctx)
        return player


    @commands.command(name='Play', aliases=['pl', 'p'], description="Play audio from the provided URL/keyword.")
    async def _play(self,ctx, *, url:str=None):
        if ctx.author.voice is None:
            await ctx.send(embed=discord.Embed(description=f"Please join a voice channel to use this command.", color=c2))        
            return
        
        if ctx.voice_client is None:
            voice_channel = ctx.author.voice.channel
            await voice_channel.connect()
            ctx.voice_client.stop()
        #Join a voice channel
        elif ctx.voice_client.channel is not ctx.author.voice.channel:
            await ctx.send(embed=discord.Embed(description=f"I'm already in a voice channel.", color=c2))
            return
        
        player = self.init_player(ctx)
        player.update_ctx(ctx)

        if not url:
            if player.is_paused:
                player.resume()
                await ctx.send(embed=discord.Embed(description=f"▶️ Resuming music...", color=c1))
            else:
                await ctx.send(embed=discord.Embed(description=f"Please provide an URL or keyword.", color=c2))        
            return   
        
        async with ctx.typing():
            downloader = Downloader()
            songs = downloader.extract_flat(url)

        if not songs:
            await ctx.send(embed=discord.Embed(description=f"Invalid keyword/link, please try again...", color=c2))
            return

        if len(songs) > 1:
            await ctx.send(embed=discord.Embed(description=f"Queued `{len(songs)}` entries from playlist.", color=c1))
        else:
            await ctx.send(embed=discord.Embed(description=f"Queued: [{songs[0].title}]({songs[0].videolink})   [{songs[0].duration}]", color=c1))
    
        await player.add_songs_to_queue(songs)



    @commands.command(name='Queue', aliases=['q'], description="Shows the list of queued songs.")
    async def _queue(self, ctx, page:int=1):
        player = await self.get_player_and_check(ctx)
        if not player:
            return

        if not player.now_playing:
            await ctx.send(embed=discord.Embed(description=f"Nothing is currently playing and the queue is empty.",color=c2))
            return
        
        queue = player.queue

        embed = discord.Embed(color=c1, title='**🎵 Now Playing:**')
        embed.description = f'{player.now_playing.title}   [[{player.now_playing.duration}]({player.now_playing.videolink})]\n'

        embed.description += "\n### Queue:"
        embed.add_field(name='', value='', inline=False)
        embed.add_field(name='', value='', inline=False)
        #add gap between now playing and queue
        
        if not queue:
            embed.add_field(name='Queue:', value='*(Empty queue)*', inline=False)
            footer = ''
            if player.loop_song:
                footer += 'Loop Song: ON'
            elif player.loop_queue:
                footer += 'Loop Queue: ON'
            embed.set_footer(text=footer)
            await ctx.send(embed=embed)
            return
        
        try:
            songs, total_pages = player.get_queue_page(page)
        except ValueError:
            await ctx.send(embed=discord.Embed(description="Invalid page.", color=c2))
            return
              
        queue_list = ""

        for i in range(len(songs)):
            title = songs[i].title
            if len(title) > 100:
                title = str(title[:100]) + "..."

            queue_list += f'\n{((page-1)*10)+i+1})  {title}   [[{songs[i].duration}]({songs[i].videolink})]'

        embed.description += queue_list

        footer = f'Page {page}/{total_pages}'
        if player.loop_song:
            footer += '  ●  Loop Song: ON'
        elif player.loop_queue:
            footer += '  ●  Loop Queue: ON'
        embed.set_footer(text=footer)
        
        await ctx.send(embed=embed)

    @_queue.error
    async def _queue_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(embed=discord.Embed(description="Invalid page number, please provide a positive integer.",color=c2))
              

    @commands.command(name='Clear', description="Clear all the songs in the queue.")
    async def _clear(self, ctx):
        player = await self.get_player_and_check(ctx)
        if not player:
            return
        
        player.clear_queue()
        await ctx.send(embed=discord.Embed(description="Queue cleared.",color=c2))


    @commands.command(name='Shuffle', description="Shuffle the queue.")
    async def _shuffle(self, ctx):
        player = await self.get_player_and_check(ctx)
        if not player:
            return
        
        try:
            player.shuffle_queue()
            await self._queue(ctx, page=1)
        except ValueError:
            await ctx.send(embed=discord.Embed(description=f"Cannot shuffle an empty queue.", color=c2))



    @commands.command(name='Leave', aliases=['disconnect','dc'], description="Disconnect from the current voice channel.")
    async def _leave(self, ctx):
        player = await self.get_player_and_check(ctx)
        if not player:
            return
        
        await player.disconnect()
        del self.players[ctx.guild.id]
        

    @commands.command(name='Pause', description="Pause the music.")
    async def _pause(self, ctx):
        player = await self.get_player_and_check(ctx)
        if not player:
            return
    
        if not player.now_playing:
            await ctx.send(embed=discord.Embed(description=f"I cannot pause when nothing is playing.", color=c2))
            return
        
        if not player.is_paused:
            player.pause()
            
        await ctx.send(embed=discord.Embed(description=f"⏸ Music paused...", color=c1))
       

    @commands.command(name='Resume', description="Resume the music.")
    async def _resume(self, ctx):
        player = await self.get_player_and_check(ctx)
        if not player:
            return
        
        if not player.now_playing:
            await ctx.send(embed=discord.Embed(description=f"I cannot resume when nothing is playing.", color=c2))
            return
        
        if player.is_paused:
            player.resume()

        await ctx.send(embed=discord.Embed(description=f"▶️ Resuming music...", color=c1))
    

    @commands.command(name='Skip', aliases=['next', 's'], description="Skip the current song.")
    async def _skip(self, ctx):
        player = await self.get_player_and_check(ctx)
        if not player:
            return
        
        if not player.now_playing:
            await ctx.send(embed=discord.Embed(description=f"I cannot skip when nothing is playing.", color=c2))
            return
        
        player.skip()
        await ctx.send(embed=discord.Embed(description=f"**Skipped:** [{player.now_playing.title}]({player.now_playing.videolink})", color=c1))
        
        if player.is_paused:
            player.resume()

       
    @commands.command(name='Remove', aliases=['rm', 'dl'], description="Remove a song from the queue at the specified index. Use -1 to remove the last song in the queue.")
    async def _remove(self,ctx,index:int=None):
        player = await self.get_player_and_check(ctx)
        if not player:
            return
        
        if not index:
            await ctx.send(embed=discord.Embed(description=f"Missing index.", color=c2))
            return
        
        try:
            removed_song = player.remove(index)
        except ValueError:
            await ctx.send(embed=discord.Embed(description=f"Invalid index.", color=c2))
            return

        await ctx.send(embed=discord.Embed(description=f"**Removed:** [{removed_song.title}]({removed_song.videolink})", color=c1))
        
    @_remove.error
    async def _remove_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(embed=discord.Embed(description="Invalid index.",color=c2))


    @commands.command(name='Jump', aliases = ['j'], description="Jump to the song at the specified index. Use -1 to remove the last song in the queue.")
    async def _jump(self,ctx,index:int=None):
        player = await self.get_player_and_check(ctx)
        if not player:
            return
        
        if not index:
            await ctx.send(embed=discord.Embed(description=f"Missing index.", color=c2))
            return
        
        try:
            player.jump(index)
        except ValueError:
            await ctx.send(embed=discord.Embed(description=f"Invalid index.", color=c2))
            return
        
        player.skip()

    @_jump.error
    async def _jump_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(embed=discord.Embed(description="Invalid index.",color=c2))


    @commands.command(name='LoopSong', aliases=['ls'], description="Enable/disable loop song.")
    async def _loopsong(self,ctx):
        player = await self.get_player_and_check(ctx)
        if not player:
            return
        
        is_enabled = player.set_loop_song()

        status = "ENABLED" if is_enabled else "DISABLED"
        await ctx.send(embed=discord.Embed(description=f"Loop Song: **{status}**", color=c1))
        

    @commands.command(name='LoopQueue', aliases=['lq'], description="Enable/disable loop queue")
    async def _loopqueue(self,ctx):
        player = await self.get_player_and_check(ctx)
        if not player:
            return
        
        is_enabled = player.set_loop_queue()

        status = "ENABLED" if is_enabled else "DISABLED"
        await ctx.send(embed=discord.Embed(description=f"Loop Queue: **{status}**", color=c1))
        

    @commands.command(name='NowPlaying', aliases=['np'], description="Show the information about the song currently playing.")
    async def _songInfo(self,ctx):
        player = await self.get_player_and_check(ctx)
        if not player:
            return
        
        if not player.now_playing:
            await ctx.send(embed=discord.Embed(description=f"Nothing is currently playing, please add a song using `play` before using this command.", color=c2))
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
            
        
    @commands.command(name='Lyrics', description="Show the lyrics of the song currently playing.")
    async def _lyrics(self,ctx):
        player = await self.get_player_and_check(ctx)
        if not player:
            return
        
        if not player.now_playing:
            await ctx.send(embed=discord.Embed(description=f"Nothing is currently playing, please add a song using `play` before using this command.", color=c2))
            return
        
        song_data, lyrics = get_lyrics_genius(self.now_playing)
        if not lyrics:
            await ctx.send(embed=discord.Embed(description=f"Please join a voice channel to use this command.", color=c2))
            return

        embed=discord.Embed(color=c1)
        try:
            embed.title = song_data['full_title']
            embed.set_thumbnail(url=song_data['song_art_image_url'])
            embed.description = lyrics.strip()
        except:
            pass

        await ctx.send(embed=embed)


    @commands.command(name='Ping', description="Show the latency of the bot.")
    async def _ping(self,ctx):
        await ctx.send(embed=discord.Embed(description=f'__{int(self.client.latency*1000)}__ ms', color=c1))


async def setup(client):
    await client.add_cog(Music(client))
