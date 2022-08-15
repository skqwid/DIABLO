import datetime

import discord
from discord import Option
from discord.ext import commands
from discord.commands import slash_command
from pymongo import MongoClient

import cogs.moderation
from utils import default
import asyncio

config = default.get("config.json")

cluster = MongoClient(config.mongoKey)
db = cluster["DIABLO"]
collection = db["Warnings"]

diablocolor = 0x1551b3

class Moderation(commands.Cog):

    def __init__(self, client):
        self.client = client

    # mute
    @slash_command(name="mute", description="Mutes a member for a specified number of minutes.", guild_only=True)
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member : Option(discord.Member, description="Input user:"), minutes: Option(int, description="How long do you want this person to be muted for?"), *, reason : Option(str, description="What for?", required=False)):
        if int(minutes) <= 0:
            await ctx.respond("I cannot perform this operation.")
        else:
            duration = datetime.timedelta(minutes=minutes)
            await member.timeout_for(duration, reason=f'{ctx.author.name}#{ctx.author.discriminator}: {reason}')

            embed = discord.Embed(color=diablocolor)
            embed.set_author(name=f'{member.name}#{member.discriminator} Muted', icon_url=member.display_avatar)
            embed.add_field(name="Duration", value=f'{duration} *(Hours/Minutes/Seconds)*')
            await ctx.respond(embed=embed)
    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed=discord.Embed(title="Something went wrong... ⚠", description=f"```{error}```", color=0xCD1F1F)
            embed.set_footer(text="If this error persists, contact us here: https://github.com/incipious/DIABLO/issues")
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Something went wrong... ⚠", description=f'```{error}```', color=0xCD1F1F)
            embed.set_footer(text="If this error persists, contact us here: https://github.com/incipious/DIABLO/issues")
            await ctx.respond(embed=embed)

    # unmute
    @slash_command(name="unmute", description="Unmute a previously muted member.", guild_only=True)
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member : Option(discord.Member, description="Input user:")):
        await member.remove_timeout()
        embed = discord.Embed(color=diablocolor)
        embed.set_author(name=f'{member.name}#{member.discriminator} Unmuted', icon_url=member.display_avatar)
        await ctx.respond(embed=embed)
    @unmute.error
    async def unmute_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed=discord.Embed(title="Something went wrong... ⚠", description=f"```{error}```", color=0xCD1F1F)
            embed.set_footer(text="If this error persists, contact us here: https://github.com/incipious/DIABLO/issues")
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Something went wrong... ⚠", description=f'```{error}```', color=0xCD1F1F)
            embed.set_footer(text="If this error persists, contact us here: https://github.com/incipious/DIABLO/issues")
            await ctx.respond(embed=embed)

    # Kick command
    @slash_command(name="kick", description="Kicks a user from the server", guild_only=True)
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member : Option(discord.Member, description="Input user:"), reason : Option(str, description="Reason:", required=False)):
        if member.id == ctx.author.id:
            await ctx.respond("You cannot kick yourself.", delete_after=5.0)
        elif member.id == self.client.user.id:
            await ctx.respond("I'm sorry that this isn't working out, but I can't kick myself.", delete_after=5.0)
        else:
            await member.kick(reason=f'{ctx.author.name}#{ctx.author.discriminator}: {reason}')
            embed=discord.Embed(color=diablocolor)
            embed.add_field(name="Reason", value=str(reason))
            embed.set_author(name=f"{member.name}#{member.discriminator} Kicked", icon_url=str(member.display_avatar))
            await ctx.respond(embed=embed)
    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed=discord.Embed(description=":octagonal_sign: Please specify a user to kick.", color=0xCD1F1F)
            embed.set_footer(text="If this error persists, contact us here: https://github.com/incipious/DIABLO/issues")
            await ctx.respond(embed=embed, delete_after=5.0)
        else:
            embed = discord.Embed(title="Something went wrong... ⚠", description=f'```{error}```', color=0xCD1F1F)
            embed.set_footer(text="If this error persists, contact us here: https://github.com/incipious/DIABLO/issues")
            await ctx.respond(embed=embed)

    # Ban
    @slash_command(name="ban", description="Bans a user from the server", guild_only=True)
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member : Option(discord.Member, description="Input user:"), reason : Option(str, description="Reason:", required=False)):
        if member.id == ctx.author.id:
            await ctx.respond("You cannot ban yourself.", delete_after=5.0)
        elif member.id == self.client.user.id:
            await ctx.respond("I'm sorry that this isn't working out, but I can't ban myself.", delete_after=5.0)
        else:
            await member.ban(reason=f'{ctx.author.name}#{ctx.author.discriminator}: {reason}')
            embed=discord.Embed(color=diablocolor)
            embed.add_field(name="Reason", value=str(reason))
            embed.set_author(name=f"{member.name}#{member.discriminator} Banned", icon_url=str(member.display_avatar))
            await ctx.respond(embed=embed)
    @kick.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed=discord.Embed(description=":octagonal_sign: Please specify a user to ban.", color=0xCD1F1F)
            embed.set_footer(text="If this error persists, contact us here: https://github.com/incipious/DIABLO/issues")
            await ctx.respond(embed=embed, delete_after=5.0)
        else:
            embed = discord.Embed(title="Something went wrong... ⚠", description=f'```{error}```', color=0xCD1F1F)
            embed.set_footer(text="If this error persists, contact us here: https://github.com/incipious/DIABLO/issues")
            await ctx.respond(embed=embed)

    # unban
    @slash_command(name="unban", description="Unbans a user from your server", guild_only=True, cog="""What do I put here?""")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split("#")

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                embed=discord.Embed(
                    title=f"{member.name} was unbanned.",
                    description=f"{member.name} was unbanned banned from the server.",
                    color=0x7289da
                )
                await ctx.respond(embed=embed)
                return
    @unban.error
    async def unban_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed=discord.Embed(description="Please specify a user to unban.", color=0xCD1F1F)
            embed.set_footer(text="If this error persists, contact us here: https://github.com/incipious/DIABLO/issues")
            await ctx.send(embed=embed, delete_after=2.0)
        elif isinstance(error, commands.BadArgument):
            embed=discord.Embed(description="Make sure you wrote the user name and discriminator (tagline) correctly.", color=0xCD1F1F)
            embed.set_footer(text="If this error persists, contact us here: https://github.com/incipious/DIABLO/issues")
            await ctx.send(embed=embed, delete_after=2.0)
        else:
            embed = discord.Embed(title="Something went wrong... ⚠", description=f'```{error}```', color=0xCD1F1F)
            embed.set_footer(text="If this error persists, contact us here: https://github.com/incipious/DIABLO/issues")
            await ctx.respond(embed=embed)

    # Purge (clear) command
    @commands.slash_command(name="purge", description="Clears a specified amount of messages", guild_only=True)
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(rate=1, per=6.5, type=commands.BucketType.user)
    async def purge(self, ctx, amount: Option(int, description="How many messages do you want to delete?")):
        if not amount > 100 and amount >= 0:
            await ctx.channel.purge(limit=amount)
            embed = discord.Embed(description=f"{amount} messages cleared.", color=diablocolor)
            await ctx.respond(embed=embed, delete_after=2.0)
        elif amount < 0:
            embed = discord.Embed(description=f"That isn't possible, {ctx.author}.", color=0x8636d1)
            await ctx.respond(embed=embed, delete_after=2.0)
        elif amount > 100:
            embed = discord.Embed(description=f":octagonal_sign: **Purge limit cannot exceed 100.**", color=0xFF0000)
            await ctx.respond(embed=embed, delete_after=2.0)
    @purge.error
    async def purge_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            embed = discord.Embed(title="Something went wrong... ⚠", description=f'```{error}```', color=0xCD1F1F)
            embed.set_footer(text="If this error persists, contact us here: https://github.com/incipious/DIABLO/issues")
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(title="Something went wrong... ⚠", description=f'```{error}```', color=0xCD1F1F)
            embed.set_footer(text="If this error persists, contact us here: https://github.com/incipious/DIABLO/issues")
            await ctx.respond(embed=embed)

def setup(client):
    client.add_cog(Moderation(client))
