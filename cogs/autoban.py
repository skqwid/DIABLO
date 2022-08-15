import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
from discord.commands import slash_command
from pymongo import MongoClient
import datetime
from utils import default
import asyncio

config = default.get("config.json")

cluster = MongoClient(config.mongoKey)
db = cluster["DIABLO"]
collection = db["Offender List"]

diablocolor = 0x1551b3

class AutoBan(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.wait_until_ready()
        await self.bloat_cleaner.start()

    @commands.slash_command(name="diablobans", description="Creates the DIABLO autoban logging channel", guild_only=True)
    @commands.has_permissions(administrator=True)
    async def diablobans(self, ctx):
        bans_channel = discord.utils.get(ctx.guild.text_channels, name='diablobans')
        if not bans_channel:
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(send_messages=False)
            }
            await ctx.guild.create_text_channel(
                name="diablobans",
                topic="Lists the offenders that join the server. :warning: MIGHT BE NSFW, DISABLE AT OWN RISK.",
                overwrites=overwrites,
                nsfw=True
            )
            embed = discord.Embed(
                description=":thumbsup: Channel successfully created. The server will be notified if an offender joins.",
                color=diablocolor,
                timestamp=datetime.datetime.utcnow()
            )
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                description=':octagonal_sign:  A diablobans channel already exists.',
                color=0xCD1F1F)
            await ctx.respond(embed=embed)
    @diablobans.error
    async def diablobans_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(title=":octagonal_sign: Something went wrong", description=f'```{error}```', color=0xCD1F1F)
            embed.set_footer(text="If this error persists, contact us here: https://github.com/incipious/DIABLO/issues")
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(title=":octagonal_sign: Something went wrong", description=f'```{error}```', color=0xCD1F1F)
            embed.set_footer(text="If this error persists, contact us here: https://github.com/incipious/DIABLO/issues")
            await ctx.respond(embed=embed)

    # Automatic ban on database offenders, triggered by user join.
    @commands.Cog.listener()
    async def on_member_join(self, member : discord.Member):
        gbr = open(f"global_bans.txt", "r")
        gbr_num = int(gbr.read())
        offense = collection.find_one({"userid":member.id})

        if not member.guild.id == 938928674294628443:
            if offense is not None:
                appeal_embed = discord.Embed(
                    title="You cannot join this server.",
                    description="You are recognized as an offender, or someone who is deemed to be in violation of our guidelines, which has signifant "
                                "overlap with international and US federal law, as well as Discord TOS."
                )
                appeal_embed.add_field(name='Reason', value=str(offense["reason"]), inline=False)
                appeal_embed.set_footer(
                    text='If you believe you were wrongfully added to DIABLO per the reason provided, you are entitled to a review by our appeals panel. Simply join the server I sent you and review the Appeals Guidelines before requesting an appeal.')
                await member.send(embed=appeal_embed)
                appeals_link = await self.client.get_guild(config.appealsGuild).get_channel(938943732240220161).create_invite(max_age=0, max_uses=1, reason=f'Created for appellant {member.name}#{member.discriminator} | {member.id}')
                await member.send(appeals_link)

                await member.ban(reason=f'Diablo Autoban - {offense["reason"]}')

                with open(f"global_bans.txt", "w") as gb:
                    gb.write(str(int(gbr_num) + 1))
                print(f'{member.name} was banned in {member.guild.name}')

                gbr.close()

                bans_channel = discord.utils.get(member.guild.text_channels, name='diablobans')
                if bans_channel is None:
                    overwrites = {
                        member.guild.default_role: discord.PermissionOverwrite(send_messages=False)
                    }
                    bans_channel = await member.guild.create_text_channel(
                        name="diablobans",
                        topic="Lists the offenders that join the server. :warning: MIGHT BE NSFW, DISABLE AT OWN RISK.",
                        overwrites=overwrites,
                        nsfw=True
                    )

                embed = discord.Embed(
                    title="DIABLO prevented a predator from entering this server.",
                    description=f'**{member}** has attempted to join the server, but was blocked by Diablo.',
                    timestamp=member.joined_at,
                    color=diablocolor
                )
                embed.set_thumbnail(url=member.avatar_url)
                embed.add_field(name='Reason', value=str(offense["reason"]), inline=False)
                await bans_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            bans_channel = discord.utils.get(ctx.guild.text_channels, name='diablobans')
            if bans_channel is None:
                overwrites = {
                    ctx.guild.default_role: discord.PermissionOverwrite(send_messages=False)
                }
                bans_channel = await ctx.guild.create_text_channel(
                    name="diablobans",
                    topic="Lists the offenders that join the server. :warning: MIGHT BE NSFW, DISABLE AT OWN RISK.",
                    overwrites=overwrites,
                    nsfw=True
                )

            embed = discord.Embed(
                title="Diablo is missing permissions",
                description="An offender just joined this server but Diablo is unable to take action. "
                            "Please ensure Diablo's role is above all members and that Diablo is able to ban players.",
                color=0xFFFF00
            )
            await bans_channel.send(embed=embed)

    @commands.slash_command(name="scan", description="Scan your server for potential predators.", guild_only=True)
    @commands.cooldown(rate=1, per=300, type=commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def scan(self, ctx):
        gbr = open(f"global_bans.txt", "r")
        gbr_num = int(gbr.read())

        server_members = [member.id for member in ctx.guild.members]
        check_offenses = [collection.find_one({"userid": int(member)}) for member in server_members]
        offense = collection.find({"userid": {"$in": server_members}})

        embed = discord.Embed(
            title="Diablo Scan",
            description="Diablo Scan could take a while depending on server size. "
                        "Once Diablo Scan has concluded, the outcome will depend on the method you selected. "
                        "Please react with the emoji that denotes your preferred method of scan. ",
            color=diablocolor,
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(text="Please be patient as Diablo Scan operates.")

        notifButton = Button(label="Notify", style=discord.ButtonStyle.blurple, emoji="❗")
        banButton = Button(label="Autoban", style=discord.ButtonStyle.blurple, emoji="🔨")

        finishEmbed = discord.Embed(
            title="✅ Diablo Scan Completed",
            description="Results may have been sent to your DMs.",
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow()
        )

        async def notifCallback(interaction):
            if sum(x is not None for x in check_offenses) > 0:
                for person in offense:
                    member_object = (discord.utils.get(ctx.guild.members, id=person["userid"]))

                    if offense is not None:
                        embed = discord.Embed(
                            title="Offender Spotted",
                            description=f'**{member_object.name}** (ID: {member_object.id}) is present on Diablo database. '
                                        f'We highly encourage you take action upon these findings.',
                            color=diablocolor,
                            timestamp=datetime.datetime.utcnow()
                        )
                        embed.add_field(name='Reason', value=str(person["reason"]), inline=False)
                        await ctx.author.send(embed=embed)
                        await interaction.response.edit_message(embed=finishEmbed, view=None)
            elif sum(x is not None for x in check_offenses) == 0:
                await interaction.response.edit_message(embed=finishEmbed, view=None)

                embed = discord.Embed(
                    title="Scan",
                    description='Server-wide scan by Diablo has yielded no offenders :tada:',
                    color=discord.Colour.green(),
                    timestamp=datetime.datetime.utcnow()
                )
                await ctx.author.send(embed=embed)

        async def banCallback(interaction):
            if sum(x is not None for x in check_offenses) > 0:
                for person in offense:
                    member_object = (discord.utils.get(ctx.guild.members, id=person["userid"]))

                    if offense is not None:
                        bans_channel = discord.utils.get(ctx.guild.text_channels, name='diablobans')
                        if bans_channel is None:
                            overwrites = {
                                ctx.guild.default_role: discord.PermissionOverwrite(send_messages=False)
                            }
                            bans_channel = await ctx.guild.create_text_channel(
                                name="diablobans",
                                topic="Lists the offenders that join the server. :warning: MIGHT BE NSFW, DISABLE AT OWN RISK.",
                                overwrites=overwrites,
                                nsfw=True
                            )

                        await member_object.ban(reason=f'Diablo Scan - {person["reason"]}')

                        gb = open(f"global_bans.txt", "w")
                        gb.write(str(int(gbr_num) + 1))
                        gb.close()
                        gbr.close()

                        embed = discord.Embed(
                            title="Offender Spotted",
                            description=f'**{member_object.name}** (ID: {member_object.id}) was spotted by Diablo and was promptly banned.',
                            color=diablocolor,
                            timestamp=datetime.datetime.utcnow()
                        )
                        embed.add_field(name='Reason', value=str(person["reason"]), inline=False)
                        await bans_channel.send(embed=embed)
                        await interaction.response.edit_message(embed=finishEmbed, view=None)
            elif sum(x is not None for x in check_offenses) == 0:
                await interaction.response.edit_message(embed=finishEmbed, view=None)

                embed = discord.Embed(
                    title="Scan",
                    description='Server-wide scan by Diablo has yielded no offenders :tada:',
                    color=discord.Colour.green(),
                    timestamp=datetime.datetime.utcnow()
                )
                await ctx.author.send(embed=embed)

        notifButton.callback = notifCallback
        banButton.callback = banCallback

        view = View(notifButton, banButton)
        startEmbed = await ctx.send(embed=embed, view=view)

    @scan.error
    async def scan_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(title="Something went wrong... ⚠", description=f"```{error}```", color=0xCD1F1F)
            embed.set_footer(text="If this error persists, contact us here: https://github.com/incipious/DIABLO/issues")
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Something went wrong... ⚠", description=f'```{error}```', color=0xCD1F1F)
            embed.set_footer(text="If this error persists, contact us here: https://github.com/incipious/DIABLO/issues")
            await ctx.respond(embed=embed)

    # Total number of Diablo offenders
    @slash_command(name="offenders", description="Shows the total number of offenders on our database", guild_only=True)
    async def offenders(self, ctx):
        with open(f"global_bans.txt", "r") as gb:
            embed = discord.Embed(
                title=":axe: Offenders",
                description=f'There are exactly **{collection.count_documents({})} offenders** on Diablo.',
                color=diablocolor,
                timestamp=datetime.datetime.utcnow()
            )
            embed.add_field(name="Global Bans (As of Oct 2021)", value=str(int(gb.read())))
            await ctx.respond(embed=embed)

    @tasks.loop(hours=24.0)
    async def bloat_cleaner(self):
        await self.client.wait_until_ready()

        day_of_month = int(datetime.date.today().strftime("%d"))

        offenderList = collection.find()
        cleanedList = []

        if day_of_month == int(28):
            print("Automatic database bloat cleaner initiated.")  # Just to see if it works in logs.
            for offender in offenderList:
                try:
                    discordable = await self.client.fetch_user(int(offender['userid']))
                    await asyncio.sleep(.8)
                except discord.NotFound:
                    cleanedList.append(int(offender['userid']))

            print(f'{int(len(cleanedList))} IDs are invalid, deletion process commencing.')

            for x in cleanedList:
                print(collection.delete_one({"userid":int(x)}))
                await asyncio.sleep(1)

            cleanedList.clear()
            print("Database bloat cleaning process complete. See you next month.")

def setup(client):
    client.add_cog(AutoBan(client))
