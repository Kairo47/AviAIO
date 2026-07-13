import discord
import json
from discord.ext import commands
from core import Astroz, Cog, Context


class Errors(Cog):

    def __init__(self, client: Astroz):
        self.client = client

    def _embed(self, ctx, color=0x5A0000):
        embed = discord.Embed(color=color)
        embed.set_author(name="◈ ASTRA", icon_url=self.client.user.display_avatar.url)
        embed.set_footer(
            text=f"{ctx.author.name} • Thank you for using Astra",
            icon_url=ctx.author.display_avatar.url
        )
        return embed

    @commands.Cog.listener()
    async def on_command_error(self, ctx: Context, error):
        with open('ignore.json', 'r') as f:
            randi = json.load(f)
        with open('blacklist.json', 'r') as f:
            data = json.load(f)

        if isinstance(error, commands.CommandNotFound):
            return

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

        elif isinstance(error, commands.CheckFailure):
            if str(ctx.author.id) in data["ids"]:
                embed = self._embed(ctx, 0x6D0000)
                embed.title = "❌ Blacklisted"
                embed.description = (
                    "You Are Blacklisted From Using My Commands.\n"
                    "If You Think That It Is A Mistake, You Can Appeal In Our Support Server "
                    "By Clicking [here](https://discord.gg/)"
                )
                await ctx.reply(embed=embed, mention_author=False)
            if str(ctx.channel.id) in randi["ids"]:
                await ctx.reply(
                    f"My all commands are disabled for {ctx.channel.mention}",
                    mention_author=True, delete_after=6
                )

        elif isinstance(error, commands.NoPrivateMessage):
            embed = self._embed(ctx, 0x2C0052)
            embed.description = "You Can't Use My Commands In DM(s)"
            await ctx.reply(embed=embed, delete_after=20)

        elif isinstance(error, commands.TooManyArguments):
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

        elif isinstance(error, commands.CommandOnCooldown):
            embed = self._embed(ctx, 0x4E2600)
            embed.description = (
                f"<:a_error:1526134515578179584> | {ctx.author.name} is on cooldown — "
                f"retry after **{error.retry_after:.2f}s**"
            )
            await ctx.reply(embed=embed, delete_after=10)

        elif isinstance(error, commands.MaxConcurrencyReached):
            embed = self._embed(ctx, 0x004040)
            embed.description = (
                "<:a_error:1526134515578179584> | This command is already running — "
                "let it finish and try again."
            )
            await ctx.reply(embed=embed, delete_after=10)
            ctx.command.reset_cooldown(ctx)

        elif isinstance(error, commands.MissingPermissions):
            missing = [
                perm.replace("_", " ").replace("guild", "server").title()
                for perm in error.missing_permissions
            ]
            fmt = (
                "{}, and {}".format(", ".join(missing[:-1]), missing[-1])
                if len(missing) > 2
                else " and ".join(missing)
            )
            embed = self._embed(ctx, 0x400000)
            embed.description = (
                f"<:a_error:1526134515578179584> | You lack `{fmt}` permission(s) "
                f"to run `{ctx.command.name}`!"
            )
            await ctx.reply(embed=embed, delete_after=6)
            ctx.command.reset_cooldown(ctx)

        elif isinstance(error, commands.BadArgument):
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

        elif isinstance(error, commands.BotMissingPermissions):
            missing = ", ".join(error.missing_perms)
            embed = self._embed(ctx, 0x001040)
            embed.description = (
                f"<:a_error:1526134515578179584> | I need **{missing}** permission(s) "
                f"to run `{ctx.command.name}`!"
            )
            await ctx.send(embed=embed, delete_after=10)

        elif isinstance(error, discord.HTTPException):
            if error.code == 50013:
                await ctx.send("I don't have enough permissions to do that.", delete_after=8)

        elif isinstance(error, commands.CommandInvokeError):
            original = error.original
            if isinstance(original, discord.Forbidden):
                embed = self._embed(ctx, 0x200040)
                embed.description = (
                    "<:a_error:1526134515578179584> | I don't have permission to do that. "
                    "Please check my role permissions."
                )
                await ctx.reply(embed=embed, mention_author=False, delete_after=10)
            elif isinstance(original, discord.NotFound):
                embed = self._embed(ctx, 0x002040)
                embed.description = (
                    "<:a_error:1526134515578179584> | Couldn't find that — "
                    "it may have been deleted or doesn't exist."
                )
                await ctx.reply(embed=embed, mention_author=False, delete_after=10)
            else:
                embed = self._embed(ctx, 0x400040)
                embed.description = (
                    f"<:a_error:1526134515578179584> | Something went wrong running "
                    f"`{ctx.command.name}`. Error: `{type(original).__name__}`"
                )
                await ctx.reply(embed=embed, mention_author=False, delete_after=15)
