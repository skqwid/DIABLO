"""
    DIABLO - A bot that bans pedos and zoos
    (C) 2020-2022 incipious. All rights reserved.
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
# DIABLO: Database Influenced Automated Ban List of Offenders

import discord
import os
from discord.ext import commands
import statcord
from utils import default

config = default.get("config.json")

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
client = commands.Bot(command_prefix = 'd.', intents=intents)

#STATCORD SO I CAN SEE STATS
key = str(config.statcordKey)
api = statcord.Client(client,key)
api.start_loop()

@client.event
async def on_ready():
    log_channel = client.get_guild(753028931686498424).get_channel(928414146981150771)

    await client.change_presence(
        status=discord.Status.online
    )

    print('Activated!')
    await log_channel.send("Fully Activated! :white_check_mark:")

# CommandNotFound
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(title=":octagonal_sign: This command does not exist", description="Use `d.help` to get a full list of commands", color=0xCD1F1F)
        await ctx.send(embed=embed, delete_after=3.5)

# Missing Permissions Error
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(description=":octagonal_sign: You do not have the correct permissions to run this command.", color=0xCD1F1F)
        await ctx.send(embed=embed, delete_after=3.5)

# Cooldown Error
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(description=f":octagonal_sign: Command is on cooldown. Try again in **{round(error.retry_after)}** seconds.", color=0xCD1F1F)
        await ctx.send(embed=embed, delete_after=3.5)

@client.event
async def on_command(ctx):
    try:
        api.command_run(ctx)
    except:
        pass

@client.command(hidden=True)
@commands.is_owner()
@commands.guild_only()
async def load(ctx, extension):
    try:
        client.load_extension(f"cogs.{extension}")
        await ctx.message.add_reaction("👍")
    except:
        await ctx.message.add_reaction("👎")

@client.command(hidden=True)
@commands.is_owner()
@commands.guild_only()
async def unload(ctx, extension):
    try:
        client.unload_extension(f"cogs.{extension}")
        await ctx.message.add_reaction("👍")
    except:
        await ctx.message.add_reaction("👎")

@client.command(hidden=True)
@commands.is_owner()
@commands.guild_only()
async def reload(ctx, extension):
    try:
        client.unload_extension(f"cogs.{extension}")
        client.load_extension(f"cogs.{extension}")
        await ctx.message.add_reaction("👍")
    except:
        await ctx.message.add_reaction("👎")

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")

client.run(config.testToken)
