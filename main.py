import os
from core.Astroz import Astroz
from keep_alive import keep_alive
import asyncio
import jishaku, cogs
import discord

os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"

client = Astroz()


@client.event
async def on_ready():
    print("Loaded & Online!")
    print(f"Logged in as: {client.user}")
    print(f"Connected to: {len(client.guilds)} guilds")
    print(f"Connected to: {len(client.users)} users")
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} slash commands")
    except Exception as e:
        print(e)


async def main():
    async with client:
        await client.load_extension("cogs")
        await client.load_extension("jishaku")
        await client.start(os.getenv("TOKEN"))


if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())
