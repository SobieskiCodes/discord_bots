import discord
from discord.ext import commands
import asyncio
from configparser import ConfigParser
import random
from imgurpython import ImgurClient
from datetime import datetime


'''--------------------------------
-----------Variables---------------
---------------------------------'''

version = '0.9.3'
config = ConfigParser()
config.read('datapicture.ini')
discordToken = config.get('config', 'token')
clientID = config.get('config', 'imgurClientID')
secretID = config.get('config', 'imgurClienetSecret')
client = ImgurClient(clientID, secretID)
boottime = datetime.now()

'''--------------------------------
------non async functions----------
---------------------------------'''


def get_prefix(bot, message):
    server = message.server
    if config.has_section(server.id):
        getprefix = config.get(server.id, 'prefix')
        prefixes = [getprefix]
        return commands.when_mentioned_or(*prefixes)(bot, message)
    else:
        prefixes = ['.']
        return commands.when_mentioned_or(*prefixes)(bot, message)


bot = commands.Bot(command_prefix=get_prefix)



'''--------------------------------
-----------bot setup---------------
---------------------------------'''


@bot.event
async def on_ready():
    print('Logged in as: ' + bot.user.name)
    print('Bot ID: ' + bot.user.id)
    print('Invite Link Below')
    print('------')
    print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=0'.format(bot.user.id))
    print('------')
    for server in bot.servers:
        print("Connected to server: {} with id: {}".format(server, server.id))
    print('------')


async def connect():
    print('Logging in...')
    while not bot.is_closed:
        try:
            await bot.start(discordToken)
        except:
            await asyncio.sleep(5)


'''--------------------------------
-----------bot events--------------
---------------------------------'''


@bot.event
async def on_server_join(server):
    me = await bot.get_user_info('245276992432373760')
    await bot.send_message(me, "I've joined server: {!r} with ID: {!r}".format(server.name, server.id))


@bot.event
async def on_server_remove(server):
    me = await bot.get_user_info('245276992432373760')
    await bot.send_message(me, "I've left server: {!r} with ID: {!r}".format(server.name, server.id))


@bot.event
async def on_command_error(error, ctx):
    channel = ctx.message.channel
    input = ctx.message.content

    if ctx.message.author.bot:
        return

    if isinstance(error, commands.MissingRequiredArgument):
        await bot.send_message(channel, '{!r} requires an arg** to be used. eg; "{} <arg>"'.format(input, input))


'''--------------------------------
-----------bot commands------------
---------------------------------'''


@bot.command(pass_context=True)
async def setprefix(ctx, message):
    """<setprefix args> default is ~setprefix <chars> (up to 2)."""
    server = ctx.message.server
    author = ctx.message.author

    if ctx.message.author.bot:
        return

    if config.has_section(server.id):
        if author.id == config.get(server.id, 'ownerid'):
            if len(message) > 2:
                await bot.say('Prefix commands can only be up to two chars long.')
            else:
                with open('datapicture.ini', 'w+', encoding="utf-8") as configfile:
                    config.set(str(server.id), 'prefix', message)
                    config.write(configfile)
                await bot.say('Prefix updated to {!r}'.format(message))

    if not config.has_section(server.id):
        await bot.say('I don\'t have a config for this server.')

    if ctx.message.author.id != config.get(server.id, 'ownerid'):
        owner = config.get(server.id, 'ownerid')
        await bot.say('{}, you are not authorized to use this command, please contact'
                      ' <@'.format(author.mention) + owner + '>')


@bot.command(pass_context=True, hidden=True)
async def echo(ctx, message: str = None):
    """is anyone home home home home home?"""
    owner = config.get(ctx.message.server.id, 'ownerid')

    if ctx.message.author.id == owner:
        if message is None:
            await bot.say('echo echo echo echo....')
        else:
            await bot.say('{}'.format(message))
    else:
        return


@bot.command(pass_context=True, hidden=True)
async def vme(ctx):
    """What version am I?"""
    owner = '245276992432373760'

    if ctx.message.author.id != owner:
        return

    else:
        server_count = 0
        member_count = 0
        for server in bot.servers:
            contains = ['264445053596991498', '110373943822540800']
            if server.id not in contains:
                for member in server.members:
                    member_count = member_count + 1
                server_count = server_count + 1
        time = datetime.now() - boottime
        days = time.days
        hours, remainder = divmod(time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        onlinefor = "{}:days {}:hours {}:minutes and {}:seconds!".format(days, hours, minutes, seconds)

        embed = discord.Embed(colour=discord.Colour(0x50bdfe),
                              description="Here is some information about me... "
                                          "                                                                           "
                                          "```Version: {}\n"
                                          "Library: Discord.py\n"
                                          "Uptime: {}\n"
                                          "Server Count: {}\n"
                                          "Member Count: {}```".format(version, onlinefor, server_count, member_count))
        embed.set_footer(text='justin@sobieski.codes')
        await bot.say(embed=embed)


@bot.command(pass_context=True, hidden=True, aliases=['inv'])
async def invite(ctx):
    """You know you want to invite me..."""

    if ctx.message.author.bot:
        return

    base = 'https://discordapp.com/oauth2/authorize?client_id='
    tail = '&scope=bot&permissions=0'
    botid = '415636390815072256'
    embed = discord.Embed(colour=discord.Colour(0x608f30),
                          description="Invite me [here](" + base + botid + tail + ")")
    embed.set_footer(text='')
    await bot.say(embed=embed)


@bot.command(pass_context=True)
async def setup(ctx):
    """Used to set up the bot for your server, no configuration."""
    serverid = ctx.message.server.id
    if ctx.message.author.bot:
        return

    if config.has_section(serverid):
        await bot.say('The bot has already been configured for this server.')
    else:
        with open('datapicture.ini', 'r+', encoding="utf-8") as data:
            config.add_section(serverid)
            config.set(str(serverid), 'ownerid', str(ctx.message.author.id))
            config.set(str(serverid), 'listofids', str(ctx.message.author.id))
            config.set(str(serverid), 'prefix', '.')
            config.write(data)
        get_the_prefix = config.get(serverid, 'prefix')
        await bot.say('Bot has been configured for this server.\n'
                      'You are now the owner, you can add more people with "{}addid <id>".\n'
                      'To add an album just do "{}album <link>"'.format(get_the_prefix, get_the_prefix))


@bot.command(pass_context=True)
async def album(ctx, message):
    """<album link> Allows owners to add an album imgur only."""
    serverid = ctx.message.server.id

    if ctx.message.author.bot:
        return

    if not config.has_section(serverid):
        await bot.say('Server hasnt been configured.')
        return

    ownerid = config.get(serverid, 'ownerid')
    idlist = config.get(serverid, 'listofids').split(', ')

    if ctx.message.author.id in idlist or ctx.message.author.id == str(ownerid):
        contains_a = 'https://imgur.com/a/'
        contains_gallery = 'https://imgur.com/gallery/'
        if contains_a in ctx.message.content or contains_gallery in ctx.message.content:
            try:
                splitmessage = message.split('/')
                client.get_album_images(splitmessage[4])
            except:
                await bot.say('Imgur says that\'s not a valid link.')
                return

            await bot.say('That link is valid, what would you like to name it?')

            albumname = await bot.wait_for_message(timeout=10.0, author=ctx.message.author)
            if albumname is None:
                await bot.say('You took to long to respond, closing this request.')
                return

            else:
                albumname.content = albumname.content.lower()
                if config.has_section(albumname.content):
                    await bot.say('There is already and album named {!r}'.format(albumname.content))
                    return

                if len(albumname.content) <= 10:
                    get_the_prefix = config.get(serverid, 'prefix')
                    await bot.say('Perfect, you can now use "{}pickone {}" to pick an image.'.format(get_the_prefix, albumname.content))
                    with open('datapicture.ini', 'r+', encoding="utf-8") as data:
                        config.set(serverid, str(albumname.content), str(message))
                        config.write(data)
                        return

                if len(albumname.content) >= 10:
                    await bot.say('Please choose a shorter name to link.')
                    return

        else:
            await bot.say('That\'s not a valid link.')
            return
    else:
        await bot.say('{}, you are not authorized for this command.'.format(ctx.message.author))
        return


@bot.command(pass_context=True)
async def delalbum(ctx, message: str):
    """<delalbum name> Deletes an album by name, owners and allowed."""
    serverid = ctx.message.server.id
    message = message.lower()

    if ctx.message.author.bot:
        return

    if not config.has_section(serverid):
        await bot.say('server hasnt been configured.')
        return

    setup = config.get(serverid, 'ownerid')
    idlist = config.get(serverid, 'listofids').split(', ')

    if ctx.message.author.id in idlist or ctx.message.author.id == str(setup):
        if config.has_option(serverid, message):
            with open('datapicture.ini', 'w+', encoding="utf-8") as data:
                config.remove_option(serverid, message)
                config.write(data)
            await bot.say('I have removed the link for {!r}'.format(message))
        else:
            await bot.say('I couldn\'t find an album by the name of {!r}'.format(message))
            return
    else:
        await bot.say('{}, you are not authorized for this command.'.format(ctx.message.author))


@bot.command(pass_context=True, aliases=['p1', 'po'])
async def pickone(ctx, message: str = None):
    """Picks a random image from the album provided."""
    serverid = ctx.message.server.id

    if ctx.message.author.bot:
        return

    if not config.has_section(serverid):
        await bot.say('This server isn\'t configured yet.')
        return

    options = config.options(ctx.message.server.id)
    if len(options) == 3:
        await bot.say('It seems you havn\'t added any links...')
        return

    if len(options) == 4:
        if message is not None:
            await bot.say('It seems you only have one link, please don\'t add parameters.')
            return

        else:
            album = config.get(serverid, options[3])
            albumtail = album.split('/')
            album = client.get_album_images(albumtail[4])
            url_list = []
            for item in album:
                url_list.append(item.link)
            i_chose = random.choice(url_list)
            embed = discord.Embed(title="I Chose..", colour=discord.Colour(0x278d89), )
            embed.set_image(url=i_chose)
            await bot.say(content="You asked me to pick a picture...", embed=embed)
            return

    if len(options) > 4:
        if message is None:
            prefix = config.get(serverid, 'prefix')
            await bot.say('You have multiple albums added but didnt specify which one im looking for. \n'
                          'Try "{} <album name>" or "{}albumlist".'.format(ctx.message.content, prefix))
            return
        else:
            if config.has_option(serverid, message):
                album = config.get(serverid, message)
                albumtail = album.split('/')
                album = client.get_album_images(albumtail[4])
                url_list = []
                for item in album:
                    url_list.append(item.link)
                i_chose = random.choice(url_list)
                embed = discord.Embed(title="I Chose..", colour=discord.Colour(0x278d89), )
                embed.set_image(url=i_chose)
                await bot.say(content="You asked me to pick a picture...", embed=embed)
            else:
                await bot.say('I couldnt find an album by the name of {!r}'.format(message))
            return


@bot.command(pass_context=True)
async def addid(ctx, message: str):
    """<addid id> Owner can add users must be userID."""
    serverid = ctx.message.server.id

    if ctx.message.author.bot:
        return

    if not config.has_section(serverid):
        await bot.say('Server hasnt been configured.')
        return

    owner = config.get(serverid, 'ownerid')
    if ctx.message.author.id == owner:
        try:
            message = int(message)
            if len(str(message)) == 18:
                idlist = config.get(serverid, 'listofids')
                stringidlist = str(idlist)
                addmessage = stringidlist + ', ' + str(message)
                with open('datapicture.ini', 'w+', encoding="utf-8") as data:
                    config.set(serverid, 'listofids', str(addmessage))
                    config.write(data)
                await bot.say('{} has been added to the allow list.'.format(message))
            else:
                await bot.say('That doesnt seem to be a real ID')

        except:
            await bot.say('Thats not an int')
            return

    else:
        await bot.say('{}, You are not authorized to use this command.'.format(ctx.author.mention))
        return


@bot.command(pass_context=True)
async def albumlist(ctx):
    """Lists all albums in storage, no args."""

    if ctx.message.author.bot:
        return

    options = config.options(ctx.message.server.id)
    option_list = []
    for option in options:
        option_list.append(option)

    await bot.say('These are the albums i found: {}'.format(option_list[3:]).replace('[', '').replace(']', '')
                  .replace(',', ''))

    #   hide first section (setup), replace [,] with spaces, and replace , with spaces for clean looking list.
    return


bot.loop.run_until_complete(connect())
