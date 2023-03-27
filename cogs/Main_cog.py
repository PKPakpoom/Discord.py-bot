from nextcord.ext import commands
from nextcord import FFmpegPCMAudio

class Maincog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('pong')

    @commands.command(brief = 'Say what you text in')
    async def say(self, ctx, *message):
        if len(message) == 0:
            return
        await ctx.send(' '.join(message))
    
    @commands.command()
    async def clear(self, ctx, amount = 5):
        await ctx.channel.purge(limit=amount)

    @commands.command()
    async def disconnectall(self, ctx):
        if ctx.message.author.voice != None:
            channel = ctx.message.author.voice.channel
            for user in channel.members:
                await user.move_to(None)
        else:
            await ctx.send("Join voice channel to use command")

def setup(client):
    client.add_cog(Maincog(client))