import asyncio
from typing import TYPE_CHECKING

import discord
from discord.ext.commands.context import Context

if TYPE_CHECKING:
    from main import CustomBot


async def confirm(bot: "CustomBot", ctx: Context, message: str, timeout: int = 20, author: str = "Confirm"):
    try:
        embed = discord.Embed(
            colour=discord.Colour.from_rgb(255, 255, 0),
            description=message
        )
        embed.set_author(name=author, icon_url=bot.avatar)

        msg = await ctx.send(embed=embed)
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in ['✅', '❌']

        reaction, _ = await bot.wait_for('reaction_add', timeout=timeout, check=check)
        if reaction.emoji == '❌':
            await msg.delete()
            return False
        elif reaction.emoji == '✅':
            await msg.delete()
            return True
    except asyncio.TimeoutError:
        await msg.delete()
        return False


def jsonKeys2int(x):
    if isinstance(x, dict):
        try:
            return {int(k): v for k, v in x.items()}
        except:
            pass
    return x
