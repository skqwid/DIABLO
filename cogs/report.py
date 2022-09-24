import discord
from discord import Option
from discord.ext import commands
from discord.ui import Button
from discord.commands import slash_command
from pymongo import MongoClient
from datetime import datetime
import asyncio
from utils import default

config = default.get("config.json")

cluster = MongoClient(config.mongoKey)
db = cluster["DiabloReporting"]
ddb = cluster["DIABLO"]
report_access = db["Report Access"]

diablocolor = 0x1551b3
report_channel = config.testReportID

class Report(commands.Cog):

    def __init__(self, client):
        self.client = client

    # GENERAL REPORTING
    @commands.command(name='report', aliases=['r'])
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.user)
    @commands.dm_only()
    async def report(self, ctx, u : discord.User):
        blocklist = db["ReportBlocklist"]
        blocked = blocklist.find_one({"userid":int(ctx.author.id)})
        exempt_list = db["ExemptIDs"]
        offender_list = ddb["Offender List"]
        offended = offender_list.find_one({"userid":int(ctx.author.id)})

        if offender_list.find_one({"userid":int(u.id)}) is None and u.bot is False:
            if blocked is None and offended is None:
                embed = discord.Embed(
                    description="Please follow all instructions carefully throughout this whole process to ensure that your report is sufficient."
                                "\n\n**First step:** Please provide a brief reason for your report against this individual. "
                                "A good thing to keep in mind is to imagine yourself writing a headline for a news story. "
                                "Please try to keep it brief, yet descriptive enough.",
                    color=diablocolor
                )
                embed.set_author(name='Thank you for initiating a report!', icon_url=ctx.author.display_avatar.url)
                embed.set_footer(text='If you ever want to stop the report process at any time, message me "stop."'
                                      '\nPlease ensure your reason has at least 5 characters in it.')
                await ctx.author.send(embed=embed)

                def frt_seq(m):
                    return m.guild is None and m.author == ctx.author

                try:
                    reason_reply = await self.client.wait_for('message', check=frt_seq, timeout=60)
                except asyncio.TimeoutError:
                    embed = discord.Embed(
                        description="To resubmit, activate the sequence by messaging me `d.report`",
                        color=0xFF0000
                    )
                    embed.set_author(name='It appears you have timed out.', icon_url=ctx.author.display_avatar.url)
                    await ctx.send(embed=embed)
                    return
                else:
                    if len(reason_reply.content) >= 5:
                        embed = discord.Embed(
                            description="Next, please provide **1 piece of image evidence** to reinforce your claim.",
                            color=diablocolor
                        )
                        embed.set_author(name='Report', icon_url=ctx.author.display_avatar.url)
                        embed.set_footer(text='File must be a PNG, JPG, or JPEG. Only images allowed.')
                        await ctx.author.send(embed=embed)

                        def send_proof(m):
                            if m.guild is None and m.author == ctx.author:
                                for image in m.attachments:
                                    if image.filename.endswith(".png") or image.filename.endswith(
                                            ".jpg") or image.filename.endswith(".jpeg"):
                                        return True
                                    else:
                                        return False

                        try:
                            sent_proof = await self.client.wait_for('message', check=send_proof, timeout=120)
                        except asyncio.TimeoutError:
                            embed = discord.Embed(
                                description="To resubmit, activate the sequence by messaging me `d.report`",
                                color=0xFF0000
                            )
                            embed.set_author(name='It appears you have timed out.', icon_url=ctx.author.display_avatar.url)
                            await ctx.send(embed=embed)
                            return
                        else:
                            if sent_proof is not None:
                                for image in sent_proof.attachments:
                                    embed = discord.Embed(
                                        color=diablocolor,
                                        description="At this time, you are given an additional 10 minutes to write a comprehensive explanation as to why you are reporting this person "
                                                    "or would like to add on any additional information not specificed in your reason. "
                                                    "It is recommended you try to explain the evidence you provided "
                                                    "and its correlation to your reason to the best of your ability, or else your report may be rejected on the grounds that not enough "
                                                    "evidence has been provided, or other reasons."
                                                    "\n\n**If there is nothing else to add, you can skip this just by messaging me with anything (except images).**"
                                    )
                                    embed.set_author(name='Additional Information', icon_url=ctx.author.display_avatar.url)
                                    embed.set_footer(text="Bot will timeout after 10 minutes if you need time to write an explanation.")
                                    await ctx.send(embed=embed)

                                    def additional_info(m):
                                        return m.guild is None and m.author == ctx.author

                                    try:
                                        more_info = await self.client.wait_for('message', check=additional_info, timeout=600)
                                    except asyncio.TimeoutError:
                                        embed = discord.Embed(
                                            description="To resubmit, activate the sequence by messaging me `d.report`",
                                            color=0xFF0000
                                        )
                                        embed.set_author(name='It appears you have timed out.',
                                                         icon_url=ctx.author.display_avatar.url)
                                        await ctx.send(embed=embed)
                                        return
                                    else:
                                        if more_info is not None:
                                            embed = discord.Embed(
                                                color=diablocolor,
                                                title="Thank you for submitting your report.",
                                                description="We will get right to work to determine if this user violates our guidelines and/or Discord TOS. "
                                                            "You may be notified on the status of your report once a decision is made."
                                            )
                                            await ctx.send(embed=embed)

                                            embed2 = discord.Embed(
                                                title="🔔 New Report",
                                                color=0x6632a8
                                            )
                                            embed2.add_field(name='User ID:', value=str(u.id), inline=False)
                                            embed2.add_field(name='Reason:', value=reason_reply.content, inline=False)
                                            embed2.add_field(name='Additional Info:', value=more_info.content, inline=False)
                                            embed2.add_field(name='User ID of Reporter', value=ctx.author.id, inline=False)
                                            embed2.set_image(url=image.url)
                                            embed2.set_thumbnail(url=ctx.author.display_avatar.url)
                                            embed2.set_footer(
                                                text='Emoji Key:\n✅ = Accept\n❌ = Reject\n⛔ = Block reporter from submitting future reports'
                                                     '\n🔄 = Add reporter to Diablo (Use only in extreme cases)')

                                            admin_embed = await self.client.get_guild(config.diabloMainServer).get_channel(config.reportChannelID).send(embed=embed2)
                                            await self.client.get_guild(config.diabloMainServer).get_channel(config.reportChannelID).send(f'`For Mobile:` {str(u.id)}')

                                            for y in ["✅", "❌", "⛔", "🔄"]:
                                                await admin_embed.add_reaction(str(y))

                                            def reaction_check(rctn, usr):
                                                return report_access.find_one({"userid": int(usr.id)}) is not None

                                            rctn, usr = await self.client.wait_for("reaction_add", check=reaction_check)

                                            if report_access.find_one({"userid": int(usr.id)}) is not None:
                                                if str(rctn) == '✅':
                                                    if exempt_list.find_one({"userid": int(ctx.author.id)}) is None or offender_list.find_one({"userid": int(ctx.author.id)}) is None:
                                                        x = offender_list.insert_one({"userid": int(u.id), "reason": str(reason_reply.content)})
                                                        print(x)

                                                        embed = discord.Embed(
                                                            title="✅ Report Update",
                                                            description="Your report has been accepted and processed. "
                                                                        "Thank you for making Discord a safer place for all.",
                                                            color=discord.Colour.green()
                                                        )
                                                        await ctx.send(embed=embed)

                                                        embed_edit = discord.Embed(
                                                            title=f"Report Accepted by {usr.name}#{usr.discriminator}",
                                                            color=discord.Colour.green()
                                                        )
                                                        embed_edit.add_field(name='User ID:', value=str(u.id))
                                                        embed_edit.add_field(name='Reason:', value=reason_reply.content)
                                                        embed_edit.set_footer(text=f"Reporter: {ctx.author.name}#{ctx.author.discriminator} | {ctx.author.id}", icon_url=ctx.author.display_avatar.url)

                                                        await admin_embed.edit(embed=embed_edit)
                                                elif str(rctn) == '❌':
                                                    embed = discord.Embed(
                                                        title="❌ Report Update",
                                                        description="Your report has been rejected. "
                                                                    "Your report might not fit our guidelines or may be missing information. "
                                                                    "Please recheck your submission and restart if necessary.",
                                                        color=discord.Colour.red()
                                                    )
                                                    await ctx.send(embed=embed)

                                                    embed_edit = discord.Embed(
                                                        title=f"Report Rejected by {usr.name}#{usr.discriminator}",
                                                        color=discord.Colour.red()
                                                    )
                                                    embed_edit.add_field(name='User ID:', value=str(u.id))
                                                    embed_edit.add_field(name='Reason:', value=reason_reply.content)
                                                    embed_edit.set_footer(
                                                        text=f"Reporter: {ctx.author.name}#{ctx.author.discriminator} | {ctx.author.id}",
                                                        icon_url=ctx.author.display_avatar.url)

                                                    await admin_embed.edit(embed=embed_edit)
                                                elif str(rctn) == "⛔":
                                                    if exempt_list.find_one({"userid": int(ctx.author.id)}) is None:
                                                        x = blocklist.insert_one({"userid": int(ctx.author.id)})
                                                        print(x)

                                                        embed_edit = discord.Embed(
                                                            title=f"Reporter Blocked by {usr.name}#{usr.discriminator}",
                                                            color=0xdbeb34
                                                        )
                                                        embed_edit.set_footer(
                                                            text=f"Reporter: {ctx.author.name}#{ctx.author.discriminator} | {ctx.author.id}",
                                                            icon_url=ctx.author.display_avatar.url)

                                                        await admin_embed.edit(embed=embed_edit)
                                                    await admin_embed.delete()
                                                elif str(rctn) == "🔄":
                                                    if exempt_list.find_one({"userid": int(ctx.author.id)}) is None or offender_list.find_one({"userid": int(ctx.author.id)}) is None:
                                                        x = offender_list.insert_one({"userid": int(ctx.author.id), "reason": "Automatically added by Report"})
                                                        print(x)
                                                    embed_edit = discord.Embed(
                                                        title=f"Reporter Switcheroo'd by {usr.name}#{usr.discriminator}",
                                                        color=0x902edb
                                                    )
                                                    embed_edit.set_footer(
                                                        text=f"Reporter: {ctx.author.name}#{ctx.author.discriminator} | {ctx.author.id}",
                                                        icon_url=ctx.author.display_avatar.url)

                                                    await admin_embed.edit(embed=embed_edit)

                    elif str(reason_reply.content.lower) == "stop":
                        embed = discord.Embed(
                            description="Feel free to submit a new report anytime!",
                            color=diablocolor
                        )
                        embed.set_author(name='Report', icon_url=ctx.author.display_avatar.url)
                        await ctx.send(embed=embed)
                        return
                    else:
                        embed = discord.Embed(
                            description="There has been an error with your reason submission. "
                                        "Please try again. Restart the sequence by writing `d.r` or `d.report`",
                            color=0xFF0000
                        )
                        embed.set_author(name='An error has occurred.', icon_url=ctx.author.display_avatar.url)
                        embed.set_footer(text='If any issues arise, you can refer to our support server: https://discord.gg/YvWwnea')
                        await ctx.send(embed=embed)
                        return
        else:
            embed = discord.Embed(
                description="This individual may not permitted to be reported or may already appear on our database. "
                            "If you believe this is a mistake, please ensure the individual's User ID is correct.",
                color=0xFF0000
            )
            embed.set_author(name='You cannot report this individual.', icon_url=ctx.author.display_avatar.url)
            embed.set_footer(text='If any issues arise, you can refer to our support server: https://discord.gg/YvWwnea')
            await ctx.send(embed=embed)

    @report.error
    async def report_error(self, ctx, error):
        if isinstance(error, commands.PrivateMessageOnly):
            embed = discord.Embed(
                title="Error: Private Messages Only",
                description="The report function is only available through DMs. "
                            "Please privately message me with `d.report` or `d.r` with the a valid **User ID** of the person you are reporting to begin"
                            " the report process.",
                color=discord.Colour.orange()
            )
            embed.add_field(name="Example", value="```d.report 12345678901011121314```")
            await ctx.send(embed=embed)
        elif isinstance(error, commands.UserNotFound):
            embed = discord.Embed(
                title="Error: User Not Found",
                description="The User ID you inputted is unavailable. "
                            "Please check to see if the User ID you inputted is correct and restart the command.",
                color=discord.Colour.red()
            )
            await ctx.send(embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="Error: Missing Required Argument",
                description="To start the report procedure, you **must** input a **valid** User ID. "
                            "Please restart the procedure and input a proper User ID.",
                color=discord.Colour.red()
            )
            embed.add_field(name="Example", value="```d.report 123456789010111213```")
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title=":octagonal_sign: Something went wrong", description=f'```{error}```', color=0xCD1F1F)
            await ctx.send(embed=embed)

        # BLOCKLIST
    @slash_command(name="block", description="Block a user from submitting future reports. (For users with report access)", guild_only=True, guild_ids=config.guildCocktail)
    async def block(self, ctx, userid):
        u = await self.client.fetch_user(int(userid))
        blocklist = db["ReportBlocklist"]
        if report_access.find_one({"userid":int(ctx.author.id)}) is not None:
            try:
                if u.bot is False:
                    print(blocklist.insert_one({"userid":int(u.id)}))
                    embed = discord.Embed(
                        description=f'**User ({u.id})** added to blocklist :white_check_mark:',
                        color=0xFFC300
                    )
                    embed.set_author(name='Blocklist', icon_url=ctx.author.display_avatar.url)
                    await ctx.respond(embed=embed)
                else:
                    embed = discord.Embed(
                        description=f'Unable to add user to blocklist. '
                                    f'Check to see if user is a bot.',
                        color=discord.Colour.red()
                    )
                    embed.set_author(name='Blocklist', icon_url=ctx.author.display_avatar.url)
                    await ctx.respond(embed=embed)
            except:
                pass
    @block.error
    async def block_error(self, ctx, error):
        if isinstance(error, commands.UserNotFound):
            embed = discord.Embed(title="Something went wrong... ⚠", description=f'```{error}```', color=0xCD1F1F)
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(title="Something went wrong... ⚠", description=f'```{error}```', color=0xCD1F1F)
            await ctx.respond(embed=embed)

    # ADD TO DIABLO
    @slash_command(name="add", description="Manually add a user to the report database. (For users with access)", guild_only=True, guild_ids=config.guildCocktail)
    async def add(self, ctx, userid, *, reason : Option(str, description="Reason they are being added to DIABLO DB")):
        db_0 = cluster["DIABLO"]
        offender_list = db_0["Offender List"]
        exempt_list = db["ExemptIDs"]

        discordable = await self.client.fetch_user(int(userid))

        if report_access.find_one({"userid": int(ctx.author.id)}) is not None:
            is_on_list = offender_list.find_one({"userid": int(discordable.id)})
            is_exempted = exempt_list.find_one({"userid": int(discordable.id)})

            if is_on_list is not None or is_exempted is not None or discordable.bot is True:
                embed_1 = discord.Embed(
                    description="Please check if User ID is correct. "
                                "May already be on the database.",
                    color=discord.Colour.red()
                )
                embed_1.set_author(name='🚫 Invalid User ID')
                embed_1.set_footer(text="Ensure that the user is not a bot. User may also be exempted from Diablo.")
                await ctx.respond(embed=embed_1)
            else:
                verified_offender = {"userid": int(discordable.id), "reason": str(reason)}
                x = offender_list.insert_one(verified_offender)
                print(x)

                embed = discord.Embed(
                    description=f':white_check_mark: Added UserID **({str(discordable.id)})**',
                    color=discord.Colour.green(),
                    timestamp=datetime.utcnow()
                )
                embed.set_author(name='Added Offender', icon_url=ctx.author.display_avatar.url)
                embed.add_field(name='User ID', value=str(discordable.id))
                embed.add_field(name='Reason', value=str(reason))
                await ctx.respond(embed=embed)
    @add.error
    async def add_error(self, ctx, error):
        if isinstance(error, commands.UserNotFound):
            embed = discord.Embed(title="Something went wrong... ⚠", description=f'```{error}```', color=0xCD1F1F)
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(title="Something went wrong... ⚠", description=f'```{error}```', color=0xCD1F1F)
            await ctx.respond(embed=embed)

    # Check User
    @commands.command(aliases=["cu"], hidden=True)
    async def check_user(self, ctx, id: discord.User):
        offender_list = ddb["Offender List"]
        exempt_list = db["ExemptIDs"]
        offended = offender_list.find_one({"userid": int(id.id)})
        if report_access.find_one({"userid": int(ctx.author.id)}) is not None:
            embed = discord.Embed(
                title="Check User",
                color=discord.Colour.blue()
            )

            embed.add_field(name="User ID", value=str(id.id))
            embed.add_field(name="User Name/Discriminator", value=f'{id.name}#{id.discriminator}')
            embed.add_field(name='Is Bot?', value=str(bool(id.bot)))
            embed.add_field(name='Created at:',
                             value=str(id.created_at.strftime(f"%A, %B %d %Y at %I:%M %p %Z")))
            embed.add_field(name='Is Bot?', value=str(bool(id.bot)))
            embed.add_field(name='Is System User?', value=str(bool(id.system)))
            embed.add_field(name='Is Banned?', value=str("Yes" if offended is not None else "No"))
            embed.add_field(name='Is Exempted?', value=str("Yes" if exempt_list.find_one({"userid":id.id}) is not None else "No"))
            embed.set_thumbnail(url=id.display_avatar.url)
            await ctx.send(embed=embed)

def setup(client):
    client.add_cog(Report(client))
