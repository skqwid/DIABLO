import discord
from discord.ext import commands, tasks
import datetime
from pymongo import MongoClient
from utils import default
import asyncio
import operator

config = default.get("config.json")
diablocolor = 0x1551b3

cluster = MongoClient(config.mongoKey)
db = cluster["DiabloReporting"]

class Admin(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.wait_until_ready()
        #await self.vote_reminder.start()

    # Just for the Diablo Server
    @tasks.loop(hours=24.0)
    async def vote_reminder(self):
        await self.client.wait_until_ready()

        guild_id = int(config.diabloMainServer)
        vote_channel = self.client.get_guild(guild_id).get_channel(760943238001197117)
        vote_role = self.client.get_guild(guild_id).get_role(914621380002209834)

        await vote_channel.send(f'{vote_role.mention} 🗣 Daily reminder to vote for Diablo on Top.GG! https://top.gg/bot/751888323517349908/vote ')

    @commands.command(name='Server Names', aliases=['sn'], hidden=True)
    @commands.is_owner()
    async def server_names(self, ctx):
        date = datetime.datetime.utcnow()
        filename = date.strftime("%m-%d-%y")

        with ctx.channel.typing():

            try:
                with open(f"{str(filename)}.csv", "a") as f:
                    f.write("name,id,members" + "\n")

                    for guild in self.client.guilds:
                        alt_name = str(guild.name).replace('"', "Q")

                        data = f'{str(alt_name)},{int(guild.id)},{(len(guild.members))}'
                        f.write(data + "\n")
                        await asyncio.sleep(1)
            except:
                pass
            try:
                await ctx.send(file=discord.File(f"{str(filename)}.csv"))
            except:
                pass

    @commands.command(hidden=True)
    @commands.is_owner()
    async def zeta(self, ctx):
        sus_words = ["ζ", "zeta", "zoo"]
        embed = discord.Embed(
            title="Zeta Symbol Identifier",
            color=discord.Colour.purple()
        )

        await ctx.send("I am currently searching every server I am present in for any individuals with zoophile name identifiers. "
                       "This may take a while.")

        with ctx.channel.typing():
            for guild in self.client.guilds:
                member_list = [member for member in guild.members]
                for person in member_list:
                    check_sus_name = [operator.contains(str(person.name).lower(), str(x).lower()) for x in sus_words]
                    check_sus_nick = [operator.contains(str(person.nick).lower(), str(x).lower()) for x in sus_words]
                    if True in check_sus_name or True in check_sus_nick:
                        embed.add_field(name=f"{guild.name} | {person.name}#{person.discriminator} | Server Nickname: {person.nick}", value=str(person.id), inline=False)
                    else:
                        pass

                    await asyncio.sleep(0.35)

                await asyncio.sleep(0.95)
                # I should probably take Harvard CS50 to learn how to rip apart a textbook

            await ctx.author.send("Done!")
            await ctx.send(embed=embed)

    @commands.command(hidden=True, aliases=['radd'])
    @commands.is_owner()
    async def report_access_add(self, ctx, u : discord.User):
        report_access = db["Report Access"]
        if report_access.find_one({"userid":int(u.id)}) is None:
            x = report_access.insert_one({"userid":int(u.id)})
            print(x)
            await ctx.send(f'{u.name} given report access.')
        else:
            await ctx.send("Cannot do that.")

    @commands.command(hidden=True, aliases=['rarm'])
    @commands.is_owner()
    async def report_access_remove(self, ctx, u : discord.User):
        report_access = db["Report Access"]
        if report_access.find_one({"userid": int(u.id)}) is not None:
            x = report_access.delete_one({"userid":int(u.id)})
            print(x)
            await ctx.send(f'{u.name} revoked report access.')
        else:
            await ctx.send("Cannot do that.")

    @commands.command(hidden=True, aliases=["svc"])
    @commands.is_owner()
    async def server_validity_checker(self, ctx, *, g: discord.Guild):
        g_link = await self.client.get_guild(g.id).get_channel(g.text_channels[0].id).create_invite(max_age=60, max_uses=1)
        await ctx.author.send(str(g_link))

def setup(client):
    client.add_cog(Admin(client))