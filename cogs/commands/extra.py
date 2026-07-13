import discord
import time
import datetime
import requests
from discord.ext import commands
from utils.Tools import blacklist_check, ignore_check
from typing import Optional, Union

start_time = time.time()

OWNER_IDS = [1177294135313584138]


class Utility(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ── Ping ─────────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="ping", aliases=["latency"], help="Shows the bot's latency.", usage="ping")
    @blacklist_check()
    @ignore_check()
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000, 2)
        embed = discord.Embed(color=0x2f3136,
            description=f"🏓 Pong! `{latency} ms`")
        await ctx.send(embed=embed)

    # ── Stats ────────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="stats", aliases=["st", "botstats"], help="Shows bot statistics.", usage="stats")
    @blacklist_check()
    @ignore_check()
    async def stats(self, ctx):
        server_count = len(self.bot.guilds)
        total_members = sum(g.member_count for g in self.bot.guilds if g.member_count)
        uptime = str(datetime.timedelta(seconds=int(round(time.time() - start_time))))

        # Fetch owner mentions (deduplicated)
        dev_lines = []
        seen = set()
        for uid in OWNER_IDS:
            if uid not in seen:
                seen.add(uid)
                try:
                    u = await self.bot.fetch_user(uid)
                    dev_lines.append(f"[{u.name}](https://discord.com/users/{uid})")
                except Exception:
                    dev_lines.append(f"<@{uid}>")
        devs_value = "\n".join(dev_lines) if dev_lines else "Unknown"

        embed = discord.Embed(color=0x2f3136)
        embed.set_author(name=f"{self.bot.user.name} Stats", icon_url=self.bot.user.display_avatar.url)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.add_field(name="﹒SERVERS",    value=f"```{server_count}```",                         inline=True)
        embed.add_field(name="﹒USERS",      value=f"```{total_members}```",                        inline=True)
        embed.add_field(name="﹒PING",       value=f"```{round(self.bot.latency*1000,2)} ms```",    inline=True)
        embed.add_field(name="﹒UPTIME",     value=f"```{uptime}```",                               inline=True)
        embed.add_field(name="﹒DEVELOPERS", value=devs_value,                                      inline=False)
        embed.set_footer(text="avi.ae", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    # ── Server Info ──────────────────────────────────────────────────────────

    @commands.hybrid_command(name="serverinfo", aliases=["si", "sinfo", "guildinfo"],
                             help="Shows information about the server.", usage="serverinfo")
    @blacklist_check()
    @ignore_check()
    @commands.guild_only()
    async def serverinfo(self, ctx: commands.Context):
        guild = ctx.guild
        c_at = int(guild.created_at.timestamp())
        humans = len([m for m in guild.members if not m.bot])
        bots   = len([m for m in guild.members if m.bot])

        nsfw_map = {"default": "Default", "explicit": "Explicit", "safe": "Safe", "age_restricted": "Age Restricted"}
        nsfw_level = nsfw_map.get(guild.nsfw_level.name, "Unknown")

        embed = discord.Embed(color=0x2f3136)
        embed.set_author(
            name=f"{guild.name} — Server Info",
            icon_url=guild.icon.url if guild.icon else guild.me.display_avatar.url
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        if guild.banner:
            embed.set_image(url=guild.banner.url)
        embed.timestamp = discord.utils.utcnow()
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        embed.add_field(name="__About__", inline=False, value=(
            f"**Name:** {guild.name}\n"
            f"**ID:** {guild.id}\n"
            f"**Owner:** {guild.owner} (<@{guild.owner_id}>)\n"
            f"**Created:** <t:{c_at}:F>"
        ))
        embed.add_field(name="__Members__", inline=True, value=(
            f"Total: **{len(guild.members)}**\n"
            f"Humans: **{humans}**\n"
            f"Bots: **{bots}**"
        ))
        embed.add_field(name="__Channels__", inline=True, value=(
            f"Text: **{len(guild.text_channels)}**\n"
            f"Voice: **{len(guild.voice_channels)}**\n"
            f"Categories: **{len(guild.categories)}**"
        ))
        embed.add_field(name="__Extras__", inline=False, value=(
            f"**Boost Level:** {guild.premium_tier} ({guild.premium_subscription_count} boosts)\n"
            f"**Verification:** {str(guild.verification_level).title()}\n"
            f"**NSFW Level:** {nsfw_level}\n"
            f"**Emojis:** {len(guild.emojis)} | **Stickers:** {len(guild.stickers)}"
        ))
        if guild.roles:
            roles_str = " ".join(r.mention for r in reversed(guild.roles[1:]))
            if len(roles_str) > 1000:
                roles_str = f"{len(guild.roles)} roles (too many to list)"
            embed.add_field(name=f"__Roles [{len(guild.roles)}]__", value=roles_str, inline=False)

        await ctx.reply(embed=embed)

    # ── User Info ────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="userinfo", aliases=["ui", "whois"],
                             help="Shows information about a user.", usage="userinfo [member]")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.guild_only()
    async def userinfo(self, ctx, member: Optional[Union[discord.Member, discord.User]] = None):
        member = member or ctx.author
        if isinstance(member, discord.Member) and member not in ctx.guild.members:
            member = await self.bot.fetch_user(member.id)

        badges = ""
        flags = member.public_flags
        if flags.hypesquad_balance:        badges += "<:balance:1059415997729226793> "
        if flags.hypesquad_bravery:        badges += "<:bravery:1059416107733221386> "
        if flags.hypesquad_brilliance:     badges += "<:brilliance:1059416199605272587> "
        if flags.early_supporter:          badges += "<a:earlysup:1003952039807696937> "
        if flags.active_developer:         badges += "<:active_dev:1040559350034473000> "
        if flags.verified_bot_developer:   badges += "<:activedev:1044968012932976750> "
        if flags.staff:                    badges += "<:staff_flag:1052742379741925406> "
        if flags.partner:                  badges += "<:partner_flag:1052742550647218196> "
        if not badges:                     badges = "None"

        bannerUser = await self.bot.fetch_user(member.id)
        embed = discord.Embed(color=0x2f3136)
        embed.set_author(name=f"{member.name}'s Info", icon_url=member.display_avatar.url)
        embed.set_thumbnail(url=member.display_avatar.url)
        if bannerUser.banner:
            embed.set_image(url=bannerUser.banner.url)
        embed.timestamp = discord.utils.utcnow()

        created = f"<t:{round(member.created_at.timestamp())}:R>"
        joined = "N/A"
        nick = "None"

        if isinstance(member, discord.Member) and member in ctx.guild.members:
            joined = f"<t:{round(member.joined_at.timestamp())}:R>"
            nick = member.nick or "None"

        embed.add_field(name="__General__", inline=False, value=(
            f"**Name:** {member}\n"
            f"**ID:** {member.id}\n"
            f"**Nickname:** {nick}\n"
            f"**Bot:** {'Yes' if member.bot else 'No'}\n"
            f"**Badges:** {badges}\n"
            f"**Account Created:** {created}\n"
            f"**Server Joined:** {joined}"
        ))

        if isinstance(member, discord.Member) and member in ctx.guild.members:
            roles = ", ".join(r.mention for r in reversed(member.roles[1:])) or "None"
            if len(roles) > 1000:
                roles = f"{len(member.roles)-1} roles"
            embed.add_field(name="__Roles__", inline=False, value=(
                f"**Top Role:** {member.top_role.mention}\n"
                f"**Roles:** {roles}"
            ))

            if isinstance(member, discord.Member):
                if member == ctx.guild.owner:       ack = "Server Owner"
                elif member.guild_permissions.administrator: ack = "Server Admin"
                elif member.guild_permissions.ban_members or member.guild_permissions.kick_members: ack = "Server Moderator"
                else:                               ack = "Server Member"
                embed.add_field(name="__Acknowledgement__", value=ack, inline=False)

        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    # ── Role Info ────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="roleinfo", aliases=["ri", "rinfo"],
                             help="Shows information about a role.", usage="roleinfo <role>")
    @blacklist_check()
    @ignore_check()
    async def roleinfo(self, ctx, *, role: discord.Role):
        perms = [p.upper() for p, allowed in iter(role.permissions) if allowed]
        embed = discord.Embed(title=f"@{role.name}", color=role.color)
        embed.add_field(name="ID",           value=str(role.id),             inline=True)
        embed.add_field(name="Color",        value=str(role.color).upper(),  inline=True)
        embed.add_field(name="Members",      value=str(len(role.members)),   inline=True)
        embed.add_field(name="Mentionable",  value=str(role.mentionable),    inline=True)
        embed.add_field(name="Hoisted",      value=str(role.hoist),          inline=True)
        embed.add_field(name="Mention",      value=role.mention,             inline=True)
        embed.add_field(name="Created",      value=role.created_at.strftime("%d/%m/%Y"), inline=True)
        if perms:
            embed.add_field(name="Permissions", value=" ".join(f"`{p}`" for p in perms[:15]), inline=False)
        if role.icon and isinstance(role.icon, discord.Asset):
            embed.set_thumbnail(url=role.icon.url)
        await ctx.send(embed=embed)

    # ── Steal Emoji ──────────────────────────────────────────────────────────

    @commands.hybrid_command(name="steal", aliases=["eadd", "emojisteal"],
                             help="Adds an emoji to the server.", usage="steal <emoji>")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(manage_emojis=True)
    async def steal(self, ctx, emote: str):
        if not emote.startswith("<"):
            return await ctx.send(embed=discord.Embed(color=0x2f3136, description="Invalid emoji. Use a custom emoji."))
        try:
            parts = emote.split(":")
            name = parts[1]
            emoji_id = parts[2][:-1]
            animated = emote.startswith("<a")
            ext = "gif" if animated else "png"
            url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{ext}"
            response = requests.get(url)
            img = response.content
            new_emoji = await ctx.guild.create_custom_emoji(name=name, image=img)
            await ctx.send(embed=discord.Embed(color=0x2f3136,
                description=f"<:GreenTick:1526084976758493254> | Added **`{new_emoji}`**!"))
        except Exception as e:
            await ctx.send(embed=discord.Embed(color=0x2f3136,
                description=f"<a:error:1002226340516331571> | Failed to add emoji: `{e}`"))

    # ── Remove Emoji ─────────────────────────────────────────────────────────

    @commands.hybrid_command(name="removeemoji", aliases=["delemoji", "re"],
                             help="Removes an emoji from the server.", usage="removeemoji <emoji>")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(manage_emojis=True)
    async def removeemoji(self, ctx, emoji: discord.Emoji):
        name = emoji.name
        await emoji.delete()
        await ctx.send(embed=discord.Embed(color=0x2f3136,
            description=f"<:GreenTick:1526084976758493254> | Removed emoji **`{name}`**."))

    # ── Unban All ────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="unbanall", aliases=["massunban"],
                             help="Unbans everyone in the server.", usage="unbanall")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def unbanall(self, ctx):
        yes_btn = discord.ui.Button(label="Yes", style=discord.ButtonStyle.green, emoji="✅")
        no_btn  = discord.ui.Button(label="No",  style=discord.ButtonStyle.red,   emoji="❌")
        view = discord.ui.View()
        view.add_item(yes_btn)
        view.add_item(no_btn)

        async def yes_callback(interaction: discord.Interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("Not for you.", ephemeral=True)
            await interaction.response.edit_message(content="Unbanning all members...", embed=None, view=None)
            count = 0
            async for ban_entry in interaction.guild.bans(limit=None):
                await interaction.guild.unban(ban_entry.user, reason=f"Unbanall by {ctx.author}")
                count += 1
            await interaction.channel.send(f"<:GreenTick:1526084976758493254> | Unbanned **{count}** member(s).")

        async def no_callback(interaction: discord.Interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("Not for you.", ephemeral=True)
            await interaction.response.edit_message(content="Cancelled.", embed=None, view=None)

        yes_btn.callback = yes_callback
        no_btn.callback  = no_callback

        embed = discord.Embed(color=0x2f3136, description="**Are you sure you want to unban everyone?**")
        await ctx.reply(embed=embed, view=view, mention_author=False)

    # ── Channel Info ─────────────────────────────────────────────────────────

    @commands.hybrid_command(name="channelinfo", aliases=["ci", "cinfo"],
                             help="Shows info about a channel.", usage="channelinfo [channel]")
    @blacklist_check()
    @ignore_check()
    @commands.guild_only()
    async def channelinfo(self, ctx, channel: Optional[discord.TextChannel] = None):
        channel = channel or ctx.channel
        created = int(channel.created_at.timestamp())
        embed = discord.Embed(color=0x2f3136, title=f"#{channel.name}")
        embed.add_field(name="ID",         value=str(channel.id),                    inline=True)
        embed.add_field(name="Type",       value=str(channel.type).title(),           inline=True)
        embed.add_field(name="Category",   value=channel.category.name if channel.category else "None", inline=True)
        embed.add_field(name="Created",    value=f"<t:{created}:R>",                 inline=True)
        embed.add_field(name="Slowmode",   value=f"{channel.slowmode_delay}s",        inline=True)
        embed.add_field(name="NSFW",       value=str(channel.is_nsfw()),             inline=True)
        if channel.topic:
            embed.add_field(name="Topic",  value=channel.topic[:200],                inline=False)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)
