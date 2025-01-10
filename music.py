import discord
from discord.ext import commands
import requests
import re
from bs4 import BeautifulSoup
from os import environ as env
import song as s
import player as p

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
            self.players[ctx.guild.id] = p.Player(ctx, self)
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
    
    def search_song_genius(self, song_title, access_token):
        search_url = "https://api.genius.com/search"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        params = {
            "q": song_title
        }
        
        response = requests.get(search_url, headers=headers, params=params)
        json_data = response.json()
        
        if json_data['response']['hits']:
            song_data = json_data['response']['hits'][0]['result']
            return song_data
        else:
            return None
        
    def get_lyrics_text_genius(self, lyrics_divs):
        lyrics = ""

        for div in lyrics_divs:
            if div is None:
                continue
            
            div_str = str(div)
            div_str = div_str.replace("<br/>", "\n").replace("<br>", "\n")

            soup = BeautifulSoup(div_str, 'html.parser')

            text = soup.get_text()
            
            if re.match(r'\[.*\]', text):
                lyrics += '\n' + text
            else:
                if '<i>' in div_str or '<b>' in div_str:
                    lyrics += text
                else:
                    lyrics += '\n' + text
        
        return lyrics


    @commands.command(name='Play', aliases=['pl', 'p'], description="Play audio from the provided URL/keyword.")
    async def _play(self,ctx, *, url:str=None):
        if ctx.author.voice is None:
            await ctx.send(embed=discord.Embed(description=f"Please join a voice channel to use this command.", color=c2))        
            return
        
        if not url:
            if player.is_paused:
                player.resume()
                await ctx.send(embed=discord.Embed(description=f"▶️ Resuming music...", color=c1))
            else:
                await ctx.send(embed=discord.Embed(description=f"Please provide an URL or keyword.", color=c2))        
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
        
        loading_message = await ctx.send(embed=discord.Embed(description=f"Loading entry...", color=c1))

        try:
            song = s.Song(url)
        except:
            await loading_message.edit(embed=discord.Embed(description=f"Invalid keyword/link, please try again...", color=c2))
            return
        
        await player.add_song_to_queue(song)
        await loading_message.edit(embed=discord.Embed(description=f"**Queued:** [{song.title}]({song.videolink})   [{song.duration}]", color=c1))


    @commands.command(name='Queue', aliases=['q'], description="Show the list of queued songs.")
    async def _queue(self, ctx, page:int=1):
        if not await self.command_availability_check(ctx):
            return

        player = self.players.get(ctx.guild.id)
        if not player:
            await ctx.send(embed=discord.Embed(description=f"I'm not in a voice channel, use the `play` command to get started.", color=c2))
            return

        if not player.now_playing:
            await ctx.send(embed=discord.Embed(description=f"Nothing is currently playing and the queue is empty.",color=c2))
            return
        
        queue = player.queue

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
        
        try:
            songs, total_pages = player.get_queue_page(page)
        except ValueError:
            await ctx.send(embed=discord.Embed(description="Invalid page.", color=c2))
            return
              
        queue_list = ""

        for i in range(len(songs)):
            queue_list += f'\n{i+1})  {songs[i].title}        [{songs[i].duration}]({songs[i].videolink})'

        embed.add_field(name='**Queue**:', value=queue_list, inline=False)

        footer = f'Page {page}/{total_pages}'
        if player.loop_song:
            footer += '  ●  Loop Song: ON'
        if player.loop_queue:
            footer += '  ●  Loop Queue: ON'
        embed.set_footer(text=footer)

        await ctx.send(embed=embed)

    @_queue.error
    async def _queue_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(embed=discord.Embed(description="Invalid page number, please provide a positive integer.",color=c2))
              

    @commands.command(name='Shuffle', description="Shuffle the queue.")
    async def _shuffle(self, ctx):
        if not await self.command_availability_check(ctx):
            return

        player = self.players.get(ctx.guild.id)
        if not player:
            await ctx.send(embed=discord.Embed(description=f"I'm not in a voice channel.", color=c2))
            return
        
        try:
            player.shuffle_queue()
            await self._queue(ctx, page=1)
        except ValueError:
            await ctx.send(embed=discord.Embed(description=f"Cannot shuffle an empty queue.", color=c2))



    @commands.command(name='Leave', aliases=['disconnect','dc'], description="Disconnect from the current voice channel.")
    async def _leave(self, ctx):
        if not await self.command_availability_check(ctx):
            return

        player = self.players.get(ctx.guild.id)
        if not player:
            await ctx.send(embed=discord.Embed(description=f"I'm not in a voice channel.", color=c2))
            return
        
        await player.disconnect()
        del self.players[ctx.guild.id]
        

    @commands.command(name='Pause', description="Pause the music.")
    async def _pause(self, ctx):
        if not await self.command_availability_check(ctx):
            return
    
        player = self.players.get(ctx.guild.id)
        if not player:
            await ctx.send(embed=discord.Embed(description=f"I'm not in a voice channel, use the `play` command to get started.", color=c2))
            return
        
        if not player.now_playing:
            await ctx.send(embed=discord.Embed(description=f"I cannot pause when nothing is playing.", color=c2))
            return
        
        if not player.is_paused:
            player.pause()
            
        await ctx.send(embed=discord.Embed(description=f"⏸ Music paused...", color=c1))
       

    @commands.command(name='Resume', description="Resume the music.")
    async def _resume(self, ctx):
        if not await self.command_availability_check(ctx):
            return
        
        player = self.players.get(ctx.guild.id)
        if not player:
            await ctx.send(embed=discord.Embed(description=f"I'm not in a voice channel, use the `play` command to get started.", color=c2))
            return
        
        if not player.now_playing:
            await ctx.send(embed=discord.Embed(description=f"I cannot resume when nothing is playing.", color=c2))
            return
        
        if player.is_paused:
            player.resume()

        await ctx.send(embed=discord.Embed(description=f"▶️ Resuming music...", color=c1))
    

    @commands.command(name='Skip', aliases=['next', 's'], description="Skip the current song.")
    async def _skip(self, ctx):
        if not await self.command_availability_check(ctx):
            return
        
        player = self.players.get(ctx.guild.id)
        if not player:
            await ctx.send(embed=discord.Embed(description=f"I'm not in a voice channel, use the `play` command to get started.", color=c2))
            return
        
        if not player.now_playing:
            await ctx.send(embed=discord.Embed(description=f"I cannot skip when nothing is playing.", color=c2))
            return
        
        player.skip()
        await ctx.send(embed=discord.Embed(description=f"**Skipped:** [{player.now_playing.title}]({player.now_playing.videolink})", color=c1))
        
        if player.is_paused:
            player.resume()

       
    @commands.command(name='Remove', aliases=['rm', 'dl'], description="Remove a song from the queue at the specified index. Use -1 to remove the last song in the queue.")
    async def _remove(self,ctx,index:int):
        if not await self.command_availability_check(ctx):
            return
        
        player = self.players.get(ctx.guild.id)
        if not player:
            await ctx.send(embed=discord.Embed(description=f"I'm not in a voice channel, use the `play` command to get started.", color=c2))
            return
        
        try:
            removed_song = player.remove(index)
        except ValueError:
            await ctx.send(embed=discord.Embed(description=f"Invalid index.", color=c2))
            return

        await ctx.send(embed=discord.Embed(description=f"**Removed:** [{removed_song.title}]({removed_song.videolink})", color=c1))
            
        
    @_queue.error
    async def _remove_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(embed=discord.Embed(description="Invalid index.",color=c2))


    @commands.command(name='Jump', aliases = ['j'], description="Jump to the song at the specified index. Use -1 to remove the last song in the queue.")
    async def _jump(self,ctx,index:int):
        if not await self.command_availability_check(ctx):
            return

        player = self.players.get(ctx.guild.id)
        if not player:
            await ctx.send(embed=discord.Embed(description=f"I'm not in a voice channel, use the `play` command to get started.", color=c2))
            return
        
        try:
            player.jump(index)
            await player.skip()
        except ValueError:
            await ctx.send(embed=discord.Embed(description=f"Invalid index.", color=c2))
            return


    @_jump.error
    async def _jump_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(embed=discord.Embed(description="Invalid index.",color=c2))


    @commands.command(name='LoopSong', aliases=['ls'], description="Enable/disable loop song.")
    async def _loopsong(self,ctx):
        if not await self.command_availability_check(ctx):
            return
        
        player = self.players.get(ctx.guild.id)
        if not player:
            await ctx.send(embed=discord.Embed(description=f"I'm not in a voice channel, use the `play` command to get started.", color=c2))
            return
        
        player.set_loop_song()

        if player.loop_song:
            await ctx.send(embed=discord.Embed(description=f"Loop Song: **DISABLED**", color=c1))
        else:
            await ctx.send(embed=discord.Embed(description=f"Loop Song: **ENABLED**", color=c1))
        

    @commands.command(name='LoopQueue', aliases=['lq'], description="Enable/disable loop queue")
    async def _loopqueue(self,ctx):
        if not await self.command_availability_check(ctx):
            return
        
        player = self.players.get(ctx.guild.id)
        if not player:
            await ctx.send(embed=discord.Embed(description=f"I'm not in a voice channel, use the `play` command to get started.", color=c2))
            return
        
        player.set_loop_queue()
        
        if player.loop_queue:
            await ctx.send(embed=discord.Embed(description=f"Loop Queue: **DISABLED**", color=c1))
        else:
            await ctx.send(embed=discord.Embed(description=f"Loop Queue: **ENABLED**", color=c1))
        

    @commands.command(name='NowPlaying', aliases=['np'], description="Show the information about the song currently playing.")
    async def _songInfo(self,ctx):
        if not await self.command_availability_check(ctx):
            return
        
        player = self.players.get(ctx.guild.id)
        if not player:
            await ctx.send(embed=discord.Embed(description=f"I'm not in a voice channel, use the `play` command to get started.", color=c2))
            return
        
        if not player.now_playing:
            await ctx.send(embed=discord.Embed(description=f"Nothing is currently playing, please add a song using play before using this command.", color=c2))
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
        if not await self.command_availability_check(ctx):
            return
        
        player = self.players.get(ctx.guild.id)
        if not player:
            await ctx.send(embed=discord.Embed(description=f"I'm not in a voice channel, use the `play` command to get started.", color=c2))
            return
        
        if not player.now_playing:
            await ctx.send(embed=discord.Embed(description=f"Nothing is currently playing, please add a song using `play` before using this command.", color=c2))
            return
        
        song_data = self.search_song_genius(player.now_playing.keyword, GENIUS_ACCESS_TOKEN)

        if not song_data:
            await ctx.send(embed=discord.Embed(description=f"No lyrics found.", color=c2))
            return
        
        try:
            song_url = f"https://genius.com{song_data['path']}"
            with requests.Session() as session:
                page = session.get(song_url)
                html = BeautifulSoup(page.text, 'html.parser')
        except Exception as e:
            await ctx.send(embed=discord.Embed(description=f"An error occurred while fetching the lyrics, please try again.\nError: {e}", color=c2))
            return
        
        lyrics_divs = html.find_all('div', {'data-lyrics-container': 'true'})

        lyrics = self.get_lyrics_text_genius(lyrics_divs)

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

