from __future__ import annotations
from core import Astroz

from .commands.help import Help
from .commands.general import General
from .commands.moderation import Moderation
from .commands.extra import Utility
from .events.Errors import Errors
from .events.on_guild import Guild


async def setup(bot: Astroz):
    await bot.add_cog(Help(bot))
    await bot.add_cog(General(bot))
    await bot.add_cog(Moderation(bot))
    await bot.add_cog(Utility(bot))
    await bot.add_cog(Errors(bot))
    await bot.add_cog(Guild(bot))
