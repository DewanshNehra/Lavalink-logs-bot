import logging
import os
import re
from datetime import datetime
from typing import TYPE_CHECKING

from core.functions import confirm
from discord.channel import TextChannel
from discord.ext import commands, tasks
from discord.ext.commands.context import Context

if TYPE_CHECKING:
    from main import CustomBot

class Logging(commands.Cog):
    
    def __init__(self, bot: "CustomBot") -> None:
        self.bot = bot
        self.last_timestamp = ""
        self.filename = ""
        
    @commands.command(name="setup-channel")
    @commands.is_owner()
    async def setup_channel(self, ctx: Context):
        if await confirm(self.bot, ctx, "Set this channel as logging channel?"):
            if ctx.guild != None:
                self.bot.configs[ctx.guild.id]["logging_channel"] = ctx.channel.id
                self.bot.configs[ctx.guild.id].save()
    
    @commands.command(name="set-filename")
    @commands.is_owner()
    async def set_filename(self, ctx: Context, *, filename: str):
        if await confirm(self.bot, ctx, f"Set filename to {filename}?"):
            if ctx.guild != None:
                self.filename = filename

    # run task repeatedly
    @tasks.loop(seconds=5)
    async def check_logs(self):
        logging.debug("Checking logs")
        
        messages: list[str] = []
        
        with open(self.filename, "r") as f:
            data_raw = f.read()
            pattern = re.compile(r"[\d]+-[\d]+-[\d]+ ([\d]+:[\d]+:[\d]+.[\d]+)  [A-Z]+ [\d]+ --- [\[[\w]+] ([^\n]+)")
            
            last_timestamp = datetime.strptime(self.last_timestamp, r"%H:%M:%S.%f") if self.last_timestamp else datetime.strptime("01:01:01.01", r"%H:%M:%S.%f")
            data = [i for i in pattern.findall(data_raw) if datetime.strptime(i[0], r"%H:%M:%S.%f") > last_timestamp]
            for i in data:
                messages.append(f"`{i[0]}` | {i[1]}")
            
            if len(messages) > 0:
                for channel in self.bot.logging_channels:
                    for message in messages:
                        await channel.send(message)
                self.last_timestamp = data[-1][0]
            
    @commands.command(name="start-logging")
    async def start_logging(self, ctx: Context):
        if ctx.guild == None: return
        if self.bot.configs[ctx.guild.id]["logging_channel"] is None:
            await ctx.send("No logging channel set")
            return
        if self.filename == "":
            await ctx.send("No filename set")
            return
        
        self.check_logs.start()
        
    @commands.command(name="stop-logging")
    async def stop_logging(self, ctx: Context):
        self.check_logs.stop()
            
        
def setup(bot: "CustomBot") -> None:
    bot.add_cog(Logging(bot))
