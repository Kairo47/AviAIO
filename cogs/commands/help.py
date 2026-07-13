import discord
from discord.ext import commands
from utils.Tools import getConfig
from core.Cog import Cog
from core.Astroz import Astroz


class HelpCommand(commands.HelpCommand):

    async def send_bot_help(self, mapping):
        data = getConfig(self.context.guild.id)
        prefix = data.get("prefix", "-")

        embed = discord.Embed(color=0x2f3136)
        embed.set_author(
            name=f"{self.context.bot.user.name} — Help",
            icon_url=self.context.bot.user.display_avatar.url
        )
        embed.set_thumbnail(url=self.context.bot.user.display_avatar.url)
        embed.description = (
            f"Prefix: `{prefix}` • Use `{prefix}help <command>` for details.\n"
            f"`<>` = required  `[]` = optional"
        )

        embed.add_field(name="🖼️ General", inline=False, value=(
            f"`avatar` `servericon` `membercount` `snipe`"
        ))

        embed.add_field(name="🔨 Moderation", inline=False, value=(
            f"`ban` `kick` `warn` `unban` `softban`\n"
            f"`mute` `purge` `prefix`\n"
            f"`lock` `unlock` `lockall` `unlockall`\n"
            f"`hide` `unhide` `hideall` `unhideall`\n"
            f"`slowmode` `rslowmode` `give` `clone`"
        ))

        embed.add_field(name="🛸 Utility", inline=False, value=(
            f"`stats` `ping` `serverinfo` `userinfo`\n"
            f"`roleinfo` `channelinfo`\n"
            f"`steal` `removeemoji` `unbanall`"
        ))

        embed.set_footer(
            text=f"Requested by {self.context.author}",
            icon_url=self.context.author.display_avatar.url
        )
        embed.timestamp = discord.utils.utcnow()
        await self.context.reply(embed=embed, mention_author=False)

    async def send_command_help(self, command):
        embed = discord.Embed(color=0x2f3136)
        embed.set_author(
            name=f"Command: {command.name}",
            icon_url=self.context.bot.user.display_avatar.url
        )
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
        await self.context.reply(embed=embed, mention_author=False)

    async def send_group_help(self, group):
        embed = discord.Embed(
            color=0x2f3136,
            title=f"{group.qualified_name} — Subcommands",
            description=f"`[]` = optional  `<>` = required"
        )
        for cmd in group.commands:
            embed.add_field(
                name=f"`{self.context.prefix}{cmd.qualified_name}`",
                value=cmd.short_doc or "No description.",
                inline=False
            )
        await self.context.reply(embed=embed, mention_author=False)

    async def send_cog_help(self, cog):
        embed = discord.Embed(
            color=0x2f3136,
            title=f"{cog.qualified_name} Commands",
        )
        for cmd in cog.get_commands():
            embed.add_field(
                name=f"`{self.context.prefix}{cmd.name}`",
                value=cmd.short_doc or "No description.",
                inline=False
            )
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
