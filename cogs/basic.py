import discord
from discord import Option
from discord.ext import commands, tasks
from discord.commands import slash_command
from datetime import datetime
from pymongo import MongoClient
from utils import default

diablocolor = 0x1551b3
config = default.get("config.json")

cluster = MongoClient(config.mongoKey)
db = cluster["DIABLO"]

class Basic(commands.Cog):

    def __init__(self, client):
        self.client = client

    #Events
    @commands.Cog.listener()
    # activation procedure
    async def on_ready(self):
        await self.client.wait_until_ready()
        await self.server_count.start()

    @tasks.loop(minutes=60.0)
    async def server_count(self):
        game = discord.Activity(name=f"{len(self.client.guilds)} servers || d.help for commands", type=discord.ActivityType.watching)
        await self.client.change_presence(
            activity=game
        )

    # Message sent when Diablo joins.
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        embed=discord.Embed(
            title="Thanks for adding Diablo!",
            description=f"Thanks for adding Diablo to {guild.name}, here's some information on Diablo:",
            color=diablocolor,
            timestamp=datetime.utcnow()
        )
        embed.add_field(
            name='About Diablo',
            value='Diablo is an open-source public discord ban bot. '
                  'In short, Diablo uses data submitted by users to compile a database of offenders to protect servers.'
                  'This means anyone can report users whom they believe are breaking our guidelines (and Discord TOS) '
                  'and our moderation team will review add them to the global database of offenders.',
            inline=False
        )
        embed.add_field(
            name='Diablo Reporting',
            value="You can run the command `d.report` to report users that may be violating our guidelines."
                  "Once you fill out the submission, our mods will determine if the alleged offender breaks our guidelines and/or Discord TOS. "
                  "Our guarantee is that we will be faster than Discord's reporting.",
            inline=False
        )
        embed.add_field(
            name='Bot Setup',
            value="After Diablo has been invited into your server, the only thing you should do is elevate Diablo's role above all the server members"
                  "and have permission to ban users. "
                  "\n⚠ **Diablo will not work without having this setting.**",
            inline=False
        )
        embed.add_field(
            name='Bot Prefix',
            value="The bot prefix is: `d.`",
            inline=False
        )
        embed.set_image(url='https://i.imgur.com/Z6swN2y.png')

        for channel in guild.text_channels:
            overwrite = channel.overwrites_for(guild.default_role)
            if overwrite.send_messages is not False:
                await channel.send(embed=embed)
                break

    @slash_command(name="whois", description="Input a user to view general information about them.", guild_only=True)
    async def whois(self, ctx, member : Option(discord.Member, description="Who do you want to view information about?")):
        collection = db["Offender List"]
        if member is None:
            member = ctx.message.author

        offended = collection.find_one({"userid": int(member.id)})
        embed=discord.Embed(color=diablocolor)
        embed.set_thumbnail(url=str(member.avatar.url))
        embed.add_field(name='User ID:', value=member.id, inline=False)
        embed.add_field(name='Nickname:', value=member.display_name, inline=False)
        embed.add_field(name='Joined Server at:', value=member.joined_at.strftime(f"%A, %B %d %Y at %I:%M %p"), inline=False)
        embed.add_field(name='Created at:', value=member.created_at.strftime(f"%A, %B %d %Y at %I:%M %p"), inline=False)
        embed.add_field(name='Top Role:', value=member.top_role, inline=False)
        embed.add_field(name='Is Banned?', value=str("Yes" if offended is not None else "No"))
        embed.add_field(name='Is Bot?', value=member.bot, inline=False)
        embed.add_field(name='Boosting Since:', value=member.premium_since, inline=False)
        embed.set_author(name=f"{member}'s Information", icon_url=str(member.display_avatar.url))

        await ctx.respond(embed=embed)
    @whois.error
    async def whois_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(title="Something went wrong... ⚠", description=f"```{error}```", color=0xCD1F1F)
            embed.set_footer(text="If this error persists, contact us here: https://github.com/incipious/DIABLO/issues")
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Something went wrong... ⚠", description=f'```{error}```', color=0xCD1F1F)
            embed.set_footer(text="If this error persists, contact us here: https://github.com/incipious/DIABLO/issues")
            await ctx.respond(embed=embed)

    # about
    @slash_command(name="about", description="Provides general information about Diablo", guild_only=True)
    async def about(self, ctx):
        with open(f"global_bans.txt", "r") as gb:
            embed=discord.Embed(
                title="About Diablo",
                description="**DIABLO** is an acronym that stands for **Database Influenced Automated Ban List of Offenders.** "
                            "Its purpose is to prevent predators from joining servers protected by Diablo, preventing any potential harm to servers and their members. "
                            "Think of it as this way- what would be more efficient: curing an illness or preventing an illness? "
                            "We believe prevention is the right course of action, because we can prevent people from getting hurt. "
                            "Our job is to act as a median before some offenders are banned by Discord and even function as a potential "
                            "long term database for some offenders.",
                color=diablocolor
            )
            embed.add_field(name="Guilds", value=str(len(self.client.guilds)))
            embed.add_field(name="User per Guild", value=str(round(len(set(self.client.get_all_members())) / len(self.client.guilds))))
            embed.add_field(name="Global Bans (As of Oct 2021)", value=str(gb.read()))
            embed.set_thumbnail(url=str(self.client.user.display_avatar.url))
            await ctx.respond(embed=embed)

    @slash_command(name="ping", description="Returns latency from API to server", guild_only=True)
    async def ping(self, ctx):
        embed=discord.Embed(
            title="Ping",
            description=f'API Latency: {(round(self.client.latency * 1000))} ms',
            color=diablocolor
        )
        embed.set_thumbnail(url=str(self.client.user.display_avatar.url))
        await ctx.respond(embed=embed)

    # Source Link
    @slash_command(name="source", description="Returns the source code for the bot.", guild_only=True)
    @commands.guild_only()
    async def source(self, ctx):
        embed=discord.Embed(title="Source", url="https://github.com/incipious/DIABLO", description="Here's the source link for Diablo.", color=diablocolor)
        await ctx.respond(embed=embed)

    # Vote Command
    @slash_command(name="vote", description="Returns the vote link for the bot on top.gg.", guild_only=True)
    async def vote(self, ctx):
        embed = discord.Embed(title="Click me to vote!",
                              url="https://top.gg/bot/751888323517349908/vote",
                              description="Diablo needs large-scale usage for our mission to be effective. "
                                          "The best way you can help is by voting for us on Top.GG!",
                              color=diablocolor)
        embed.set_image(url="https://i.imgur.com/Z6swN2y.png")
        await ctx.respond(embed=embed)


def setup(client):
    client.add_cog(Basic(client))
