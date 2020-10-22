# Imports for bot

import discord
import json
import datetime
import time
#import asyncio
from datetime import date

# From imports for Bot

#from apscheduler.schedulers.asyncio import AsyncIOScheduler
#from apscheduler.triggers.cron import CronTrigger
from discord.ext import commands
from discord.ext.commands import has_permissions, bot_has_permissions
from typing import Optional
from utils.jsonLoader import read_json
from utils.util import (
    CreateNewTicket,
    CloseTicket,
    IsATicket,
    ReactionCreateNewTicket,
    SetupNewTicketMessage,
    CheckIfValidReactionMessage,
)
from bot_config.configure import (
    CATEGORYID,
    LOGCHANNELID,
    SETCOMMENTRANKS,
    HELPCHANNELID,
    PREFIX,
)

# Bot start up variables and events

intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix=".",
    case_insensitive=True,
    owner_id=751942027645812748, Intents=intents)
bot.remove_command("help")
self = 751942027645812748
e = discord.Embed()

today = date.today()
datev2 = time.strftime("%m-%d-%Y")


bot.new_ticket_channel_id = 755320868137205761
bot.log_channel_id = 755661364164296704
bot.category_id = 759955006123540530
bot.mod_role_id = 755688223287803914
bot.tsupp_role_id = 752008973548519445
bot.supp_role_id = 752511030139027506



# c = bot.get_channel(753442986251256018)
    #embed = discord.Embed(
        #title="*•.¸♡𝔻𝕒𝕚𝕝𝕪 ℂ𝕙𝕖𝕔𝕜 𝕀𝕟 ♡¸.•*",
        #description="Self care is one of the most important parts of the day! In an effort to help you guys take good care of yourselves, here is a daily check in!\n\n> Don't forget to do something you love! Master a hobby or just take a hot bath! If you need suggestions for self care, do the command ``.selfcare``!\n\n> When you get triggered, make sure to do grounding and self soothing to cope with the anxiety! If you need help with grounding, do the command ``.grounding``!\n\nTo complete the daily check in, answer the questions in the chat! And remember to support your peers, we are all in this together! ❤️",
        #color=0xFAB6EE,
  #  )
    #embed.set_image(url="https://i.imgur.com/aaGVkD0.png")
    #embed.set_footer(text="The Butterfly Project Support Team")
    #await c.send(embed=embed)


print("Loading code...")


@bot.event
async def on_connect():
    print("  Connected to the Discord server")


@bot.event
async def on_ready():
    print("Starting up bot...\nLogged in as: {}\nBot ID is: {})".format(self, bot.user.id))
    print("Bot is connect to guild!")


# Basic or misc commands


@bot.command()
@has_permissions(manage_messages=True)
async def say(ctx, *, msg: Optional[str] = "no context given"):
    embed = discord.Embed(title="", description=f"{msg}", color=0xFAB6EE)
    await ctx.message.delete()
    await ctx.send(embed=embed)


@bot.command()
@has_permissions(manage_messages=True)
async def repeat(ctx, *, msg):
    await ctx.message.delete()
    await ctx.send(msg)


@bot.command(pass_context=True)
@has_permissions(manage_roles=True)
async def sr(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await ctx.send("The role was successfully added to {}".format(member.mention))


@bot.command(pass_context=True)
@has_permissions(manage_roles=True)
async def rr(ctx, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)
    await ctx.send("The role was successfully removed from {}".format(member.mention))


@bot.command()
@bot_has_permissions(manage_messages=True)
async def purge(ctx, amount=10000):
    embed = discord.Embed(
        title="**Channel was purged**",
        description=f"Channel purged: {ctx.channel.mention} | {ctx.channel.id} \nChannel purged by {ctx.author.mention} | {ctx.author.id}",
        color=0xFAB6EE,
    )
    channel = ctx.channel
    log = bot.get_channel(755288699192737812)
    purgeid = ctx.channel.id
    messages = await channel.history(limit=amount, oldest_first=True).flatten()
    msgs = "".join(
        [
            f"{message.author.id} | {message.author.display_name} | {message.created_at} | {message.content}\n"
            for message in messages
        ]
    )
    with open(f"data/purgelogs/{purgeid}.txt", "w", encoding="utf8") as f:
        f.write("Purged Channel Log")
        f.write(msgs)
    await log.send(embed=embed)
    await log.send(file=discord.File(f"data/purgelogs/{purgeid}.txt"))
    await ctx.message.delete()
    await ctx.channel.purge(limit=amount, check=lambda msg: not msg.pinned)


# Peer Support Code


@bot.event
async def on_raw_reaction_add(payload):

    if payload.user_id == bot.user.id:
        return

    reaction = str(payload.emoji)
    if reaction not in ["🔒", "✅"]:
        return

    if not payload.channel_id == bot.new_ticket_channel_id and not IsATicket(
        str(payload.channel_id)
    ):
        return

    if not CheckIfValidReactionMessage(payload.message_id):
        return

    data = read_json("config")
    if payload.message_id == data["ticketSetupMessageId"] and reaction == "✅":

        await ReactionCreateNewTicket(bot, payload)

        guild = bot.get_guild(payload.guild_id)
        member = await guild.fetch_member(payload.user_id)

        channel = bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        await message.remove_reaction("✅", member)

        return

    elif reaction == "🔒":

        channel = bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        await message.add_reaction("✅")

    elif reaction == "✅":

        guild = bot.get_guild(payload.guild_id)
        member = await guild.fetch_member(payload.user_id)

        channel = bot.get_channel(payload.channel_id)
        await CloseTicket(bot, channel, member)


@bot.event
async def on_raw_reaction_remove(payload):

    if payload.user_id == bot.user.id:
        return

    reaction = str(payload.emoji)
    if reaction not in ["🔒"]:
        return

    if not payload.channel_id == bot.new_ticket_channel_id and not IsATicket(
        str(payload.channel_id)
    ):
        return

    if not CheckIfValidReactionMessage(payload.message_id):
        return

    if reaction == "🔒":

        guild = bot.get_guild(payload.guild_id)
        member = await guild.fetch_member(bot.user.id)

        channel = bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        await message.remove_reaction("✅", member)


@bot.command()
async def new(ctx, *, subject=None):
    await CreateNewTicket(bot, ctx.guild, ctx.message.author, subject=subject)


@bot.command()
async def end(ctx, *, reason=None):
    await CloseTicket(bot, ctx.channel, ctx.author, reason)


@bot.command()
@commands.has_role(bot.mod_role_id)
async def adduser(ctx, user: discord.Member):
    """
    add users to a ticket - only staff role can add users.
    """
    channel = ctx.channel
    if not IsATicket(channel.id):
        await ctx.send(
            "This is not a ticket! Users can only be added to a ticket channel"
        )
        return

    await channel.set_permissions(user, read_messages=True, send_messages=True)
    await ctx.message.delete()


@bot.command()
@commands.has_role(bot.mod_role_id)
async def removeuser(ctx, user: discord.Member):
    """
    removes users from a ticket - only staff role can remove users.
    """
    channel = ctx.channel
    if not IsATicket(channel.id):
        await ctx.send(
            "This is not a ticket! Users can only be removed from a ticket channel"
        )
        return

    await channel.set_permissions(user, read_messages=False, send_messages=False)
    await ctx.message.delete()


@bot.command()
@commands.is_owner()
async def sudonew(ctx, user: discord.Member):
    await CreateNewTicket(
        bot, ctx.guild, user, subject="Sudo Ticket Creation", message=ctx.message
    )


@bot.command()
@commands.is_owner()
async def setup(ctx):
    await SetupNewTicketMessage(bot)


# Modmail in dms

rank = 0


@bot.command()
async def getid(ctx):
    print((ctx.author.guild.id))


@bot.event
async def on_message(message):
    if message.author.id == bot.user.id:
        return
    me = client.get_user(751942027645812748)
    guild = client.get_guild(751990570989387796)
    tmod = discord.utils.get(guild.roles, name="Trial Moderator")
    mod = discord.utils.get(guild.roles, name="Moderator")
    supmod = discord.utils.get(guild.roles, name="Head Moderator")
    admin = discord.utils.get(guild.roles, name="Administrator")
    owners = discord.utils.get(guild.roles, name="Owners")
    category = discord.utils.get(guild.categories, id=int(CATEGORYID))
    await bot.process_commands(message)
    if message.guild is None and message.content.startswith(f"{PREFIX}open"):
        membersname1 = message.author.name
        membersname = membersname1.replace(" ", "")
        tchannel2 = discord.utils.get(
            guild.text_channels, name=f"report-{membersname.lower()}"
        )
        tchannel = discord.utils.get(
            guild.text_channels, name=f"report-{membersname.lower()}"
        )
        if tchannel2 == None:
            if tchannel == None:
                channel = await guild.create_text_channel(
                    f"report-{membersname.lower()}", category=category
                )
                embed = discord.Embed(
                    title=f"**New report from {membersname.lower()}**",
                    description=f"Hello {message.author.mention}, thank you for reaching out to our staff team. Someone will be with you shortly.\n\n> While you wait please give a detailed description of what you are making a report for. The more detailed you are, the faster we can get to your report.\n\nPlease be patient as our staff members are volunteers. Thank you for your time!",
                    color=0xFAB6EE,
                )
                embed.add_field(name="New report", value=message.content, inline=False)
                embed.set_footer(text=f"user ID: {message.author.id}")

                await message.author.send(embed=embed)
                await channel.send(message.author.id)
                await channel.send(
                    "**New user report has been opened!**\n <@&755688223287803914>"
                )
                await channel.send(embed=embed)
                await bot.process_commands(message)
                return
        else:
            print("message send")
            await bot.process_commands(message)
            embed = discord.Embed(
                title=f"{message.author.name} replied to your message!",
                description=message.content,
                color=0xFAB6EE,
            )
            await tchannel2.send(embed=embed)
            await message.add_reaction(emoji="\u2705")
            await bot.process_commands(message)
    else:
        if message.content.startswith("%"):
            await message.delete()
            user1 = message.author
            await bot.process_commands(message)
            global rank
            if tmod in user1.roles:
                rank = "Trial Moderator"
            if admin in user1.roles:
                rank = "Administrator"
            if supmod in user1.roles:
                rank = "Head Moderator"
            if mod in user1.roles:
                rank = "Moderator"
            if owners in user1.roles:
                rank = "Owner"
            comment = message.content
            cutcomment = comment[2:]
            if SETCOMMENTRANKS.lower() == "True":
                embed = discord.Embed(
                    title=f"Comment from {user1} - {rank}",
                    description=cutcomment,
                    color=0xFAB6EE,
                )
                embed.set_footer(text=f"user ID: {message.author.id}")
            else:
                embed = discord.Embed(
                    title=f"Comment from {user1} - Support",
                    description=cutcomment,
                    color=0xFAB6EE,
                )
                embed.set_footer(text=f"user ID: {message.author.id}")
            await message.channel.send(embed=embed)
            await bot.process_commands(message)
        else:
            if message.channel.name.startswith("report"):
                if message.content.startswith(
                    f"{PREFIX}close"
                ) or message.content.startswith(f"{PREFIX}solve"):
                    return
                else:
                    async for message2 in message.channel.history(
                        oldest_first=True, limit=1
                    ):
                        membersid = message2.content
                    member = client.get_user(int(membersid))
                    if member == None:
                        await message.channel.send(
                            "ERROR1: Cannot find member to message. Please contact an administrator"
                        )
                    await bot.process_commands(message)
                    embed = discord.Embed(
                        title=f"{message.author.name} replied to your message!",
                        description=message.content,
                        color=0xFAB6EE,
                    )
                    async with member.typing():
                        await member.send(embed=embed)
                    await message.add_reaction(emoji="\u2705")
                    await bot.process_commands(message)
            else:
                return
    await bot.process_commands(message)


@bot.command(aliases=["solve"])
async def close(ctx):
    if ctx.channel.name.startswith("report"):
        channel = ctx.channel
        opendate = f"{ctx.channel.created_at.month}-{ctx.channel.created_at.day}-{ctx.channel.created_at.year}"
        async for message2 in ctx.message.channel.history(oldest_first=True, limit=1):
            membersid = message2.content
        member = ctx.message.guild.get_member(int(membersid))
        embed = discord.Embed(
            title=f"**{ctx.author.name} has closed your report**",
            description=f"Hello {member.mention}, your report is now closed. Thank you for reaching out to our staff team today. \n\n> If you need to open a new report, send another message containing why. Have a nice day.",
            color=0xFAB6EE,
        )
        embed.add_field(name="\n\nTicket Creation Date", value=opendate, inline=False)
        embed.add_field(name="Ticket Close Date", value=datev2, inline=False)
        await member.send(embed=embed)
        channel2 = client.get_channel(int(LOGCHANNELID))
        embed = discord.Embed(
            title=f"Ticket closed by {ctx.author.name}", color=0xFAB6EE
        )
        embed.add_field(name="\n\nTicket Open Date", value=opendate, inline=False)
        embed.add_field(name="Ticket Close Date", value=datev2, inline=True)
        embed.add_field(name="Ticket Creator", value=member.name)

        messages = await channel.history(limit=None, oldest_first=True).flatten()
        ticketContent = " ".join(
            [
                f"{message.author.display_name} | {message.author.id} | {message.created_at} | {message.content}\n"
                for message in messages
            ]
        )
        with open(f"data/reports/{member.id}.txt", "w", encoding="utf8") as f:
            f.write(
                f"Here is the message log for modmail report ID {member.id}\n----------\n\n"
            )
            f.write(ticketContent)

        await ctx.channel.delete(reason=None)
        await channel2.send(embed=embed)
        await channel2.send(file=discord.File(f"data/reports/{member.id}.txt"))
    else:
        await ctx.send(
            f"{ctx.author.mention} this can only be used in ticket channels!"
        )


@bot.command()
async def createhelpchannel(ctx):
    channel = client.get_channel(int(HELPCHANNELID))
    embed = discord.Embed(title=":ticket:Modmail Help")
    embed.add_field(name="", value="Close Ticket: `.close/solve`", inline=False)
    embed.add_field(
        name="How to open a report:",
        value="When a user DMs the bot it will create a ticket",
        inline=False,
    )
    await channel.send(embed=embed)


# Embed to liven up the server


@bot.event
async def on_message(message):
    embed = discord.Embed(title="Test", description="test", color=0xFAB6EE)
    test_embed = discord.Embed(
        title="Test", description=message.content, color=0xFAB6EE
    )
    if message.guild is None:
        if message.content.startswith("-apply"):
            await message.author.send(embed=embed)
            await bot.process_commands(message)
        else:
            if message.content.startswith("-answer"):
                msg = await message.channel.history().find(lambda m: bot.user.id)
                await msg.edit(embed=test_embed)
                await bot.process_commands(message)


@bot.command()
async def mutedembed(ctx):
    embed = discord.Embed(
        title="𝕐𝕠𝕦 𝕙𝕒𝕧𝕖 𝕓𝕖𝕖𝕟 𝕞𝕦𝕥𝕖𝕕",
        description="Welcome to the muted waiting room. You are here because you were involved in a situation and a moderator needs to speak with you about it. This is a place for the moderator to get your side of the story and work out the problem.\n\n> Once they are available, the moderator that muted you will pull you into a private channel to discuss what happened. Please be patient as they may need to speak to other people involved. When in the channel they will ask you your side of the story and discuss what actions are necessary for the situation. Please be respectful, the moderators are trained to be unbiased and do what is best for the overall server.",
        color=0xFAB6EE,
    )
    embed.set_footer(text="The Butterfly Project Team")
    await ctx.send(embed=embed)


@bot.command()
async def verifyembed(ctx):
    embed = discord.Embed(
        title="𝕎𝕖𝕝𝕔𝕠𝕞𝕖 𝕥𝕠 𝕋𝕙𝕖 𝔹𝕦𝕥𝕖𝕣𝕗𝕝𝕪 ℙ𝕣𝕠𝕛𝕖𝕔𝕥",
        description="The Butterfly Project is a mental health server aimed at providing community while helping those around us to battle their illnesses and learn how to lead happier and fuller lives together!\n\n𝙷𝚎𝚛𝚎 𝚊𝚝 𝚃𝚑𝚎 𝙱𝚞𝚝𝚝𝚎𝚛𝚏𝚕𝚢 𝙿𝚛𝚘𝚓𝚎𝚌𝚝, 𝚘𝚞𝚛 𝚖𝚒𝚜𝚜𝚒𝚘𝚗 𝚒𝚜...\n\n> To teach our members about coping ahead so they can be better prepared to face real life's hardships and triggers\n\n> To provide a safe and comforting environment so people feel safe with making mistakes and being able to grow from them\n\n> To bring together members and lift each other up through friendship and spirit\n\n> To create a safe space for everyone during their healing processes through a strong moderation team and effective rules and regulations\n\n> To provide above excellent one on one peer support for our members with trained supporters who were hand picked for their skills and their compassion\n\nWe are honored to welcome you to a new home and community. To proceed into the server, please head over to <#753440763366604860> and read through our rules and regulations to find how to gain access to the rest of the server.\n\n```ATTENTION! Due to the nature of the services we provide, you must be at least 18 years old or older to participate. If you are under that age, please do not proceed. If we suspect any minors of joining the server, they will be subjected to an age verification process through the server admins. Thank you for respecting this rule.```",
        color=0xFAB6EE,
    )
    embed.set_image(url="https://i.imgur.com/BHvbDUl.png")
    embed.set_footer(text="The Butterfly Project Team")

    await ctx.send(embed=embed)


@bot.command()
async def faqembed(ctx):
    embed = discord.Embed(
        title="𝔽𝕣𝕖𝕢𝕦𝕖𝕟𝕥𝕝𝕪 𝔸𝕤𝕜𝕖𝕕 ℚ𝕦𝕖𝕤𝕥𝕚𝕠𝕟𝕤",
        description="\n\n\n𝚆𝚑𝚊𝚝 𝚒𝚜 𝚝𝚛𝚒𝚐𝚐𝚎𝚛 𝚠𝚊𝚛𝚗𝚒𝚗𝚐?\n\n> Trigger warning is a term used to inform members that potentially triggering topics are going to be around. Channels marked NSFW are trigger warning channels and should only be entered if you can cope.\n\n𝚆𝚑𝚎𝚛𝚎 𝚌𝚊𝚗 𝙸 𝚏𝚒𝚗𝚍 𝚒𝚗𝚏𝚘𝚛𝚖𝚊𝚝𝚒𝚘𝚗 𝚘𝚗 𝚍𝚒𝚜𝚘𝚛𝚍𝚎𝚛𝚜?\n\n> There are many different disorders this server includes and represents, so to help people understand each disorder better we will add basic information on each disorder. To find this information, go to <#753442529256538113>\n\n𝙷𝚘𝚠 𝚍𝚘 𝙸 𝚐𝚎𝚝 𝚜𝚞𝚙𝚙𝚘𝚛𝚝?\n\n> Here in the server we offer a hand built support system. To find more detailed information on how to speak with a volunteer, please go to <#755320868137205761>\n\n𝚆𝚑𝚊𝚝 𝚊𝚛𝚎 𝚝𝚑𝚎 𝚜𝚝𝚊𝚏𝚏 𝚛𝚘𝚕𝚎𝚜?\n\n> There are several staff roles in the server so we can keep everything running smoothly. We have: Head Administrator, Administrator, Head Moderator, Moderator, Trial Moderator, Welcomer, Head Supporter, Supporter, and  Supporter in training. All staff roles are filled by hard working volunteers who are trained and go through a trial period.\n\n𝙷𝚘𝚠 𝚍𝚘 𝙸 𝚟𝚘𝚕𝚞𝚗𝚝𝚎𝚎𝚛 for 𝚝𝚑𝚎 𝚜𝚎𝚛𝚟𝚎𝚛?\n\n> To find all information on volunteering opportunities, please go to <#764090420777975808>. Any new positions that open will be posted in <#756032536161026078>\n\n𝙷𝚘𝚠 𝚍𝚘 𝙸 𝚌𝚑𝚊𝚗𝚐𝚎 𝚖𝚢 𝚗𝚒𝚌𝚔𝚗𝚊𝚖𝚎?\n\n> In order to avoid any unnecessary rule breaking or triggering content, we do not allow members to change their own nicknames. If you want a name change, please ping Welcomers in <#753442529256538113>\n\n𝙷𝚘𝚠 𝚍𝚘 𝙸 𝚐𝚎𝚝 𝚛𝚘𝚕𝚎𝚜?\n\n> We have many different roles to let other members know about you and your preferences. To get roles, check out <#753444645081710592>\n\n𝙷𝚘𝚠 𝚍𝚘 𝙸 𝚖𝚊𝚔𝚎 𝚜𝚞𝚐𝚐𝚎𝚜𝚝𝚒𝚘𝚗𝚜 𝚘𝚛 𝚊𝚜𝚔 𝚚𝚞𝚎𝚜𝚝𝚒𝚘𝚗𝚜?\n\n> To ask any questions or submit a suggestion, use the <#753442529256538113> channel.\n\n\n𝙸𝚏 𝚢𝚘𝚞 𝚑𝚊𝚟𝚎 𝚊𝚗𝚢 𝚏𝚞𝚛𝚝𝚑𝚎𝚛 𝚚𝚞𝚎𝚜𝚝𝚒𝚘𝚗𝚜, 𝚙𝚒𝚗𝚐 𝚊 𝚠𝚎𝚕𝚌𝚘𝚖𝚎𝚛 𝚊𝚗𝚍 𝚝𝚑𝚎𝚢 𝚠𝚒𝚕𝚕 𝚐𝚞𝚒𝚍𝚎 𝚢𝚘𝚞! 𝚃𝚑𝚊𝚗𝚔 𝚢𝚘𝚞 𝚊𝚗𝚍 𝚎𝚗𝚓𝚘𝚢 𝚝𝚑𝚎 𝚜𝚎𝚛𝚟𝚎𝚛!",
        color=0xFAB6EE,
    )
    embed.set_image(url="https://i.imgur.com/opmuQqs.png")
    embed.set_footer(text="The Butterfly Project Team")

    await ctx.send(embed=embed)


@bot.command()
async def reactembed(ctx):
    embed = discord.Embed(
        title="ℝ𝕖𝕒𝕔𝕥𝕚𝕠𝕟 ℝ𝕠𝕝𝕖𝕤 𝕃𝕚𝕤𝕥",
        description="**Use reactions to get roles!** \n\n> In this channel you will find a list of all reation roles you can have. These roles are used by other members to learn about you and your preferences.\n\n> We have included roles to specify if you have open or closed DMs, what you want to get pinged for, age, gender, and an ever growing list of disorders.\n\n> These roles are also used by staff and peer supports to identify the best way to interact with and help you, so please choose only roles that are accurate to you.\n\n> If you have any roles you want added to the reaction role list, use <#753442529256538113> to suggest the role you want.",
        color=0xFAB6EE,
    )
    embed.set_image(url="https://i.imgur.com/bhbuE7m.png")
    embed.set_footer(text="The Butterfly Project Team")

    await ctx.send(embed=embed)


@bot.command()
async def ruleembed(ctx):
    embed = discord.Embed(
        title="ℝ𝕦𝕝𝕖𝕤 𝕒𝕟𝕕 ℝ𝕖𝕘𝕦𝕝𝕒𝕥𝕚𝕠𝕟𝕤",
        description="Please read the provided guidelines before proceeding to the main server",
        color=0xFAB6EE,
    )
    embed.add_field(
        name="**1. Age Requirement**",
        value="You must be at least 18 years of age to join this server. Anyone suspected of breaking this rule will be investigated by our admins. If you are found to be lying about your age, you will be banned immediately and reported to Discord.",
    )
    embed.add_field(
        name="**2. No NSFW**",
        value="There is no gore, NSFW, self harm or suicide imagery allowed. Any NSFW content posted, including messages, will be deleted, reported to Discord, and the member will be banned.",
    )
    embed.add_field(
        name="**3. Dangerous Items**",
        value="Any discussion of substance abuse, self-harming objects, or any other items used to cause you or anyone else harm are only allowed to be discussed in private support rooms with someone trained. In any other channel, you will be muted immediately.",
    )
    embed.add_field(
        name="**4. Banned Topics**",
        value="The following topics are completely banned from the serve, including the support channels, unless you are speaking of a personal experience you lived through: Abuse, pedophilia, sexual assault, homicide, hate speech, shooting, or encouraging self harming or dangerous behaviors. If you are speaking of something you have experienced, the topic must stay in the proper trigger warning channels and words must be censored.",
    )
    embed.add_field(
        name="**5. Intimidating Behavior**",
        value="Intimidating behaviors, such as threatening or guilt tripping (even unintentionally), will be taken extremely seriously. If you are found to be committing these behaviors, immediate actions will be taken, such as a kick or a ban.",
    )
    embed.add_field(
        name="**6. Triggering Topics**",
        value="Be mindful of triggers. We know many different people have many different triggers, so if you find yourself getting triggered, please move away from the chat or gently let Security know if it is obviously inappropriate. The staff at The Butterfly Project want to encourage everyone to learn healthy coping skills, so if you do get overwhelmed, you can always ping for Support.",
    )
    embed.add_field(
        name="**7. Moving Channels**",
        value="If a moderator decides a conversation isn't quite channel appropriate, they will ask you to move to a better channel. Do not argue with them or you may receive a written warning or be muted.",
    )
    embed.add_field(
        name="**8. Outside Drama**",
        value="Do not bring your outside drama into the server This is a lot of people's safe space, and bringing in drama will not benefit anyone. If you have a problem with someone who is in the server, please use our mod mail system to speak with a staff member and make a report.",
    )
    embed.add_field(
        name="**9. DM Support**",
        value="No staff member at any time will communicate with you for dm support. If you are in need of support, please come make a request in server as it is for your safety and ours. If you are reported trying to reach out to staff or any other member of the server for inappropriate help, they will be told to block you and you may be banned.",
    )
    embed.add_field(
        name="**10. Inner Server Conflict**",
        value="If you or anyone else has an in server conflict with another member, please ping Security immediately. Do not try to engage or take care of it yourself. Ping for the staff and step away to avoid further escalation such as dog piling or more serious behaviors. In other words, don't mini mod.",
    )
    embed.add_field(
        name="**11. Moderation Actions**",
        value="If a moderator steps into a situation, they will take actions to keep the server safe. The steps they may take are as follows:\n\n> First offense, they will give a verbal warning to the member\n\n> Second offense, they will give out a written warning. When you receive a total of three written warnings, the moderation team will discuss banning or kicking you.\n\n> The third offense, or for more intense situations, the moderator will mute the person instigating the situation. When you are muted, you will be taken to a seperate room to speak with them alone about the situation and try to come to a peaceful resolution.\n\n> The fourth offense will be consideration or kicking or banning. The staff team may decide on other ways to go about resolving the situation, but if the member refuses to work with the staff, they will most likely be banned.\n\nThe moderation team may skip any of these steps or do them out of order at their own digression. This is merely for your reference on our moderation system.",
    )
    embed.add_field(
        name="**12. Pluralkit**",
        value="Many people do not know what Pluralkit is, and it can lead to a lot of conflict within the server. If you do not know what the bot is or what its for, you may check out the Pluralkit and alters section of <#753442449975804025> for further information. The main thing is, its real people just speaking through a bot, so please respect them as such.",
    )
    embed.add_field(
        name="**13. Littles and Age Regressors**",
        value="One of our biggest goals is to make all of our members feel safe and comfortable, so Littles an age regressors are not restricted to <#753443539530285077> only. However, it is up to whatever adults are around, or the other alters in the system to draw boundaries with their Littles as to where they are allowed and where they are not. If one little can handle the trigger warning room, then they are allowed as long as an adult approved it.",
    )
    embed.add_field(
        name="**14. Fake Claiming**",
        value="Faking an illness is no joke, and we take it very seriously here. However, there is absolutely no fake claiming, or saying someone is faking, out in the server or to members that share the server with you. If you are reported to be fake claiming, you will be immediately reported to Discord and banned from the server. If you have legitimate concerns someone may be faking an illness, you are allowed to use the modmail system to make a report to an admin.",
    )
    embed.add_field(
        name="**15. Support Information**",
        value="Further rules for our peer support program will be available in <#755320868137205761>. If you have any questions about the support system, please open a modmail ticket and speak with the staff to protect any sensitive information.\n\n```These rules are subject to change at any time without advanced warning```\n\n***You must be 18 years or older to join this server. If you agree to these rules and the punishments that come with breaking them, please go back to verify and do the command ?agree to gain access to the rest of the server.***",
    )
    embed.set_image(url="https://i.imgur.com/aXvKW1X.png")
    await ctx.send(embed=embed)
    


bot.run("NzUyMTgzNzYxNzkzMTg3OTUy.X1T7tw.6VocrMsw_KFSrWB3VRQh74kgajQ")


