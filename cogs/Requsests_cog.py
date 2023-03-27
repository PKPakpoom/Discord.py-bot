from nextcord.ext import commands
import requests

class RequestsCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @commands.command()
    async def req(self, ctx):
        await ctx.send(requests.get('https://google.com').status_code)


def setup(client):
    client.add_cog(RequestsCog(client))