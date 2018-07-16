import discord
from discord.ext import commands
from bs4 import BeautifulSoup
from time import ctime
import logging
import traceback
import asyncio
import aiohttp
from configparser import ConfigParser

token = 'tokenhere'

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

config = ConfigParser()
config.read('data.ini')

class linkThing:
    url = ""
    title = ""
    body = ""


def get_prefix(bot, message):
    server = message.server
    if config.has_section(server.id) == True:
        get_prefix = config.get(server.id, 'botprefix')
        prefixes = [get_prefix]
        return commands.when_mentioned_or(*prefixes)(bot, message)
    else:
        prefixes = ['~']
        return commands.when_mentioned_or(*prefixes)(bot, message)

bot = commands.Bot(command_prefix=get_prefix)

@bot.event
async def on_ready():
    print('Logged in as: '+bot.user.name)
    print('Bot ID: '+bot.user.id)
    print('Invite Link Below')
    print('------')
    print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8'.format(bot.user.id))
    print('------')
    for server in bot.servers:
        print("Connected to server: {} with id: {}".format(server, server.id))
    print('------')


async def connect():
    print('Logging in...')
    while not bot.is_closed:
        try:
            await bot.start(token)
        except:
            await asyncio.sleep(5)


@bot.command(pass_context=True)
async def setprefix(ctx, message):
    """<prefix><setprefix><args> default is ~setprefix <chars> (up to 2)"""
    server = ctx.message.server
    author = ctx.message.author
    if config.has_section(server.id) == True:
        if author.id == config.get(server.id, 'ownerid'):
            if len(message) > 2:
                await bot.say('prefix commands can only be up to two chars long')
            else:
                with open('data.ini', 'w+', encoding="utf-8") as configfile:
                    config.set(str(server.id), 'botprefix', message)
                    config.write(configfile)
                await bot.say('prefix updated to {!r}'.format(message))

    if config.has_section(server.id) == False:
        await bot.say('I dont have a config for this channel')

    if ctx.message.author.id != config.get(server.id, 'ownerid'):
        owner = config.get(server.id, 'ownerid')
        await bot.say('{} you are not authorized to use this command, please contact'
                      ' <@'.format(author.mention) + owner + '>')


@bot.command(pass_context=True)
async def addchannel(ctx):
    """<prefix><addchannel> use only in the channel you want to add it to, no arguments to give"""
    server = ctx.message.server
    if config.has_section(server.id) != True:
        server = ctx.message.server
        channel = ctx.message.channel
        author = ctx.message.author
        await bot.say('couldnt find your config, creating one now.')
        with open('data.ini', 'w+', encoding="utf-8") as configfile:
            config.add_section(str(server.id))
            config.set(str(server.id), 'servername', str(server))
            config.set(str(server.id), 'channelname', str(channel))
            config.set(str(server.id), 'channelID', str(channel.id))
            config.set(str(server.id), 'owner', str(author))
            config.set(str(server.id), 'ownerid', str(author.id))
            config.set(str(server.id), 'botprefix', '~')
            config.write(configfile)
    else:
        channelname = config.get(server.id, 'channelname')
        servername = config.get(server.id, 'servername')
        owner = config.get(server.id, 'ownerid')
        await bot.say('the bot has already been set up for channel {!r} on server {!r} '
                      'to change this please talk to <@'.format(channelname, servername) + owner + '>')


@bot.command(pass_context=True)
async def news():
    """Fetches news, no args."""
    await bot.say("fetching now..")
    async with aiohttp.ClientSession() as client:
        listOfLinks = await fetch(client)
        try:
            for x in listOfLinks:
                embed = discord.Embed(colour=discord.Colour(0x608f30),
                                      description="```" + x.body[2:] + '...'"```" + "Read more [here](" + x.url + ")", )
                embed.set_footer(text=ctime())
                await bot.say(
                    content="**" + x.title + "**",
                    embed=embed)
        except:
            logging.warning(traceback.format_exc())  # logs the error
            await bot.say('there was a problem fetching the news...')
            with open('traceback.log', 'a+') as log:
                log.write('\n' + ctime() + '\n')
                log.write(traceback.format_exc())



async def fetch(client):
    """fetches the information"""
    async with client.get('https://www.pcgamer.com/news/') as resp:
        assert resp.status == 200
        response = await resp.text()
    try:
        soup = BeautifulSoup(response, 'html.parser')
        href_list = []
        title_list = []

        for href in soup.find_all("div", {"class": "feature-block-item-wrapper"}):
            url = href.find('a', href=True)
            url = url['href']
            href_list.append(url)

        for title in soup.find_all('figure', attrs={'class': 'feature-block-item'}):
            title = title.find('span', {'article-name'})
            title = title.text
            title_list.append(title)

        body_list_string = []
        for url in href_list:
            body_list = []
            async with client.get(url) as resp:
                assert resp.status == 200
                response = await resp.text()
            soup = BeautifulSoup(response, 'html.parser')
            results = soup.find_all("p", {"class": None})
            for body in results:
                body = body.text
                body_list.append(body)

            body_list = body_list[:3]
            body_list_string.append(str(body_list).replace("\\", "")[:200])

        listOfLinks = list()

        for x, yz in enumerate(href_list):
            newLinkItem = linkThing()
            newLinkItem.url = href_list[x]
            newLinkItem.title = title_list[x]
            newLinkItem.body = body_list_string[x]
            listOfLinks.append(newLinkItem)

        return listOfLinks

    except:
        logging.warning(traceback.format_exc())  # logs the error
        with open('traceback.log', 'a+') as log:
            log.write('\n' + ctime() + '\n')
            log.write(traceback.format_exc())


bot.loop.run_until_complete(connect())
