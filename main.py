import argparse
import json
import logging
import os
import sys

import discord
from discord.ext import commands
from discord.ext.commands import AutoShardedBot
from discord.ext.commands.context import Context
from discord.ext.commands.errors import (ExtensionAlreadyLoaded,
                                         ExtensionNotFound, ExtensionNotLoaded)
from pretty_help import PrettyHelp

from core.config import Configuration

# region Parser
parser = argparse.ArgumentParser(
    prog="Trinity", description="Economy discord bot made in python")
parser.add_argument("-l", "--logging",  default="INFO",
                    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="Choose level of logging")
parser.add_argument("-f", "--file", type=str, help="Filename for logging")
parser.add_argument("--token", default="mg", type=str,
                    help="Discord API token: Get yours at https://discord.com/developers/applications")
args = parser.parse_args()
# endregion


# region Logging
loglevels = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL:": logging.CRITICAL
}

logging.basicConfig(
    level=loglevels[args.logging], handlers=[logging.FileHandler(args.file, "w", 'utf-8'), logging.StreamHandler(sys.stdout)] if args.file else [logging.StreamHandler(sys.stdout)], format='%(levelname)s | %(asctime)s | %(name)s |->| %(message)s', datefmt=r"%H:%M:%S"
)
# endregion

default_extensions = ["cogs."+i.replace(".py", "")
                      for i in os.listdir("cogs") if i.endswith(".py")]

if not os.path.exists("config"):
    os.makedirs("config")


def get_prefix(bot, msg):
    return commands.when_mentioned_or(bot.configs[msg.guild.id]["prefix"])(bot, msg)


class CustomBot(AutoShardedBot):
    def get_fallback(self):
        fallback = {}
        with open("./core/fallback.json", "r") as _fallback:
            fallback: dict = json.load(_fallback)
        return fallback
    
    def __init__(self):
        super().__init__(
            command_prefix=get_prefix,
            help_command=PrettyHelp(
                color=0xffff00, show_index=True, sort_commands=True),
            intents=discord.Intents.all()
        )
        self.avatar = ""
        self.paused = False
        self.configs = {}
        self.asyncs_on_hold = []
        self.__version__ = "0.0.1alpha"
        self.fallback = self.get_fallback()
        self.logging_channels: list = []
        self.pattern = r"[\d]+-[\d]+-[\d]+ ([\d]+:[\d]+:[\d]+.[\d]+)  [A-Z]+ [\d]+ --- \[[^\]]+\] ([^\n]+)"


bot = CustomBot()

@bot.command(name="reload")
@commands.is_owner()
async def _reload_extension(ctx: Context, extension: str):
    try:
        bot.reload_extension("cogs."+extension)
        logging.info(f"{extension} reloaded")
        embed = discord.Embed(
            color=0x00ff00, description=f"{extension} reloaded")
        embed.set_author(name="Reload", icon_url=bot.avatar)
    except ExtensionNotFound:
        logging.error(f"{extension} not found")
        embed = discord.Embed(
            color=0xff0000, description=f"{extension} not found")
        embed.set_author(name="Reload", icon_url=bot.avatar)

    await ctx.send(embed=embed)


@bot.command(name="load")
@commands.is_owner()
async def _load_extension(ctx: Context, extension: str):
    try:
        bot.load_extension("cogs."+extension)
        logging.info(f"{extension} loaded")
        embed = discord.Embed(
            color=0x00ff00, description=f"{extension} loaded")
        embed.set_author(name="Load", icon_url=bot.avatar)
    except ExtensionAlreadyLoaded:
        logging.warn(f"{extension} already loaded")
        embed = discord.Embed(
            color=0xff0000, description=f"{extension} already loaded")
        embed.set_author(name="Load", icon_url=bot.avatar)
    except ExtensionNotFound:
        logging.error(f"{extension} not found")
        embed = discord.Embed(
            color=0xff0000, description=f"{extension} not found")
        embed.set_author(name="Load", icon_url=bot.avatar)

    await ctx.send(embed=embed)


@bot.command(name="unload")
@commands.is_owner()
async def _unload_extension(ctx: Context, extension: str):
    try:
        bot.unload_extension("cogs."+extension)
        logging.info(f"{extension} unloaded")
        embed = discord.Embed(
            color=0x00ff00, description=f"{extension} unloaded")
        embed.set_author(name="Unload", icon_url=bot.avatar)
    except ExtensionNotFound:
        logging.error(f"{extension} not found")
        embed = discord.Embed(
            color=0xff0000, description=f"{extension} not found")
        embed.set_author(name="Unload", icon_url=bot.avatar)
    except ExtensionNotLoaded:
        logging.error(f"{extension} not found")
        embed = discord.Embed(
            color=0xff0000, description=f"{extension} exists, but is not loaded")
        embed.set_author(name="Unload", icon_url=bot.avatar)

    await ctx.send(embed=embed)


@bot.command(name="reload-all")
@commands.is_owner()
async def reload_extension(ctx: Context):
    all_extensions = ["cogs."+i.replace(".py", "")
                      for i in os.listdir("cogs") if i.endswith(".py")]

    ok = True

    for extension in all_extensions:
        try:
            bot.reload_extension(extension)
            logging.info(f"{extension} reloaded")
        except ExtensionNotFound:
            ok = False
            logging.error(f"{extension} not found")
            embed = discord.Embed(
                color=0xff0000, description=f"{extension} not found")
            embed.set_author(name="Reload All", icon_url=bot.avatar)

    if ok:
        embed = discord.Embed(
            color=0x00ff00, description=f"All extensions reloaded")
        embed.set_author(name="Reload All", icon_url=bot.avatar)

    await ctx.send(embed=embed)

if __name__ == "__main__":
    for extension in default_extensions:
        bot.load_extension(extension)
        logging.info(f"{extension} loaded")

    bot.run(args.token, reconnect=True)
