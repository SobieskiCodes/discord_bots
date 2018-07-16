from idlelib import replace

import discord
from discord.ext import commands
import asyncio
import pyson
import re
import random

bot = commands.Bot(command_prefix='.')
config = pyson.Pyson('data.json')
token = config.data.get('config').get('token')
users = config.data.get('users')


@bot.event
async def on_ready():
    print('Logged in as: '+bot.user.name)
    print('Bot ID: '+bot.user.id)
    print('Invite Link Below')
    print('------')
    print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=0'.format(bot.user.id))
    print('------')
    for server in bot.servers:
        print("Connected to server: {} with id: {}".format(server, server.id))
        for member in server.members:
            if not member.bot:
                if member.id not in config.data.get('users'):
                    new_user = {"itemlist": {}, "points": 0}
                    config.data['users'][member.id] = new_user
                    config.save()
                    print('{} has been added'.format(member))

    print('------')


async def connect():
    print('Logging in...')
    while not bot.is_closed:
        try:
            await bot.start(token)
        except:
            await asyncio.sleep(5)


@bot.command(pass_context=True)
async def buy(ctx, message: str = None):
    item_list = ['weak', 'skilled', 'frantic']
    message = message.lower()
    if message is None:
        await bot.say('Categories are weak, skilled, and frantic.')
        return

    items = config.data.get('items')
    weak_items = []
    for item in items:
        cost = config.data.get('items').get(item).get('cost')
        if cost is 5:
            weak_items.append(item)

    weak_recieve = random.choice(weak_items)
    weak_name = config.data.get('items').get(weak_recieve).get('name')

    if message in item_list:
        if message == 'weak':
            player_inventory = config.data.get('users').get(ctx.message.author.id).get('itemlist')
            amount_to_add = []
            for item in player_inventory:
                get_amount = config.data.get('users').get(ctx.message.author.id).get('itemlist').get(item)
                amount_to_add.append(int(get_amount))

            if len(amount_to_add) == 0:
                config.data['users'][ctx.message.author.id]['itemlist'][weak_recieve] = 1
                config.save()
                await bot.say(f'{ctx.message.author.mention} you recieved {weak_name}')
                return

            else:
                total = 0
                for item in amount_to_add:
                    total = int(total) + int(item)
                if total >= 3:
                    await bot.say(f'{ctx.message.author.mention} you have too many items already, please use one first.')
                else:
                    get_player_inventory = config.data.get('users').get(ctx.message.author.id).get('itemlist')
                    if weak_recieve in get_player_inventory:
                        get_current_amount = config.data.get('users').get(ctx.message.author.id).get('itemlist').get(weak_recieve)
                        new_value = get_current_amount + 1
                        config.data['users'][ctx.message.author.id]['itemlist'][weak_recieve] = new_value
                        config.save()

                    else:
                        config.data['users'][ctx.message.author.id]['itemlist'][weak_recieve] = 1
                        config.save()

                    await bot.say(f'{ctx.message.author.mention} you recieved {weak_name}')

        if message == 'skilled':
            await bot.say('skilled items not added yet')

        if message == 'frantic':
            await bot.say('frantic items not added yet.')

    else:
        await bot.say('item categories are weak, skilled and frantic.')
        return


@bot.command(pass_context=True)
async def store(ctx, message: str = None):
    get_items = config.data.get('items')
    embed = discord.Embed(title="Store", description=ctx.message.author.mention,
                          colour=discord.Colour(0x278d89))
    items = ''
    descriptions = ''
    for item in get_items:
        description = config.data.get('items').get(item).get('description')
        price = config.data.get('items').get(item).get('cost')
        name = config.data.get('items').get(item).get('name')
        items += f'{name} ({price})\n'
        descriptions += f'{description}\n'

    embed.add_field(name='Item & Price', value=items)
    embed.add_field(name='Description', value=descriptions)
    await bot.say(embed=embed)



@bot.command(pass_context=True)
async def pos(ctx, message: str = None):
    if message is None:
        author = ctx.message.author
        leaderboard = sorted(users, key=lambda x: users[x]['points'], reverse=True)
        position = leaderboard.index(author.id)
        await bot.say('You are in position: {}'.format(position + 1))
        return
    else:
        mention_list = []
        for mention in ctx.message.mentions:
            mention_list.append(mention.id)
        user = str(mention_list).replace('[', '').replace(']', '').replace('\'', '')

        if len(mention_list) >= 2:
            await bot.say('It seems you are trying to get the position of multiple people, I can\'t do that.')
            return

        if not message.startswith('<@'):
            await bot.say('Message must start with a mention.')
            return

        if len(mention_list) == 1:
            if message.startswith('<@'):
                value = str(ctx.message.content).split('> ')
                if len(value) >= 2:
                    await bot.say('Please just use a mention.')
                    return
                else:
                    user = str(mention_list).replace('[', '').replace(']', '').replace('\'', '')
                    leaderboard = sorted(users, key=lambda x: users[x]['points'], reverse=True)
                    position = leaderboard.index(user)
                    await bot.say('<@{}> is in position {}.'.format(user, position))
'''
        if position == 0:
            print('first place true')
        if position+1 == len(users):
            print('last place true')
        else:
            print('before: {},after: {}'.format(leaderboard[position-1], leaderboard[position+1]))
'''

@bot.command(pass_context=True)
async def points(ctx, message: str = None):
    author = ctx.message.author.id

    if message is None:
        get_points = config.data.get('users').get(author).get('points')
        await bot.say('{} you have {} points.'.format(ctx.message.author.mention, get_points))
        return

    else:
        mention_list = []
        for mention in ctx.message.mentions:
            mention_list.append(mention.id)

        user = str(mention_list).replace('[', '').replace(']', '').replace('\'', '')
        if len(mention_list) >= 2:
            await bot.say('It seems you are trying to get the points of multiple people, I can\'t do that.')
            return
        if len(mention_list) == 1:
            if message.startswith('<@'):
                if len(message) > len(user) + 3:
                    await bot.say('Please don\'t add context to your message, just mention the user.')
                    return
                else:
                    get_points = config.data.get('users').get(user).get('points')
                    await bot.say('<@{}> has {} points.'.format(user, get_points))
                    return
            else:
                await bot.say('The message needs to contain nothing but a user mention.')
                return


@bot.command(pass_context=True)
async def inventory(ctx, message: str = None):

    if message is None:
        try:
            get_inventory = config.data.get('users').get(ctx.message.author.id).get('itemlist')
            embed = discord.Embed(title="Inventory", description=ctx.message.author.mention,
                                  colour=discord.Colour(0x278d89))
            descriptions = ''
            items = ''
            for item in get_inventory:
                name = config.data.get('items').get(item).get('name')
                description = config.data.get('items').get(item).get('description')
                itemamount = config.data.get('users').get(ctx.message.author.id).get('itemlist').get(item)
                descriptions += f'{description}\n'
                items += f'{name} x({itemamount})\n'

            embed.add_field(name='Item & Amount', value=items)
            embed.add_field(name='Description', value=descriptions)
            await bot.say(embed=embed)
        except:
            embed = discord.Embed(title="Inventory", description=ctx.message.author.mention,
                                  colour=discord.Colour(0x278d89))
            embed.add_field(name='Item & Amount', value="None")
            embed.add_field(name='Description', value='None')
            await bot.say(embed=embed)

    else:
        mention_list = []
        for mention in ctx.message.mentions:
            mention_list.append(mention.id)
        user = str(mention_list).replace('[', '').replace(']', '').replace('\'', '')

        if message is None:
            await bot.say('You need to include a user.')
            return

        if len(mention_list) >= 2:
            await bot.say('It seems you are trying to get the inventory of multiple people, I can\'t do that.')
            return

        if not message.startswith('<@'):
            await bot.say('Message must start with a mention.')
            return

        value = str(ctx.message.content).split('> ')
        if len(mention_list) == 1:
            if message.startswith('<@'):
                if len(value) >= 2:
                    await bot.say('can you not include anything other then a mention?')
                    return
                else:
                    stripmessage = message.replace('<', '').replace('>', '').replace('@', '')
                    if stripmessage == ctx.message.author.id:
                        await bot.say('can you not mention yourself?')
                        return

                    if stripmessage == bot.user.id:
                        await bot.say('{} thats a bot....'.format(ctx.message.author.mention))
                        return

                    try:
                        get_inventory = config.data.get('users').get(stripmessage).get('itemlist')
                        embed = discord.Embed(title="Inventory", description='<@{}>'.format(stripmessage),
                                              colour=discord.Colour(0x278d89))
                        descriptions = ''
                        items = ''
                        for item in get_inventory:
                            name = config.data.get('items').get(item).get('name')
                            description = config.data.get('items').get(item).get('description')
                            itemamount = config.data.get('users').get(stripmessage).get('itemlist').get(item)
                            descriptions += f'{description}\n'
                            items += f'{name} x({itemamount})\n'

                        embed.add_field(name='Item & Amount', value=items)
                        embed.add_field(name='Description', value=descriptions)
                        await bot.say(embed=embed)
                    except:
                        embed = discord.Embed(title="Inventory", description='<@{}>'.format(stripmessage),
                                              colour=discord.Colour(0x278d89))
                        embed.add_field(name='Item & Amount', value="None")
                        embed.add_field(name='Description', value='None')
                        await bot.say(embed=embed)

            else:
                await bot.say('The message needs to start with a mention.')
                return


@bot.command(pass_context=True)
async def top10(ctx):
    #server=ctx.message.server
    leaderboard = sorted(users, key=lambda x: users[x]['points'], reverse=True)
    leaderboard = list(enumerate(leaderboard))
    embed = discord.Embed(colour=discord.Colour(0x278d89))
    embed.set_thumbnail(url='https://cgg.website/lb.png')
    players_list = ''
    points_list = ''
    for place, entry in leaderboard[:10]:
        user_points = users[entry]['points']
        player = await bot.get_user_info(entry)  # will be server.get_member(entry)
        players_list += f'**#{place+1}** {player.mention}\n'
        points_list += f'{user_points}\n'

    embed.add_field(name='Players', value=players_list)
    embed.add_field(name='Points', value=points_list)
    await bot.say(embed=embed)


@bot.command(pass_context=True, hidden=True)
async def purge(ctx, number):
    if ctx.message.author.id != '245276992432373760':
        await bot.say('no')
        return

    mgs = []
    number = int(number)
    async for x in bot.logs_from(ctx.message.channel, limit=number):
        mgs.append(x)
    await bot.delete_messages(mgs)


async def ink_timer(player, submessage, name):
    counter = 0
    while True:
        user_list = []
        for user in users:
            user_list.append(user)
        randomperson = random.choice(user_list)
        counter = counter + 1
        points = config.data.get('users').get(randomperson).get('points')
        value = config.data.get('items').get(submessage).get('value')
        new_points = points + value
        config.data['users'][randomperson]['points'] = int(new_points)
        config.save()
        await bot.say(f'<@{player}> has used {name} on <@{randomperson}> they now have {new_points}')
        if counter == 10:
            break
        else:
            await  asyncio.sleep(180)

@bot.command(pass_context=True)
async def use(ctx, message: str = None):
    itemlist = config.data.get('items')
    list_items = []
    for item in itemlist:
        list_items.append(item)
    submessage = re.sub('[><]', '', message)
    if submessage not in list_items:
        await bot.say('Thats not an item')
        return

    if submessage is None:
        await bot.say('list items here')
        return

    if submessage in list_items:
        above = config.data.get('items').get(submessage).get('above')
        below = config.data.get('items').get(submessage).get('below')
        cost = config.data.get('items').get(submessage).get('cost')
        target = config.data.get('items').get(submessage).get('target')
        value = config.data.get('items').get(submessage).get('value')
        amount = config.data.get('users').get(ctx.message.author.id).get('itemlist').get(submessage)

        if amount == 0 or amount is None:
            await bot.say(f'you have no {message} to use')
            return

        new_amount = amount - 1
        config.data['users'][ctx.message.author.id]['itemlist'][submessage] = int(new_amount)
        if new_amount is 0:
            config.data['users'][ctx.message.author.id]['itemlist'].pop(submessage, None)
        config.save()
        leaderboard = sorted(users, key=lambda x: users[x]['points'], reverse=True)
        position = leaderboard.index(ctx.message.author.id)
        if target is None:
            if above is True:
                if position is 0:
                    await bot.say(f'You are in position {position+1}, you can\'t use this item')
                    return

                else:
                    points_above = config.data.get('users').get(leaderboard[position-1]).get('points')
                    new_points_above = int(points_above) + int(value)
                    if new_points_above <= 0:
                        new_points_above = int(0)
                    config.data['users'][leaderboard[position-1]]['points'] = int(new_points_above)
                    config.save()
                    await bot.say(f'<@{leaderboard[position-1]}> now has {new_points_above} points')

            if below is True:
                if position + 1 == len(users):
                    await bot.say(f'You are in position {position+1}(last place) you can\'t use this item')
                    return

                else:
                    points_below = config.data.get('users').get(leaderboard[position+1]).get('points')
                    new_points_below = int(points_below) + int(value)
                    if new_points_below <= 0:
                        new_points_below = int(0)
                    config.data['users'][leaderboard[position+1]]['points'] = int(new_points_below)
                    config.save()
                    await bot.say(f'<@{leaderboard[position+1]}> now has {new_points_below} points.')
                    return


        if target is not None:
            if target == "random":
                if message == "<:ink:465333794354757632>":
                    name = config.data.get('items').get(submessage).get('name')
                    await ink_timer(ctx.message.author.id, submessage, name)
                    return
                if message == "<:ink:465333794354757632>":
                    await bot.say(f'{ctx.message.author.mention} has used an :ink:!')
                    return

                if message == "<:boo:465654825187541002>":
                    await bot.say('boo has not been configured.')
                    return

                else:
                    leaderboard = sorted(users, key=lambda x: users[x]['points'], reverse=True)
                    pick_random_user = random.choice(leaderboard)
                    points_old = config.data.get('users').get(pick_random_user).get('points')
                    new_points_random = int(points_old) + int(value)
                    if new_points_random <= 0:
                        new_points_random = int(0)
                    config.data['users'][pick_random_user]['points'] = int(new_points_random)
                    config.save()
                    await bot.say(f'<@{pick_random_user}> now has {new_points_random} points.')
                    return


            if target == "all":
                await bot.say(f'target is {value} {target}')
                return

            if target == "self":
                await bot.say(f'target is {value} {target}')
                return

            if target == "targeted":
                await bot.say(f'target is {value} {target}')
                return

            if target == "top":
                leaderboard = sorted(users, key=lambda x: users[x]['points'], reverse=True)
                points_old = config.data.get('users').get(leaderboard[0]).get('points')
                new_points = points_old + value
                config.data['users'][leaderboard[0]]['points'] = int(new_points)
                config.save()
                await bot.say(f'<@{leaderboard[0]}> now has {new_points} points.')
                return



    else:
        await bot.say('shrug')
        return



'''    
    if message == '<:tack:464785937902338058>' or message == 'tack':
        author = ctx.message.author
        leaderboard = sorted(users, key=lambda x: users[x]['points'], reverse=True)
        position = leaderboard.index(author.id)
        amount = config.data.get('users').get(ctx.message.author.id).get('itemlist').get(':tack:')
        if amount is 0:
            await bot.say('you have none to use!')
            return

        if position + 1 == len(users):
            await bot.say('There is no one below you to use that item!')
            return

        else:
            old_points = config.data.get('users').get(leaderboard[position + 1]).get('points')
            await bot.say('<@{}> has {} points'.format(leaderboard[position + 1], old_points))
            new_points = int(old_points) - int(4)
            new_amount = int(amount) - 1
            config.data['users'][ctx.message.author.id]['itemlist'][':tack:'] = new_amount
            config.data['users'][leaderboard[position + 1]]['points'] = int(new_points)
            config.save()

            await bot.say('{} used :tack: on <@{}> they now have {} points'.format(ctx.message.author.mention, leaderboard[position + 1], new_points))
            return
'''


@bot.command(pass_context=True, hidden=True)
async def addpoints(ctx, message: str = None):

    if ctx.message.author.id != '245276992432373760':
        await bot.say('no')
        return

    mention_list = []
    for mention in ctx.message.mentions:
        mention_list.append(mention.id)
    user = str(mention_list).replace('[', '').replace(']', '').replace('\'', '')

    if message is None:
        await bot.say('You need to include a user.')
        return

    if len(mention_list) >= 2:
        await bot.say('It seems you are trying to get the points of multiple people, I can\'t do that.')
        return

    if not message.startswith('<@'):
        await bot.say('Message must start with a mention.')
        return

    value = str(ctx.message.content).split('> ')
    if len(mention_list) == 1:
        if message.startswith('<@'):
            if len(value) <= 1:
                await bot.say('You should include how many points you would like to add')
                return
            else:
                try:
                    messagecheck = value[1]
                    messagecheck = int(messagecheck)

                except:
                    await bot.say('{} is not and int.'.format(messagecheck))
                    return
            old_points = config.data.get('users').get(user).get('points')
            new_points = int(old_points) + int(value[1])
            config.data['users'][user]['points'] = int(new_points)
            config.save()
            await bot.say('added {} points to <@{}>'.format(value[1], user))
            return

        else:
            await bot.say('The message needs to start with a mention.')
            return



bot.loop.run_until_complete(connect())