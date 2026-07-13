import discord
from discord.ext import commands
from utils.Tools import getConfig
from core.Cog import Cog
from core.Astroz import Astroz

BANNER_URL = (
    "https://cdn.discordapp.com/attachments/1520142476919177327/"
    "1526157135916961852/file_00000000aa6872308131f12fcc4653b5.png"
    "?ex=6a560017&is=6a54ae97&hm=36b5d304d4db608fffc040feb8d1ff303f3cd44bc92f5a5ec41912b6cddb818f&"
)


class HelpCommand(commands.HelpCommand):

    def _embed(self, color):
        embed = discord.Embed(color=color)
        embed.set_author(
            name="◈ ASTRA",
            icon_url=self.context.bot.user.display_avatar.url
        )
        return embed

    def _footer(self, embed):
        embed.set_footer(
            text=f"{self.context.author.name} • Thank you for using Astra",
            icon_url=self.context.author.display_avatar.url
        )

    async def send_bot_help(self, mapping):
        data = getConfig(self.context.guild.id)
        prefix = data.get("prefix", "-")

        embed = self._embed(0x5865F2)
        embed.description = (
            f"Prefix: `{prefix}` • Use `{prefix}help <command>` for details.\n"
            f"`<>` = required  `[]` = optional"
        )
        embed.add_field(
            name="<:general:1526132688820633601> General",
            inline=False,
            value="`avatar` `servericon` `membercount` `snipe`"
        )
        embed.add_field(
            name="<:Moderation:1526133761379401839> Moderation",
            inline=False,
            value=(
                "`ban` `kick` `warn` `unban` `softban`\n"
                "`mute` `purge` `prefix`\n"
                "`lock` `unlock` `lockall` `unlockall`\n"
                "`hide` `unhide` `hideall` `unhideall`\n"
                "`slowmode` `rslowmode` `give` `clone`"
            )
        )
        embed.add_field(
            name="<:Utility:1526133482500395028> Utility",
            inline=False,
            value=(
                "`stats` `ping` `serverinfo` `userinfo`\n"
                "`roleinfo` `channelinfo`\n"
                "`steal` `removeemoji` `unbanall`"
            )
        )
        embed.set_image(url=BANNER_URL)
        self._footer(embed)
        await self.context.reply(embed=embed, mention_author=False)

    async def send_command_help(self, command):
        embed = self._embed(0x4A7FC1)
        embed.title = f"Command: {command.name}"
        embed.description = (
            f"```yaml\n[] = optional  <> = required\nDo NOT type brackets when using commands.\n```\n"
            f"{command.help or 'No description provided.'}"
        )
        if command.aliases:
            embed.add_field(name="Aliases", value=" | ".join(f"`{a}`" for a in command.aliases), inline=False)
        embed.add_field(
            name="Usage",
            value=f"`{self.context.prefix}{command.qualified_name} {command.signature}`".strip(),
            inline=False
        )
        self._footer(embed)
        await self.context.reply(embed=embed, mention_author=False)

    async def send_group_help(self, group):
        embed = self._embed(0x2E86C1)
        embed.title = f"{group.qualified_name} — Subcommands"
        embed.description = "`[]` = optional  `<>` = required"
        for cmd in group.commands:
            embed.add_field(
                name=f"`{self.context.prefix}{cmd.qualified_name}`",
                value=cmd.short_doc or "No description.",
                inline=False
            )
        self._footer(embed)
        await self.context.reply(embed=embed, mention_author=False)

    async def send_cog_help(self, cog):
        embed = self._embed(0x1A5276)
        embed.title = f"{cog.qualified_name} Commands"
        for cmd in cog.get_commands():
            embed.add_field(
                name=f"`{self.context.prefix}{cmd.name}`",
                value=cmd.short_doc or "No description.",
                inline=False
            )
        self._footer(embed)
        await self.context.reply(embed=embed, mention_author=False)


class Help(Cog, name="help"):

    def __init__(self, client: Astroz):
        self._original_help_command = client.help_command
        attributes = {
            "name": "help",
            "aliases": ["h"],
            "cooldown": commands.CooldownMapping.from_cooldown(1, 5, commands.BucketType.user),
            "help": "Shows the help menu."
        }
        client.help_command = HelpCommand(command_attrs=attributes)
        client.help_command.cog = self

    async def cog_unload(self):
        self.bot.help_command = self._original_help_command
