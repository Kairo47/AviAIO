import discord
import asyncio
import datetime
import re
from discord.ext import commands
from discord.ui import Button, View
from utils.Tools import blacklist_check, ignore_check, getConfig, updateConfig

time_regex = re.compile(r"(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}


def parse_time(argument: str) -> int:
    matches = re.findall(time_regex, argument.lower())
    if not matches:
        return -1
    total = 0
    for key, unit in matches:
        try:
            total += time_dict[unit] * float(key)
        except (KeyError, ValueError):
            return -1
    return round(total)


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def _embed(self, color, ctx):
        embed = discord.Embed(color=color)
        embed.set_author(name="◈ ASTRA", icon_url=self.bot.user.display_avatar.url)
        embed.set_footer(
            text=f"{ctx.author.name} • Thank you for using Astra",
            icon_url=ctx.author.display_avatar.url
        )
        return embed

    # ── Unlock All ───────────────────────────────────────────────────────────

    @commands.command(name="unlockall", aliases=["ua"], help="Unlocks all channels in the server.", usage="unlockall")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def unlockall(self, ctx, *, reason=None):
        loading = self._embed(0x004D00, ctx)
        loading.description = "<a:loading:1002226340516331571> | Unlocking all channels..."
        msg = await ctx.reply(embed=loading, mention_author=False)
        for channel in ctx.guild.channels:
            try:
                await channel.set_permissions(ctx.guild.default_role,
                    overwrite=discord.PermissionOverwrite(send_messages=True, read_messages=True),
                    reason=reason)
            except Exception:
                pass
        done = self._embed(0x004D00, ctx)
        done.description = "<:GreenTick:1526084976758493254> | All channels have been unlocked."
        await msg.edit(embed=done)

    # ── Lock All ─────────────────────────────────────────────────────────────

    @commands.command(name="lockall", aliases=["la"], help="Locks all channels in the server.", usage="lockall")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def lockall(self, ctx, *, reason=None):
        loading = self._embed(0x5C0A0A, ctx)
        loading.description = "<a:loading:1002226340516331571> | Locking all channels..."
        msg = await ctx.reply(embed=loading, mention_author=False)
        for channel in ctx.guild.channels:
            try:
                await channel.set_permissions(ctx.guild.default_role,
                    overwrite=discord.PermissionOverwrite(send_messages=False, read_messages=True),
                    reason=reason)
            except Exception:
                pass
        done = self._embed(0x5C0A0A, ctx)
        done.description = "<:GreenTick:1526084976758493254> | All channels have been locked."
        await msg.edit(embed=done)

    # ── Give (Add Role) ──────────────────────────────────────────────────────

    @commands.command(name="give", aliases=["addrole", "ar"], help="Gives a role to a member.", usage="give <member> <role>")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def give(self, ctx, member: discord.Member, role: discord.Role):
        if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            embed = self._embed(0x003366, ctx)
            embed.description = "<:a_error:1526134515578179584> | That role is above or equal to your top role."
            return await ctx.send(embed=embed)
        if role >= ctx.guild.me.top_role:
            embed = self._embed(0x003366, ctx)
            embed.description = "<:a_error:1526134515578179584> | That role is above my top role."
            return await ctx.send(embed=embed)
        await member.add_roles(role, reason=f"Role added by {ctx.author}")
        embed = self._embed(0x003366, ctx)
        embed.add_field(name="Role Given", value=f"{role.mention} → {member.mention}", inline=False)
        await ctx.send(embed=embed)

    # ── Hide All ─────────────────────────────────────────────────────────────

    @commands.command(name="hideall", aliases=["ha"], help="Hides all channels from @everyone.", usage="hideall")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(manage_channels=True)
    async def hideall(self, ctx):
        loading = self._embed(0x1A001A, ctx)
        loading.description = "<a:loading:1002226340516331571> | Hiding all channels..."
        msg = await ctx.reply(embed=loading, mention_author=False)
        for channel in ctx.guild.channels:
            try:
                await channel.set_permissions(ctx.guild.default_role, view_channel=False)
            except Exception:
                pass
        done = self._embed(0x1A001A, ctx)
        done.description = "<:GreenTick:1526084976758493254> | All channels have been hidden."
        await msg.edit(embed=done)

    # ── Unhide All ───────────────────────────────────────────────────────────

    @commands.command(name="unhideall", aliases=["uha"], help="Unhides all channels for @everyone.", usage="unhideall")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(manage_channels=True)
    async def unhideall(self, ctx):
        loading = self._embed(0x00334D, ctx)
        loading.description = "<a:loading:1002226340516331571> | Unhiding all channels..."
        msg = await ctx.reply(embed=loading, mention_author=False)
        for channel in ctx.guild.channels:
            try:
                await channel.set_permissions(ctx.guild.default_role, view_channel=True)
            except Exception:
                pass
        done = self._embed(0x00334D, ctx)
        done.description = "<:GreenTick:1526084976758493254> | All channels have been unhidden."
        await msg.edit(embed=done)

    # ── Hide ─────────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="hide", aliases=["hc"], help="Hides a channel.", usage="hide [channel]")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    async def hide(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.view_channel = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite,
                                      reason=f"Hidden by {ctx.author}")
        embed = self._embed(0x2D0033, ctx)
        embed.description = f"<:GreenTick:1526084976758493254> | Hidden {channel.mention}."
        await ctx.reply(embed=embed)

    # ── Unhide ───────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="unhide", aliases=["uhc"], help="Unhides a channel.", usage="unhide [channel]")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    async def unhide(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.view_channel = True
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite,
                                      reason=f"Unhidden by {ctx.author}")
        embed = self._embed(0x003333, ctx)
        embed.description = f"<:GreenTick:1526084976758493254> | Unhidden {channel.mention}."
        await ctx.reply(embed=embed)

    # ── Prefix ───────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="prefix", aliases=["setprefix", "sp"],
                             help="Changes the bot prefix for this server.", usage="prefix <new_prefix>")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def prefix(self, ctx, new_prefix: str):
        if len(new_prefix) > 5:
            embed = self._embed(0x331A00, ctx)
            embed.description = "<:a_error:1526134515578179584> | Prefix can't be longer than 5 characters."
            return await ctx.reply(embed=embed, mention_author=False)
        data = getConfig(ctx.guild.id)
        old = data.get("prefix", "-")
        data["prefix"] = new_prefix
        updateConfig(ctx.guild.id, data)
        embed = self._embed(0x331A00, ctx)
        embed.description = f"<:GreenTick:1526084976758493254> | Prefix changed: `{old}` → `{new_prefix}`"
        await ctx.reply(embed=embed, mention_author=False)

    # ── Softban ──────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="softban", aliases=["sb"],
                             help="Bans then unbans a member (removes their messages).", usage="softban <member> [reason]")
    @blacklist_check()
    @ignore_check()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def softban(self, ctx, member: discord.Member, *, reason=None):
        reason = reason or f"Softbanned by {ctx.author}"
        await member.ban(reason=reason, delete_message_days=7)
        await ctx.guild.unban(member, reason=reason)
        embed = self._embed(0x4D0000, ctx)
        embed.description = f"<:GreenTick:1526084976758493254> | Softbanned {member.mention}.\n**Reason:** {reason}"
        await ctx.send(embed=embed)

    # ── Purge ────────────────────────────────────────────────────────────────

    @commands.group(name="purge", aliases=["clear", "p"], invoke_without_command=True,
                    help="Deletes messages.", usage="purge <amount>")
    @commands.has_guild_permissions(manage_messages=True)
    @blacklist_check()
    @ignore_check()
    async def purge(self, ctx, amount: int = 10):
        if amount > 1000:
            return await ctx.send("Amount must be 1000 or less.")
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"<:GreenTick:1526084976758493254> Deleted **{len(deleted)-1}** message(s).", delete_after=4)

    @purge.command(name="startswith", help="Purge messages starting with a keyword.")
    @blacklist_check()
    @ignore_check()
    @commands.has_guild_permissions(manage_messages=True)
    async def purge_startswith(self, ctx, key: str, amount: int = 10):
        counter = 0
        def check(m):
            nonlocal counter
            if counter >= amount: return False
            if m.content.startswith(key): counter += 1; return True
            return False
        deleted = await ctx.channel.purge(limit=200, check=check)
        await ctx.send(f"<:GreenTick:1526084976758493254> Deleted **{len(deleted)}** message(s).", delete_after=4)

    @purge.command(name="endswith", help="Purge messages ending with a keyword.")
    @blacklist_check()
    @ignore_check()
    @commands.has_guild_permissions(manage_messages=True)
    async def purge_endswith(self, ctx, key: str, amount: int = 10):
        counter = 0
        def check(m):
            nonlocal counter
            if counter >= amount: return False
            if m.content.endswith(key): counter += 1; return True
            return False
        deleted = await ctx.channel.purge(limit=200, check=check)
        await ctx.send(f"<:GreenTick:1526084976758493254> Deleted **{len(deleted)}** message(s).", delete_after=4)

    @purge.command(name="contains", help="Purge messages containing a keyword.")
    @blacklist_check()
    @ignore_check()
    @commands.has_guild_permissions(manage_messages=True)
    async def purge_contains(self, ctx, key: str, amount: int = 10):
        counter = 0
        def check(m):
            nonlocal counter
            if counter >= amount: return False
            if key in m.content: counter += 1; return True
            return False
        deleted = await ctx.channel.purge(limit=200, check=check)
        await ctx.send(f"<:GreenTick:1526084976758493254> Deleted **{len(deleted)}** message(s).", delete_after=4)

    @purge.command(name="user", help="Purge messages from a specific user.")
    @blacklist_check()
    @ignore_check()
    @commands.has_guild_permissions(manage_messages=True)
    async def purge_user(self, ctx, member: discord.Member, amount: int = 10):
        counter = 0
        def check(m):
            nonlocal counter
            if counter >= amount: return False
            if m.author.id == member.id: counter += 1; return True
            return False
        deleted = await ctx.channel.purge(limit=200, check=check)
        await ctx.send(f"<:GreenTick:1526084976758493254> Deleted **{len(deleted)}** message(s).", delete_after=4)

    @purge.command(name="invites", help="Purge messages containing invite links.")
    @blacklist_check()
    @ignore_check()
    @commands.has_guild_permissions(manage_messages=True)
    async def purge_invites(self, ctx, amount: int = 10):
        counter = 0
        def check(m):
            nonlocal counter
            if counter >= amount: return False
            if "discord.gg/" in m.content.lower(): counter += 1; return True
            return False
        deleted = await ctx.channel.purge(limit=200, check=check)
        await ctx.send(f"<:GreenTick:1526084976758493254> Deleted **{len(deleted)}** message(s).", delete_after=4)

    # ── Mute (Timeout) ───────────────────────────────────────────────────────

    @commands.hybrid_command(name="mute", aliases=["timeout", "stfu"],
                             help="Times out a member for a duration (e.g. 10m, 2h, 1d).", usage="mute <member> <duration>")
    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.guild_only()
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, member: discord.Member, duration: str):
        if member.guild_permissions.administrator:
            embed = self._embed(0x0A0A3D, ctx)
            embed.description = "<:a_error:1526134515578179584> | Can't mute an administrator."
            return await ctx.reply(embed=embed)
        seconds = parse_time(duration)
        if seconds <= 0:
            embed = self._embed(0x0A0A3D, ctx)
            embed.description = "<:a_error:1526134515578179584> | Invalid duration. Examples: `10m`, `2h`, `1d`"
            return await ctx.reply(embed=embed)
        until = discord.utils.utcnow() + datetime.timedelta(seconds=seconds)
        await member.timeout(until, reason=f"Muted by {ctx.author}")
        embed = self._embed(0x0A0A3D, ctx)
        embed.description = f"<:GreenTick:1526084976758493254> | Muted {member.mention} for **{duration}**."
        await ctx.send(embed=embed)

    # ── Kick ─────────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="kick", aliases=["k"],
                             help="Kicks a member from the server.", usage="kick <member> [reason]")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        if member == ctx.guild.me:
            return await ctx.send("You can't kick me!")
        if ctx.author.top_role <= member.top_role and ctx.author != ctx.guild.owner:
            embed = self._embed(0x4D1A00, ctx)
            embed.description = "<:a_error:1526134515578179584> | You can't kick someone with a higher or equal role."
            return await ctx.send(embed=embed)
        reason = reason or "No reason provided"
        try:
            await member.send(embed=discord.Embed(color=0x4D1A00,
                description=f":exclamation: You were kicked from **{ctx.guild.name}**.\n**Reason:** {reason}"))
        except Exception:
            pass
        await member.kick(reason=reason)
        embed = self._embed(0x4D1A00, ctx)
        embed.description = f"<:GreenTick:1526084976758493254> | Kicked **{member}**.\n**Reason:** {reason}"
        await ctx.send(embed=embed)

    # ── Warn ─────────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="warn", aliases=["w"],
                             help="Warns a member.", usage="warn <member> [reason]")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason="No reason provided"):
        embed = self._embed(0x4D3300, ctx)
        embed.description = f"<:GreenTick:1526084976758493254> | **{member.display_name}** has been warned.\n**Reason:** {reason}"
        await ctx.send(embed=embed)
        try:
            await member.send(embed=discord.Embed(color=0x4D3300,
                description=f":exclamation: You were warned in **{ctx.guild.name}**.\n**Reason:** {reason}"))
        except Exception:
            pass

    # ── Ban ──────────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="ban", aliases=["b"],
                             help="Bans a member from the server.", usage="ban <member> [reason]")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        if member == ctx.guild.me:
            return await ctx.send("You can't ban me!")
        if ctx.author.top_role <= member.top_role and ctx.author != ctx.guild.owner:
            embed = self._embed(0x3D0014, ctx)
            embed.description = "<:a_error:1526134515578179584> | You can't ban someone with a higher or equal role."
            return await ctx.send(embed=embed)
        reason = reason or "No reason provided"
        try:
            await member.send(embed=discord.Embed(color=0x3D0014,
                description=f":exclamation: You were banned from **{ctx.guild.name}**.\n**Reason:** {reason}"))
        except Exception:
            pass
        await member.ban(reason=reason)
        embed = self._embed(0x3D0014, ctx)
        embed.description = f"<:GreenTick:1526084976758493254> | Banned **{member}**.\n**Reason:** {reason}"
        await ctx.send(embed=embed)

    # ── Unban ────────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="unban", aliases=["ub"],
                             help="Unbans a user by their ID.", usage="unban <user_id>")
    @blacklist_check()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            embed = self._embed(0x003D00, ctx)
            embed.description = f"<:GreenTick:1526084976758493254> | Unbanned **{user}**."
            await ctx.send(embed=embed)
        except discord.NotFound:
            embed = self._embed(0x003D00, ctx)
            embed.description = "<:a_error:1526134515578179584> | User not found or not banned."
            await ctx.send(embed=embed)

    # ── Clone ────────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="clone", aliases=["cc"],
                             help="Clones a channel.", usage="clone <channel>")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(manage_channels=True)
    async def clone(self, ctx, channel: discord.TextChannel):
        await channel.clone()
        embed = self._embed(0x00003D, ctx)
        embed.description = f"<:GreenTick:1526084976758493254> | Cloned **{channel.name}**."
        await ctx.send(embed=embed)

    # ── Lock ─────────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="lock", aliases=["lockdown", "lc"],
                             help="Locks a channel.", usage="lock [channel] [reason]")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.TextChannel = None, *, reason=None):
        channel = channel or ctx.channel
        await channel.set_permissions(ctx.guild.default_role,
            overwrite=discord.PermissionOverwrite(send_messages=False), reason=reason)
        embed = self._embed(0x3D003D, ctx)
        embed.description = f"<:GreenTick:1526084976758493254> | Locked {channel.mention}."
        await ctx.send(embed=embed)

    # ── Unlock ───────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="unlock", aliases=["unlockdown", "ulc"],
                             help="Unlocks a channel.", usage="unlock [channel] [reason]")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None, *, reason=None):
        channel = channel or ctx.channel
        await channel.set_permissions(ctx.guild.default_role,
            overwrite=discord.PermissionOverwrite(send_messages=True), reason=reason)
        embed = self._embed(0x003D3D, ctx)
        embed.description = f"<:GreenTick:1526084976758493254> | Unlocked {channel.mention}."
        await ctx.send(embed=embed)

    # ── Slowmode ─────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="slowmode", aliases=["slow", "sm"],
                             help="Sets slowmode in the current channel (max 21600s).", usage="slowmode <seconds>")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    async def slowmode(self, ctx, seconds: int):
        if seconds > 21600:
            embed = self._embed(0x1A0033, ctx)
            embed.description = "<:a_error:1526134515578179584> | Slowmode max is 21600 seconds (6 hours)."
            return await ctx.send(embed=embed)
        await ctx.channel.edit(slowmode_delay=seconds)
        msg = "Slowmode disabled." if seconds == 0 else f"Slowmode set to **{seconds}s**."
        embed = self._embed(0x1A0033, ctx)
        embed.description = f"<:GreenTick:1526084976758493254> | {msg}"
        await ctx.send(embed=embed)

    # ── Remove Slowmode ──────────────────────────────────────────────────────

    @commands.hybrid_command(name="rslowmode", aliases=["rslow", "rsm", "unslowmode"],
                             help="Removes slowmode from the current channel.", usage="rslowmode")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    async def rslowmode(self, ctx):
        await ctx.channel.edit(slowmode_delay=0)
        embed = self._embed(0x330033, ctx)
        embed.description = "<:GreenTick:1526084976758493254> | Slowmode removed."
        await ctx.send(embed=embed)
