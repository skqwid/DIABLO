import discord
from discord.ext import commands, tasks
from pymongo import MongoClient
from utils import default

config = default.get("config.json")

cluster = MongoClient(config.mongoKey)
db = cluster["DIABLO"]
collection = db["Warnings"]

diablocolor = 0x1551b3

class Moderation(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.warnings_delete.start()

    # mute
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, member : discord.Member):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            await ctx.guild.create_role(name="Muted", permissions=(discord.Permissions(send_messages=False, speak=False)))
        await member.add_roles(muted_role)
        embed = discord.Embed(description=f"{member.name} has been muted.", color=diablocolor)
        await ctx.send(embed=embed)
    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed=discord.Embed(description="Please specify a user to mute.", color=0xCD1F1F)
            await ctx.send(embed=embed, delete_after=2.0)
        elif isinstance(error, commands.BadArgument):
            embed=discord.Embed(description="Either tag the user you want to mute or be sure to check you wrote their name correctly.", color=0xCD1F1F)
            await ctx.send(embed=embed, delete_after=2.0)

    # unmute
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx, member : discord.Member):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if muted_role not in member.roles:
            embed = discord.Embed(description="User is not muted", color=0xCD1F1F)
            await ctx.send(embed=embed)
        else:
            await member.remove_roles(muted_role)
            embed = discord.Embed(description=f"{member.name} has been unmuted.", color=diablocolor)
            await ctx.send(embed=embed)
    @unmute.error
    async def unmute_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed=discord.Embed(description="Please specify a user to unmute.", color=0xCD1F1F)
            await ctx.send(embed=embed, delete_after=2.0)
        elif isinstance(error, commands.BadArgument):
            embed=discord.Embed(description="Either tag the user you want to mute or be sure to check you wrote their name correctly.", color=0xCD1F1F)
            await ctx.send(embed=embed, delete_after=2.0)

    # Kick command
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member : discord.Member, *, reason=None):
        await member.kick(reason=f'{ctx.author.name}#{ctx.author.discriminator}: {reason}')
        embed=discord.Embed(title=f":boot: **{member}** `{member.id}` Kicked", description=f"{member} was kicked for {reason}", color=diablocolor)
        await ctx.send(embed=embed)
    @kick.error
    async def kick_error(self, ctx, error):
            if isinstance(error, commands.MissingRequiredArgument):
                embed=discord.Embed(description=":octagonal_sign: Please specify a user to kick.", color=0xCD1F1F)
                await ctx.send(embed=embed, delete_after=2.0)
            elif isinstance(error, commands.BadArgument):
                embed=discord.Embed(description=":octagonal_sign: Either tag the user you want to kick or be sure to check you wrote their name correctly.", color=0xCD1F1F)
                await ctx.send(embed=embed, delete_after=2.0)

    # Warn
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(rate=1, per=3.5, type=commands.BucketType.user)
    async def warn(self, ctx, member : discord.Member, *, reason=None):
        if reason is None:
            embed = discord.Embed(description=f":octagonal_sign: Please provide a reason.", color=0xCD1F1F)
            await ctx.send(embed=embed)
        elif member == ctx.author:
            embed = discord.Embed(description=f"Why are you warning yourself? :thinking:", color=0x8636d1)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                description=f"You have been warned in **{ctx.guild.name}**",
                color=diablocolor
            )
            embed.add_field(name="Reason", value=str(reason))
            embed.set_author(name=f'Warning', url=member.avatar_url)
            await member.send(embed=embed)

            embed2 = discord.Embed(
                description=f"{member} has been warned.",
                color=diablocolor
            )
            embed2.add_field(name="Reason", value=str(reason))
            embed2.set_author(name=f'{member} Warned', url=member.avatar_url)
            await ctx.send(embed=embed2)

            warning = {"userid":member.id}
            collection.insert_one(warning)
    @warn.error
    async def warn_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(description=":octagonal_sign: Please specify a user to warn.", color=0xCD1F1F)
            await ctx.send(embed=embed, delete_after=2.0)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(description=":octagonal_sign: Either tag the user you want to warn or be sure to check you wrote their name correctly.", color=0xCD1F1F)
            await ctx.send(embed=embed, delete_after=2.0)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)
    async def warnings(self, ctx, member : discord.Member):
        infractions = collection.count_documents({"userid":member.id})
        if infractions > 1:
            embed = discord.Embed(title=f":warning: Infractions:", description=f"**{member.name}** has **{infractions} warnings**", color=diablocolor)
            embed.add_field(name="NOTE:", value="Currently Diablo does NOT have a server-specific warnings count. The warning you see accounts for all warnings a person has.", inline=False)
            await ctx.send(embed=embed)
        elif infractions == 1:
            embed = discord.Embed(title=f":warning: Infractions:",  description=f"**{member.name}** has **1 warning**", color=diablocolor)
            embed.add_field(name="NOTE:", value="Currently Diablo does NOT have a server-specific warnings count. The warning you see accounts for all warnings a person has.", inline=False)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title=f":warning: Infractions:", description=f"**{member.name}** has **0 warnings** :tada:", color=diablocolor)
            embed.add_field(name="NOTE:", value="Currently Diablo does NOT have a server-specific warnings count. The warning you see accounts for all warnings a person has.", inline=False)
            await ctx.send(embed=embed)

    @tasks.loop(hours=730.001)
    async def warnings_delete(self):
        delete_infractions = collection.delete_many({})

    @warnings.error
    async def warnings_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(description=":octagonal_sign: Please specify a user to check warnings of.", color=0xCD1F1F)
            await ctx.send(embed=embed, delete_after=2.0)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed( description=":octagonal_sign: Either tag the user you want to check warnings of or check you wrote their name correctly.", color=0xCD1F1F)
            await ctx.send(embed=embed, delete_after=2.0)

    # Ban
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member : discord.Member, *,  reason=None):
        await member.ban(reason=f'{ctx.author.name}#{ctx.author.discriminator}: {reason}')
        embed=discord.Embed(title=f"**{member}** `{member.id}` Banned", description=f"{member} was banned for {reason}", color=diablocolor)
        await ctx.send(embed=embed)
    @ban.error
    async def ban_error(self, ctx, error):
            if isinstance(error, commands.MissingRequiredArgument):
                embed=discord.Embed(description="Please specify a user to ban.", color=0xCD1F1F)
                await ctx.send(embed=embed, delete_after=2.0)
            elif isinstance(error, commands.BadArgument):
                embed=discord.Embed(description="Either tag the user you want to ban or be sure to check you wrote their name correctly.", color=0xCD1F1F)
                await ctx.send(embed=embed, delete_after=2.0)

    # unban
    @commands.command()
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
                await ctx.send(embed=embed)
                return
    @unban.error
    async def unban_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed=discord.Embed(description="Please specify a user to unban.", color=0xCD1F1F)
            await ctx.send(embed=embed, delete_after=2.0)
        elif isinstance(error, commands.BadArgument):
            embed=discord.Embed(description="Make sure you wrote the user name and discriminator (tagline) correctly.", color=0xCD1F1F)
            await ctx.send(embed=embed, delete_after=2.0)

    # Purge (clear) command
    @commands.command(aliases=['clear'])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(rate=1, per=6.5, type=commands.BucketType.user)
    async def purge(self, ctx, amount=1):
        if not amount > 100 and amount >= 0:
            await ctx.channel.purge(limit=amount)
            embed = discord.Embed(description=f"{amount} messages cleared.", color=diablocolor)
            await ctx.send(embed=embed, delete_after=2.0)
        elif amount < 0:
            embed = discord.Embed(description=f"That isn't possible, {ctx.author}.", color=0x8636d1)
            await ctx.send(embed=embed, delete_after=2.0)
        elif amount > 100:
            embed = discord.Embed(description=f":octagonal_sign: **Purge limit cannot exceed 100.**", color=0xFF0000)
            await ctx.send(embed=embed, delete_after=2.0)
    @purge.error
    async def purge_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            embed = discord.Embed(description="The amount you have inputted is invalid, please retry.", color=0xCD1F1F)
            await ctx.send(embed=embed, delete_after=2.0)

def setup(client):
    client.add_cog(Moderation(client))
