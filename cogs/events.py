import logging
from typing import TYPE_CHECKING

import discord
from core.config import Configuration
from discord.activity import Activity
from discord.enums import ActivityType
from discord.errors import NotFound
from discord.ext import commands
from discord.ext.commands.errors import (CommandNotFound,
                                         MissingRequiredArgument)

if TYPE_CHECKING:
    from main import CustomBot


class Events(commands.Cog):

    def __init__(self, bot: "CustomBot"):
        @bot.event
        async def on_command_error(ctx, error):
            logging.debug(f"Error occured: {error}")
            if isinstance(error, CommandNotFound):
                embed = discord.Embed(
                    colour=0xff0000,
                    description=f'❌ Command not found'
                )
                embed.set_author(name="Status", icon_url=bot.avatar)
                await ctx.send(embed=embed)
            elif isinstance(error, NotFound):
                logging.debug("Error 404, passing")
                pass
            elif isinstance(error, MissingRequiredArgument):
                logging.debug(error)
                embed = discord.Embed(
                    colour=0xff0000,
                    description=f'❌ Missing required argument(s)'
                )
                embed.set_author(name="Status", icon_url=bot.avatar)
                await ctx.send(embed=embed)
                pass
            else:
                logging.debug("Error not catched, raising")
                raise error

        @bot.event
        async def on_ready():
            for guild in bot.guilds:
                config = Configuration(str(guild.id), bot)
                config.load()
                bot.configs[guild.id] = config
                if config.config["logging_channel"] is not None:
                    channel = bot.get_channel(config.config["logging_channel"])
                    if channel:
                        bot.logging_channels.append(channel)
                    

            await bot.change_presence(activity=Activity(name=f"{len(bot.guilds)} servers", type=ActivityType.watching))


def setup(bot: "CustomBot"):
    bot.add_cog(Events(bot))
