import discord
import json
import logging
from discord.ext import commands
from utils.Tools import getConfig, updateConfig
from core.Cog import Cog
from core.Astroz import Astroz

logging.basicConfig(
    level=logging.INFO,
    format="\x1b[38;5;197m[\x1b[0m%(asctime)s\x1b[38;5;197m]\x1b[0m -> \x1b[38;5;197m%(message)s\x1b[0m",
    datefmt="%H:%M:%S",
)


class Guild(Cog):

    def __init__(self, client: Astroz):
        self.client = client

    @commands.Cog.listener(name="on_guild_join")
    async def on_guild_join(self, guild: discord.Guild):
        if not guild.chunked:
            await guild.chunk()
        # Initialise config for new guild
        getConfig(guild.id)
        # Send a welcome embed to the first writable text channel
        embed = discord.Embed(
            title="👋 Hey, I'm here!",
            description="Thanks for adding me! Use `help` to see all available commands.",
            color=0x2f3136,
        )
        embed.add_field(name="Prefix", value="Default prefix is `-`. Change it with `-prefix <new>`.", inline=False)
        channel = discord.utils.get(guild.text_channels, name="general")
        if not channel:
            channels = [c for c in guild.text_channels if c.permissions_for(guild.me).send_messages]
            if channels:
                channel = channels[0]
        if channel:
            try:
                await channel.send(embed=embed)
            except Exception:
                pass

    @commands.Cog.listener(name="on_guild_remove")
    async def on_guild_remove(self, guild: discord.Guild):
        # Clean up config entry for the removed guild
        try:
            with open("config.json", "r") as f:
                data = json.load(f)
            if str(guild.id) in data.get("guilds", {}):
                del data["guilds"][str(guild.id)]
            with open("config.json", "w") as f:
                json.dump(data, f, indent=4)
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_shard_ready(self, shard_id):
        logging.info("Shard #%s is ready" % shard_id)

    @commands.Cog.listener()
    async def on_shard_connect(self, shard_id):
        logging.info("Shard #%s connected" % shard_id)

    @commands.Cog.listener()
    async def on_shard_disconnect(self, shard_id):
        logging.info("Shard #%s disconnected" % shard_id)

    @commands.Cog.listener()
    async def on_shard_resume(self, shard_id):
        logging.info("Shard #%s resumed" % shard_id)
