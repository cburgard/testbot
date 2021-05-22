import discord
from discord.ext import commands

import utils as ut


def find_music(name, path):
    import os
    from fuzzywuzzy import fuzz
    match = None
    quality = 0
    for root, dirs, files in os.walk(path):
        for musicfile in files:
            path = os.path.join(root, musicfile)
            q = fuzz.partial_ratio(name,path)
            if q > quality:
                match = path
                quality = q
    return match

class Misc(commands.Cog):
    """
    Various useful Commands for everyone
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping', help="Check if Bot available")
    async def ping(self, ctx):
        print(f"ping: {round(self.bot.latency * 1000)}")

        await ctx.send(
            embed=ut.make_embed(
                name='Poll-Bot is available',
                value=f'`{round(self.bot.latency * 1000)}ms`')
        )

    @commands.command(name='play', help="Play music from Carstens computer")
    async def play(self,ctx):
        from discord import FFmpegPCMAudio
        from discord.utils import get
        channel = ctx.message.author.voice.channel
        if not channel:
            await ctx.send("You are not connected to a voice channel")
            return
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            keywords = " ".join(ctx.message.content.split()[1:])            
            thefile = find_music(keywords,"/home/cburgard/Music")
            if thefile:
                voice = await channel.connect()
                source = FFmpegPCMAudio(thefile)
                player = voice.play(source)
                await ctx.message.reply("Playing "+thefile)
            else:
                await ctx.message.reply("I don't have anything matching "+keywords)                

    @commands.command(name='hello', help="Say hello!")
    async def hello(self, ctx):
        person = ctx.author.name
        await ctx.send(content="Hello "+str(person)+"!")

    @commands.command(name='say', help="Simon says!")
    async def say(self, ctx):
        await ctx.message.add_reaction("\N{THUMBS UP SIGN}")
        await ctx.send(content=" ".join(ctx.message.content.split()[1:]))
        
    @commands.command(name='google', help="Google Image Search!")
    async def google(self, ctx):
        from os import listdir,remove
        from os.path import join as pjoin

        keywords = " ".join(ctx.message.content.split()[1:])
        
        from icrawler.builtin import GoogleImageCrawler
        google_Crawler = GoogleImageCrawler(storage = {'root_dir': r'tmp'})
        google_Crawler.crawl(keyword = keywords, max_num = 1)
        tmpfiles = listdir("tmp")
        if len(tmpfiles) > 0:
            tmpfile = tmpfiles[0]
            with open(pjoin("tmp",tmpfile), 'rb') as f:
                picture = discord.File(f)
                await ctx.channel.send(file=picture)
            for tmpfile in tmpfiles:
                remove(pjoin("tmp",tmpfile))
        else:
            await ctx.channel.send(content="No image found, weirdo!")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send('{0.mention} is here. What a n00b!'.format(member))

    @commands.Cog.listener()
    async def on_message(self, message):
        from random import uniform
        if message.author.id == self.bot.user.id:
            return
        if uniform(0,1) < 0.3:
            await message.channel.send("lol".format(message.author))
        import re
        if "nein" in message.content:
            await message.channel.send("{0.mention} doch!".format(message.author))
        if uniform(0,1) < 0.1 or re.search("[Rr]ick",message.content):
            await message.channel.send("https://media1.tenor.com/images/4324d537dbc06f422b34ae131c7b3e14/tenor.gif?itemid=7755460")
        if message.mention_everyone:
            await message.add_reaction("\N{ANGRY FACE}")
        if self.bot.user.mentioned_in(message):
            await message.channel.send("Was los {0.mention}, hast du Problem?".format(message.author))
            
        
def setup(bot):
    bot.add_cog(Misc(bot))
