"""
    DIABLO - A bot that bans pedos and zoos
    (C) 2022 skqwid. All rights reserved.
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
from discord import Option
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
    await client.wait_until_ready()
    await client.change_presence(
        status=discord.Status.online
    )

    print('Activated!')

# CommandNotFound
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(title=":octagonal_sign: Something went wrong", description=f'```{error}```', color=discord.Color.red())
        embed.set_footer(text="If this error persists, contact us here: https://github.com/incipious/DIABLO/issues")
        await ctx.respond(embed=embed)

# Missing Permissions Error
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title=":octagonal_sign: Something went wrong", description=f'```{error}```', color=discord.Color.red())
        embed.set_footer(text="If this error persists, contact us here: https://github.com/incipious/DIABLO/issues")
        await ctx.respond(embed=embed)

# NotOwner
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        embed = discord.Embed(title=":octagonal_sign: Something went wrong", description=f'You are unable to run this command.```{error}```', color=discord.Color.red())
        await ctx.respond(embed=embed)

# Cooldown Error
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(title=":octagonal_sign: Something went wrong", description=f'```{error}```', color=0xCD1F1F)
        embed.set_footer(text="If this error persists, contact us here: https://github.com/incipious/DIABLO/issues")
        await ctx.respond(embed=embed)

@client.event
async def on_command(ctx):
    try:
        api.command_run(ctx)
    except:
        pass

@client.slash_command(name="load", description="Load cog (owner-specific)", guild_only=True, guild_ids=config.guildCocktail)
@commands.is_owner()
async def load(ctx, extension : Option(str, description="Which cog (lowercase):")):
    try:
        client.load_extension(f"cogs.{extension}")
        await ctx.respond("👍")
    except:
        await ctx.respond("👎")

@client.slash_command(name="unload", description="Unload cog (owner-specific)", guild_only=True, guild_ids=config.guildCocktail)
@commands.is_owner()
async def unload(ctx, extension : Option(str, description="Which cog (lowercase):")):
    try:
        client.unload_extension(f"cogs.{extension}")
        await ctx.respond("👍")
    except:
        await ctx.respond("👎")

@client.slash_command(name="reload", description="Reload cog (owner-specific)", guild_only=True, guild_ids=config.guildCocktail)
@commands.is_owner()
async def reload(ctx, extension : Option(str, description="Which cog (lowercase):")):
    try:
        client.unload_extension(f"cogs.{extension}")
        client.load_extension(f"cogs.{extension}")
        await ctx.respond("👍")
    except:
        await ctx.respond("👎")

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")

client.run(config.token)
