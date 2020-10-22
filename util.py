import discord
from discord.ext import commands

from utils.jsonLoader import read_json, write_json


def GetTicketCount():
    data = read_json("config")
    return data["ticketCount"]


def IncrementTicketCount():
    data = read_json("config")
    data["ticketCount"] += 1
    write_json(data, "config")


def GetTicketSetupMessageId():
    data = read_json("config")
    return data["ticketSetupMessageId"]


def LogNewTicketChannel(channelId, ticketId):
    data = read_json("config")
    data[str(channelId)] = {}
    data[str(channelId)]["id"] = ticketId
    data[str(channelId)]["reactionMsgId"] = None
    write_json(data, "config")


def IsATicket(channelId):
    data = read_json("config")
    return str(channelId) in data


def GetTicketId(channelId):
    data = read_json("config")
    return data[str(channelId)]["id"]


def RemoveTicket(channelId):
    data = read_json("config")
    data.pop(str(channelId))
    write_json(data, "config")


async def NewTicketSubjectSender(author, channel, subject):
    if subject == "No subject specified.":
        return
    embed = discord.Embed(
        title="Provided subject for ticket:", description=subject, color=0xfab6ee,
    )
    embed.set_author(name=author.name, icon_url=author.avatar_url)
    await channel.send(embed=embed)


async def NewTicketEmbedSender(bot, author, channel):
    
    embed = discord.Embed(
    title="**Welcome to peer to peer support {}!**".format(author.display_name),
    description="**Thank you for contacting support**\n\n> While you wait for a supporter, please briefly describe why you need support and identify any triggering topics that may come up.\n\n> If you need immediate help, please do the command ``.crisis`` to alert higher ups.\n\n> If you need any additional help, we have resources with the bot listed in <#755320868137205761>",
    color=0xfab6ee)
    embed.set_thumbnail(url="https://i.imgur.com/mxLRE31.png")
    embed.set_footer(text="The Butterfly Project Team")
    
    
    m = await channel.send(f"{author.mention} | <@&{bot.supp_role_id}> | <@&{bot.tsupp_role_id}>", embed=embed)
    await m.add_reaction("🔒")

    data = read_json("config")
    data[str(channel.id)]["reactionMsgId"] = m.id
    write_json(data, "config")


async def ReactionCreateNewTicket(bot, payload):
    guild = bot.get_guild(751990570989387796)
    author = guild.get_member(payload.user_id)

    await CreateNewTicket(bot, guild, author)


async def CreateNewTicket(bot, guild, author, *, subject=None, message=None):
    subject = subject or "No subject specified."
    ticketId = GetTicketCount() + 1
    modRole = guild.get_role(bot.mod_role_id)
    suppRole = guild.get_role(bot.supp_role_id)
    tsuppRole = guild.get_role(bot.tsupp_role_id)
    logChannel = bot.get_channel(bot.log_channel_id)
    category_id = int(759955006123540530)
    category = guild.get_channel(category_id)

    

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
        modRole: discord.PermissionOverwrite(read_messages=True),
        suppRole: discord.PermissionOverwrite(read_messages=True),
        tsuppRole: discord.PermissionOverwrite(read_messages=True),
        author: discord.PermissionOverwrite(read_messages=True)}

    channel = await guild.create_text_channel(
        name=f"Support Ticket #{ticketId}",
        overwrites=overwrites,
        category=category)
    
    
    LogNewTicketChannel(channel.id, ticketId)
    await SendLog(
        bot,
        author,
        logChannel,
        f"Created ticket with ID {ticketId}",
        f"Ticket Creator: {author.mention}(`{author.id}`)\nChannel: {channel.mention}({channel.name})\nSubject: {subject}",
        0xfab6ee,
    )

    await NewTicketEmbedSender(bot, author, channel)
    await NewTicketSubjectSender(author, channel, subject)
    IncrementTicketCount()

    if message:
        await message.delete()


async def CloseTicket(bot, channel, author, reason=None):
    if not IsATicket(channel.id):
        await channel.send("I cannot close this as it is not a ticket.")
        return

    reason = reason or "No closing reason specified."
    ticketId = GetTicketId(channel.id)
    messages = await channel.history(limit=None, oldest_first=True).flatten()
    ticketContent = " ".join(
        [f"{message.content} | {message.author.name}\n" for message in messages]
    )
    with open(f"data/tickets/{ticketId}.txt", "w", encoding="utf8") as f:
        f.write(f"Here is the message log for ticket ID {ticketId}\n----------\n\n")
        f.write(ticketContent)

    fileObject = discord.File(f"data/tickets/{ticketId}.txt")
    logChannel = bot.get_channel(bot.log_channel_id)
    await SendLog(
        bot,
        author,
        logChannel,
        f"Closed Ticked: Id {ticketId}",
        f"Close Reason: {reason}",
        0xfab6ee,
        file=fileObject,
    )
    await channel.delete()


async def SendLog(
    bot: commands.Bot,
    author,
    channel,
    contentOne: str = "Default Message",
    contentTwo: str = "\uFEFF",
    color=0xfab6ee,
    timestamp=None,
    file: discord.File = None,
):
    embed = discord.Embed(title=contentOne, description=contentTwo, color=color)

    if timestamp:
        embed.timestamp = timestamp

    embed.set_author(name=author.name, icon_url=author.avatar_url)
    await channel.send(embed=embed)

    if file:
        await channel.send(file=file)


def CheckIfValidReactionMessage(msgId):
    data = read_json("config")

    if data["ticketSetupMessageId"] == msgId:
        return True

    data.pop("ticketSetupMessageId")
    data.pop("ticketCount")
    for value in data.values():
        if value["reactionMsgId"] == msgId:
            return True

    return False


async def SetupNewTicketMessage(bot):
    data = read_json("config")
    channel = bot.get_channel(bot.new_ticket_channel_id)
    
    embed = discord.Embed(
        title="𝕋𝕙𝕖 𝔹𝕦𝕥𝕥𝕖𝕣𝕗𝕝𝕪 ℙ𝕣𝕠𝕛𝕖𝕔𝕥 ℙ𝕖𝕖𝕣 𝕊𝕦𝕡𝕡𝕠𝕣𝕥 𝕊𝕪𝕤𝕥𝕖𝕞",
        description="Welcome to The Butterfly Project's Peer Support!\n\nThis is a safe space for those who are going through recovery or want to recover with their mental illness. On top of our already loving community, we are proud to offer you:\n\n> Private one on one peer support with our trained volunteers\n\n> A team of moderators and supporters that truly care about your safety\n\n> A completely private and safe enviornment for you to talk to your volunteer\n\n> And custom commands to help you in a pinch\n\nWe are so happy to be a part of your recovery journey! Our volunteers aren't just people on the other side of a screen, they are your friends that you get to know personally in server. Below are the basic rules of our peer to peer support. Once you have read them and understand them, click the check mark below to get started.",
        color=0xfab6ee,
    )
    embed.add_field(
   	name="ℙ𝕖𝕖𝕣 𝕊𝕦𝕡𝕡𝕠𝕣𝕥 𝔾𝕦𝕚𝕕𝕖𝕝𝕚𝕟𝕖𝕤",
   	value="Please read the following rules before asking for support.") 
    embed.add_field(
   	name="**1. Be mindful of triggering topics**",
   	value="*When you open a ticket we ask that you describe your situation and identify any triggers that may come up. This is for the safety of our volunteers so they can be aware if they need to cope ahead.*")
    embed.add_field(
   	name="**2. Respect the Supporters**",
   	value="*Our peer supports are all here on a volunteer basis. They are doing a hard job for free to help you, so pleade do not disrespect the volunteers.If you have an issue with a volunteer, please report them through the modmail system in the server.*")
    embed.add_field(
   	name="**3. Do not abuse the system**",
   	value="*This support system is here for you to use when other methods of coping fail. Before coming to our peer supports, please try and use the rest of the server and resources provided to you. You may come directly to the supporters when you are in a crisis (suicidal, homicidal, having strong self harm urges, so on) or when you feel you don't have any good coping skills.*")
    embed.add_field(
   	name="***Crisis situation***",
   	value="*Due to the nature of the job, we may not always have enough volunteers to keep up with the volume of support requests. This can lead to wait times for those seeking support.If you are in a crisis, please alert higher ups once in a chat with the command ``.crisis``. We will prioritize your ticket and make sure you get the help you need. We can also give you your local suicide hotline number.*")
    embed.set_footer(text="The Butterfly Project Team")
    embed.set_image(url="https://i.imgur.com/dQk2HRM.png")
    m = await channel.send(embed=embed)
    await m.add_reaction("✅")
    data["ticketSetupMessageId"] = m.id

    write_json(data, "config")
