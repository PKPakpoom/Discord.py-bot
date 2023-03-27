from nextcord import Embed
from nextcord.ext import commands
from json import load, dump
from datetime import datetime
from pytz import timezone

class LogsCog(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        with open("./configs/config.json", "rt") as r:
            config = load(r)

        if (str(member.guild.id) not in config.keys()):
            return
        
        if (before.channel == after.channel):
            return
        
        channel = self.client.get_channel(int(config[str(member.guild.id)]["voice_log"]))
        
        if before.channel == None:
            embed = Embed(title = f"{member}", color = 0x64ff64)
            embed.set_thumbnail(url = member.display_avatar)
            embed.add_field(name = "", value = f"{member.name if not member.nick else member.nick} joined the {after.channel.name}", inline = True)
            embed.set_footer(text = datetime.now(timezone("Asia/Jakarta")))
            await channel.send(embed=embed)

        elif after.channel == None:
            embed = Embed(title = f"{member}", color = 0xff0000)
            embed.set_thumbnail(url = member.display_avatar)
            embed.add_field(name = f"", value = f"{member.name if not member.nick else member.nick} Left the {before.channel.name}", inline = True)
            embed.set_footer(text = datetime.now(timezone("Asia/Jakarta")))
            await channel.send(embed=embed)

        elif before.channel != None and after.channel != None:
            embed = Embed(title = f"{member}", color=0xffc832)
            embed.set_thumbnail(url = member.display_avatar)
            embed.add_field(name = "", value = f"{member.name if not member.nick else member.nick} moved from {before.channel.name} to {after.channel.name}", inline = True)
            embed.set_footer(text = datetime.now(timezone("Asia/Jakarta")))
            await channel.send(embed=embed)

    @commands.command()
    async def setlog(self, ctx, channel: commands.TextChannelConverter):
        with open("./configs/config.json", "rt") as r:
            config = load(r)
        
        if (str(ctx.guild.id) not in config.keys()):
            config[str(ctx.guild.id)] = {}
        
        config[str(ctx.guild.id)]["voice_log"] = str(channel.id)
        
        with open("./configs/config.json", "wt") as f:
            dump(config, f, indent = 4)
        
        await ctx.send(f"Set {channel.mention} as voice log channel")

def setup(client):
    client.add_cog(LogsCog(client))