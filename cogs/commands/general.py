import discord
from discord.ext import commands
from utils.Tools import blacklist_check, ignore_check
from typing import Optional, Union


class General(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.sniped = {}

    def _embed(self, color, ctx):
        embed = discord.Embed(color=color)
        embed.set_author(name="◈ ASTRA", icon_url=self.bot.user.display_avatar.url)
        embed.set_footer(
            text=f"{ctx.author.name} • Thank you for using Astra",
            icon_url=ctx.author.display_avatar.url
        )
        return embed

    # ── Avatar ──────────────────────────────────────────────────────────────

    @commands.hybrid_command(
        name="avatar",
        aliases=["av", "pfp", "avi"],
        usage="avatar [member]",
        help="Shows a member's avatar."
    )
    @blacklist_check()
    @ignore_check()
    async def avatar(self, ctx, member: Optional[Union[discord.Member, discord.User]] = None):
        member = member or ctx.author
        user = await self.bot.fetch_user(member.id)
        if not user.avatar:
            return await ctx.send("This user has no avatar.")
        png  = user.avatar.replace(format="png")
        jpg  = user.avatar.replace(format="jpg")
        webp = user.avatar.replace(format="webp")
        links = f"[`PNG`]({png}) | [`JPG`]({jpg}) | [`WEBP`]({webp})"
        if user.avatar.is_animated():
            gif = user.avatar.replace(format="gif")
            links += f" | [`GIF`]({gif})"
        embed = self._embed(0x1B1464, ctx)
        embed.description = links
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_image(url=user.avatar.url)
        await ctx.send(embed=embed)

    # ── Server Icon ─────────────────────────────────────────────────────────

    @commands.hybrid_command(
        name="servericon",
        aliases=["sicon", "guildicon"],
        usage="servericon",
        help="Shows the server's icon."
    )
    @blacklist_check()
    @ignore_check()
    async def servericon(self, ctx: commands.Context):
        if not ctx.guild.icon:
            return await ctx.send("This server has no icon.")
        icon = ctx.guild.icon
        png  = icon.replace(format="png")
        jpg  = icon.replace(format="jpg")
        webp = icon.replace(format="webp")
        links = f"[`PNG`]({png}) | [`JPG`]({jpg}) | [`WEBP`]({webp})"
        if icon.is_animated():
            links += f" | [`GIF`]({icon.replace(format='gif')})"
        embed = self._embed(0x006400, ctx)
        embed.title = f"{ctx.guild.name}'s Icon"
        embed.description = links
        embed.set_image(url=icon.url)
        await ctx.send(embed=embed)

    # ── Member Count ─────────────────────────────────────────────────────────

    @commands.hybrid_command(
        name="membercount",
        aliases=["mc"],
        usage="membercount",
        help="Shows the server's member count breakdown."
    )
    @blacklist_check()
    @ignore_check()
    async def membercount(self, ctx: commands.Context):
        online = offline = dnd = idle = bots = 0
        for m in ctx.guild.members:
            if m.bot:
                bots += 1
            elif m.status == discord.Status.online:
                online += 1
            elif m.status == discord.Status.offline:
                offline += 1
            elif m.status == discord.Status.dnd:
                dnd += 1
            elif m.status == discord.Status.idle:
                idle += 1
        embed = self._embed(0x8B0000, ctx)
        embed.title = ctx.guild.name
        embed.description = f"Member info for **{ctx.guild.name}**"
        embed.add_field(name="<:ONLINE:1526087003223883906> Online",   value=f"`{online}`",                  inline=True)
        embed.add_field(name="<:idel:1526086937679630436> Idle",       value=f"`{idle}`",                    inline=True)
        embed.add_field(name="<:dnd:1526086757916086414> DND",         value=f"`{dnd}`",                     inline=True)
        embed.add_field(name="<:OFFLINE:1526087074984235090> Offline", value=f"`{offline}`",                 inline=True)
        embed.add_field(name="<:bot:1526088400682090576> Bots",        value=f"`{bots}`",                    inline=True)
        embed.add_field(name="<:a_users:1526088103591153754> Total",   value=f"`{len(ctx.guild.members)}`",  inline=True)
        await ctx.send(embed=embed)

    # ── Snipe ────────────────────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.guild or message.author.bot or not message.content:
            return
        self.sniped[message.channel.id] = message

    @commands.hybrid_command(
        name="snipe",
        usage="snipe",
        help="Shows the most recently deleted message in this channel."
    )
    @commands.guild_only()
    @commands.has_permissions(view_audit_log=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @blacklist_check()
    @ignore_check()
    async def snipe(self, ctx: commands.Context):
        message = self.sniped.get(ctx.channel.id)
        if not message:
            embed = self._embed(0x3D0000, ctx)
            embed.title = "Snipe"
            embed.description = "<:a_error:1526134515578179584> No recently deleted messages in this channel."
            return await ctx.send(embed=embed)
        embed = self._embed(0x4A0404, ctx)
        embed.title = f"Sniped — sent by {message.author}"
        embed.description = message.content
        await ctx.send(embed=embed)
