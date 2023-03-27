import nextcord, os
from dotenv import load_dotenv
from nextcord import Embed
from nextcord.ext import commands
from typing import Optional, Set

load_dotenv(r"./configs/.env")
token = os.getenv("TOKEN")
owner_id = os.getenv("OWNER_ID")

bot_theme = 0x6464ff

class HelpDropdown(nextcord.ui.Select):
    def __init__(self, help_command: "1", options: list[nextcord.SelectOption]):
        super().__init__(placeholder="Choose a category...", min_values=1, max_values=1, options=options)
        self._help_command = help_command

    async def callback(self, interaction: nextcord.Interaction):
        embed = (
            await self._help_command.cog_help_embed(self._help_command.context.bot.get_cog(self.values[0]))
            if self.values[0] != self.options[0].value
            else await self._help_command.bot_help_embed(self._help_command.get_bot_mapping())
        )
        await interaction.response.edit_message(embed=embed)


class HelpView(nextcord.ui.View):
    def __init__(self, help_command: "1", options: list[nextcord.SelectOption], *, timeout: Optional[float] = 120.0):
        super().__init__(timeout=timeout)
        self.add_item(HelpDropdown(help_command, options))
        self._help_command = help_command

    async def on_timeout(self):
        self.clear_items()
        await self._help_command.response.edit(view=self)

    async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
        return self._help_command.context.author == interaction.user


class Mainhelpcommand(commands.MinimalHelpCommand):
    def get_command_signature(self, command):
        return f"{self.context.clean_prefix}{command.qualified_name} {command.signature}"

    async def _cog_select_options(self) -> list[nextcord.SelectOption]:
        options: list[nextcord.SelectOption] = []
        options.append(nextcord.SelectOption(
            label="Home",
            emoji="🏠",
            description="Go back to the main menu.",
        ))

        for cog, command_set in self.get_bot_mapping().items():
            filtered = await self.filter_commands(command_set, sort=True)
            if not filtered:
                continue
            emoji = getattr(cog, "COG_EMOJI", None)
            options.append(nextcord.SelectOption(
                label=cog.qualified_name if cog else "No Category",
                emoji=emoji,
                description=cog.description[:100] if cog and cog.description else None
            ))

        return options

    async def _help_embed(
        self, title: str, description: Optional[str] = None, mapping: Optional[str] = None,
        command_set: Optional[Set[commands.Command]] = None, set_author: bool = False
    ) -> Embed:
        embed = Embed(title=title, color=bot_theme)
        if description:
            embed.description = description
        if set_author:
            avatar = self.context.bot.user.avatar or self.context.bot.user.default_avatar
            embed.set_author(name=self.context.bot.user.name, icon_url=avatar.url)
        if command_set:
            # show help about all commands in the set
            filtered = await self.filter_commands(command_set, sort=True)
            for command in filtered:
                embed.add_field(
                    name=self.get_command_signature(command),
                    value=command.short_doc or "...",
                    inline=False
                )
        elif mapping:
            # add a short description of commands in each cog
            for cog, command_set in mapping.items():
                filtered = await self.filter_commands(command_set, sort=True)
                if not filtered:
                    continue
                name = cog.qualified_name if cog else "No category"
                emoji = getattr(cog, "COG_EMOJI", None)
                cog_label = f"{emoji} {name}" if emoji else name
                # \u2002 is an en-space
                cmd_list = "\u2002".join(
                    f"`{self.context.clean_prefix}{cmd.name}`" for cmd in filtered
                )
                value = (
                    f"{cog.description}\n{cmd_list}"
                    if cog and cog.description
                    else cmd_list
                )
                embed.add_field(name=cog_label, value=value)
        return embed

    async def bot_help_embed(self, mapping: dict) -> Embed:
        return await self._help_embed(
            title="Bot Commands",
            description=self.context.bot.description,
            mapping=mapping,
            set_author=True,
        )
    
    async def send_bot_help(self, mapping: dict):
        embed = await self.bot_help_embed(mapping)
        options = await self._cog_select_options()
        self.response = await self.get_destination().send(embed=embed, view=HelpView(self, options))

    async def send_command_help(self, command: commands.Command):
        emoji = getattr(command.cog, "COG_EMOJI", None)
        embed = await self._help_embed(
            title=f"{emoji} {command.qualified_name}" if emoji else command.qualified_name,
            description=command.help,
            command_set=command.commands if isinstance(command, commands.Group) else None
        )
        await self.get_destination().send(embed=embed)

    async def cog_help_embed(self, cog: Optional[commands.Cog]) -> Embed:
        if cog is None:
            return await self._help_embed(
                title=f"No category",
                command_set=self.get_bot_mapping()[None]
            )
        emoji = getattr(cog, "COG_EMOJI", None)
        return await self._help_embed(
            title=f"{emoji} {cog.qualified_name}" if emoji else cog.qualified_name,
            description=cog.description,
            command_set=cog.get_commands()
        )

    async def send_cog_help(self, cog: commands.Cog):
        embed = await self.cog_help_embed(cog)
        await self.get_destination().send(embed=embed)

    send_group_help = send_command_help
    
client = commands.Bot(
    command_prefix = 'm!',
    help_command = Mainhelpcommand(),
    intents = nextcord.Intents.all()
  )



@client.command()
async def coglist(ctx):
    i = 1
    embed = nextcord.Embed(color=bot_theme)
    embed.set_author(name="List of Cogs")
    for f in os.listdir('./cogs'):
        if f.endswith('.py'):
            embed.add_field(name = f'Cog No.{i}', value = f[:-3], inline = False)
            i += 1
    embed.set_footer(text = f'Requested by {ctx.author}')
    embed.set_thumbnail(url = 'https://cdn.pixabay.com/photo/2013/07/12/13/50/cog-147414_960_720.png')
    await ctx.send(embed = embed)


 
@client.command(brief='reload all cogs')
async def restart(ctx):
    if str(ctx.author.id) != owner_id:
        await ctx.send(f'`You are not the owner of this bot!`')
        return

    for f in os.listdir('./cogs'):
        if f.endswith('.py'):
            try:
                client.unload_extension(f'cogs.{f[:-3]}')
            except:
                pass

    for f in os.listdir('./cogs'):
        if f.endswith('.py'):
            client.load_extension(f'cogs.{f[:-3]}')
            print(f'{f[:-3]} has been succesfully loaded!')

    await ctx.send(f'`{client.user} has been succesfully restarted!`')



if __name__ == '__main__':
    for f in os.listdir('./cogs'):
        if f.endswith('.py'):
            client.load_extension(f'cogs.{f[:-3]}')
            print(f'{f[:-3]} has been succesfully loaded!')

    client.run(token)