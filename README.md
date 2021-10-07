# DIABLO
### DIABLO - Database Influenced Automated Ban List of Offenders. 
DIABLO syncs up with our databases on predators, such as pedophiles and zoophiles, and prevents them from joining servers that have DIABLO. DIABLO relies on cutting-edge infrastructure to ban predators from your server in mere milliseconds. Keep your server safe from  any potential predators with DIABLO.

Diablo is designed to allow users to report potential offenders who have engaged in predatory behavior. Reported users are investigated by Diablo moderators before being placed on our database, which prevents them from joining servers that are protected by Diablo.

Although some predator accounts do get banned by Discord, there is still an window in which predators have the opportunity to roam and wage destruction on innocent servers and their populace. Diablo offers to act as a barrier to that window and prevents predators from harming innocent server members.

## Invite Diablo to your server:
https://top.gg/bot/751888323517349908

## Set up Diablo with ease:
When Diablo has been invited into your server, please either elevate Diablo's role above all the server members (not including admin roles, but if you want that extra edge over your admins/server mods, I'd suggest so) or give Diablo a pre-existing Bot role with ban or administrator permissions. If Diablo does not have either, then it will not be able to do its job of protecting your server. 

## How Diablo Works
Diablo's primary method of AutoBan occurs when an offender (user on the Diablo database) joins the server. If an offender joins a server, the bot will instantly detect that the offender has a presence on Diablo's database by confirming the user ID of the member with a match in our database. Accordingly, Diablo will take instant measures to prevent the offender from having the ability to interact with the server or its members by automatically removing the offender from the server prior to any potential interactions.

Diablo also has a built-in manual scan command that allows server administrators to run a specific command that will identify matches in our database, and allows administrators to select their preferred method of outcome (what will happen to users who are confirmed matches). Server administrators can select to be notified or for the bot to autoban offenders.
## Commands
### Bot Prefix: `d.`
The following is a list of commands that Diablo currently has. You can run `d.help` for a full list of commands in any server with Diablo.
#### Report
##### Bot's main function alongside commands pertaining to it.
You can report a user to DIABLO by running `d.report` or `d.r` with the User ID of the individual you are attempting to report in DIABLO's DMs (EXAMPLE: `d.report 1234567890`). You will be asked for a reason for your report, which is essentially a brief summary. You will also be required to provide one piece of image evidence and an extended explanation to ensure your report is specific and credible. Finally, once your report has been submitted, our team of moderators will work dilligently and quickly to determine if the individual you reported meets our criteria and will be added to our database. You will be notified if your submission gets accepted/rejected by our moderators. 

#### AutoBan
##### Bot's primary function alongside essential related commands.
- `diablobans` - Creates a diablobans log channel (if there is none) `[OPTIONAL: Bot will make one automatically if offender joins.]`
- `offenders` - Gives an official amount of offenders listed on our anti-predator database.
- `scan` - Manually scans the server for potential database matches. Gives server administrators a preference in database detection. (Notification or AutoBan)

#### Basic
##### Basic, fun commands for Diablo.
- `about` - Information about Diablo, such as API latency, total guilds, and average members per guild.
- `source` - Link to bot source page.
- `whois [member]` - Information about member such as name, nicknames, account creation, etc... If member paremeter left blank, it will show your information.
- `vote` - Sends a voting link for Diablo in order to engage users to help grow Diablo. 
- `whatdadogdoing` - Just a fun command that shows some adorable puppers. 

#### Moderation
##### Moderation commands for Diablo.
- `ban [member] [reason]` Bans a member from a server. Reason will default to "None" if no reason provided. 
- `unban [member#discriminator]` - Unbans a member from a server.
- `kick [member] [reason]` - Kicks a member from a server. Reason will default to "None" if no reason provided. 
- `mute [member]` - Mutes a member permanently until unmuted.
- `ummute [member]` - Unmutes a muted member.
- `warn [member] [reason]` - Gives a member an infraction for doing something bad. **WARNING: WARNS ARE GLOBAL. WARNINGS WILL ACCOUNT FOR ALL WARNINGS USER HAS RECIEVED WITH DIABLO**
- `warnings [member]` - Retrieves the amount of warnings a member has. **WARNING: WARNS ARE GLOBAL. WARNINGS WILL ACCOUNT FOR ALL WARNINGS USER HAS RECIEVED WITH DIABLO**
- `purge (or) clear [amount]`- Clears a specific amount of messages. Default is 1, limit is 100. 
