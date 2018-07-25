import discord
from discord.ext import commands
import asyncio
import pyson
import random
from datetime import datetime
import time


bot = commands.Bot(command_prefix='.')
config = pyson.Pyson('data.json')
trivia = pyson.Pyson('QnA.json')
token = config.data.get('config').get('token')
users = config.data.get('users')
boottime = datetime.now()
version = '0.0.9'



@bot.event
async def on_ready():
    print('Logged in as: '+bot.user.name)
    print('Bot ID: '+bot.user.id)
    print('Invite Link Below')
    print('------')
    print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=0'.format(bot.user.id))
    print('------')
    for server in bot.servers:
        asyncio.ensure_future(top10(server))
        asyncio.ensure_future(giveaway(server))
        asyncio.ensure_future(start_q_channel(server))
        print("Connected to server: {} with id: {}".format(server, server.id))
        for member in server.members:
            if not member.bot:
                if member.id not in config.data.get('users'):
                    new_user = {"itemlist": {}, "points": 0}
                    config.data['users'][member.id] = new_user
                    config.save()
                    await asyncio.sleep(1)
                    print('{} has been added'.format(member))
    print('------')


async def connect():
    print('Logging in...')
    while not bot.is_closed:
        try:
            await bot.start(token)
        except:
            await asyncio.sleep(5)


@bot.event
async def on_server_join(server):
    questions_channel = discord.utils.get(server.channels, name='questions', type=discord.ChannelType.text)
    events_channel = discord.utils.get(server.channels, name='events', type=discord.ChannelType.text)
    leaderboard_channel = discord.utils.get(server.channels, name='leaderboard', type=discord.ChannelType.text)
    if not questions_channel:
        await bot.create_channel(server, "questions", type=discord.ChannelType.text)

    if not events_channel:
        await bot.create_channel(server, "events", type=discord.ChannelType.text)

    if not leaderboard_channel:
        await bot.create_channel(server, "leaderboard", type=discord.ChannelType.text)



@bot.command(pass_context=True, hidden=True)
async def about(ctx):
    """What version am I?"""
    owner = '245276992432373760'

    if ctx.message.author.id != owner:
        return

    else:
        await bot.send_typing(ctx.message.channel)
        counter = 0
        with open('jellybot.py', 'r') as data:
            for line in data:
                # if line is not '\n':
                counter += 1


        developer = await bot.get_user_info('245276992432373760')
        game_designer = await bot.get_user_info('231587988323172352')
        time = datetime.now() - boottime
        days = time.days
        hours, remainder = divmod(time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        onlinefor = "{}:days {}:hours {}:minutes and {}:seconds!".format(days, hours, minutes, seconds)

        embed = discord.Embed(colour=discord.Colour(0x50bdfe),
                              description=f"Here is some information about me... "
                                          f"                                                                           "
                                          f"```Version: {version}\n"
                                          f"Library: Discord.py\n"
                                          f"Uptime: {onlinefor}\n"
                                          f"LoC: {counter}\n"
                                          f"Developer: {developer}\n"
                                          f"Game Designer: {game_designer}```")
        embed.set_footer(text='justin@sobieski.codes')
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


async def giveaway(server):
    await bot.wait_until_ready()
    user_list = []
    for user in users:
        user_list.append(user)
    while not bot.is_closed:
        await asyncio.sleep(600)
        pickone = random.choice(user_list)
        events_channel = discord.utils.get(server.channels, name='events', type=discord.ChannelType.text)
        user_old_points = config.data.get('users').get(pickone).get('points')
        new_points = user_old_points + 10
        config.data['users'][pickone]['points'] = int(new_points)
        config.save()
        embed = discord.Embed(colour=discord.Colour(0x7cb342),
                              description=f'<@{pickone}> just recieved 10 points from the giveaway and now has '
                                          f'{new_points} points!')
        await bot.send_message(events_channel, embed=embed)


async def purge_channel(server):
    q_channel = discord.utils.get(server.channels, name='questions', type=discord.ChannelType.text)
    await bot.send_message(q_channel, 'Channel will be purged in 5m.')
    await asyncio.sleep(15)
    mgs = []
    async for x in bot.logs_from(q_channel, limit=100000):
        mgs.append(x)

    while len(mgs) > 100:
        mgs = mgs[:100]
        await bot.delete_messages(mgs)
        if len(mgs) < 100:
            await bot.delete_messages(mgs)

    await bot.delete_messages(mgs)
    return


async def start_q_channel(server):
    while not bot.is_closed:
        class Timer:
            timer = True

        async def set_timer():
            await asyncio.sleep(30)
            Timer.timer = False

        q_channel = discord.utils.get(server.channels, name='questions', type=discord.ChannelType.text)
        events_channel = discord.utils.get(server.channels, name='events', type=discord.ChannelType.text)
        trivia_question = trivia.data.get('questions')
        question_list = []
        for question in trivia_question:
            question_list.append(question)
        pick_question = random.choice(question_list)
        question = trivia.data.get('questions').get(pick_question).get('question')
        answer = trivia.data.get('questions').get(pick_question).get('answer')
        await bot.send_message(q_channel, f'Question time! \n```{question}```')
        guess = None
        bot.loop.create_task(set_timer())
        while not guess and Timer.timer:
            guess_msg = await bot.wait_for_message(timeout=30, channel=q_channel)
            if guess_msg:
                guess = guess_msg.content.lower()
                if guess == answer:
                    user_points = config.data.get('users').get(guess_msg.author.id).get('points')
                    new_points = user_points + 10
                    config.data['users'][guess_msg.author.id]['points'] = int(new_points)
                    config.save()
                    embed = discord.Embed(colour=discord.Colour(0x06f116), description=f'{guess_msg.author.mention},'
                                    f'you have guessed correctly and earned 10 points, for a total of {new_points}!')
                    await bot.send_message(q_channel, embed=embed)

                    event = discord.Embed(colour=discord.Colour(0x06f116), description=f'{guess_msg.author.mention}'
                                                                                         f' has answered "{question}" '
                                                f'correctly and earned 10 points, they now have {new_points} points!')
                    await bot.send_message(events_channel, embed=event)
                    bot.loop.create_task(purge_channel(server))
                else:
                    guess = None
        if not guess:
            embed = discord.Embed(colour=discord.Colour(0xf20707),
                              description=f'Nobody got the question correct!')
            await bot.send_message(q_channel, embed=embed)
            bot.loop.create_task(purge_channel(server))

        await asyncio.sleep(120)


@bot.command(pass_context=True)
async def buy(ctx, message: str = None):
    events_channel = discord.utils.get(ctx.message.server.channels, name='events', type=discord.ChannelType.text)
    item_list = ['weak', 'skilled', 'frantic']

    if message is None:
        await bot.say('Categories are weak, skilled, and frantic.')
        return

    message = message.lower()

    items = config.data.get('items')
    weak_items = []
    skilled_items = []
    frantic_items = []
    for item in items:
        cost = config.data.get('items').get(item).get('cost')
        if cost is 5:
            weak_items.append(item)
        if cost is 15:
            skilled_items.append(item)
        if cost is 30:
            frantic_items.append(item)

    if message in item_list:
        weak_recieve = random.choice(weak_items)
        skilled_recieve = random.choice(skilled_items)
        frantic_recieve = random.choice(frantic_items)

        if message == 'weak':
            item_recieved = weak_recieve

        if message == 'skilled':
            item_recieved = skilled_recieve

        if message == 'frantic':
            item_recieved = frantic_recieve

        name = config.data.get('items').get(item_recieved).get('name')

        player_inventory = config.data.get('users').get(ctx.message.author.id).get('itemlist')
        amount_to_add = []
        for item in player_inventory:
            get_amount = config.data.get('users').get(ctx.message.author.id).get('itemlist').get(item)
            amount_to_add.append(int(get_amount))

        if len(amount_to_add) == 0:
            config.data['users'][ctx.message.author.id]['itemlist'][item_recieved] = 1
            config.save()
            embed = discord.Embed(colour=discord.Colour(0xb2ff59),
                                  description=f'{ctx.message.author.mention} you recieved {name}')
            await bot.send_message(events_channel, embed=embed)
            return

        else:
            total = 0
            for item in amount_to_add:
                total = int(total) + int(item)

            if total >= 3:
                embed = discord.Embed(colour=discord.Colour(0xb2ff59),
                                          description=f'{ctx.message.author.mention} you have too many items already, '
                                                      f'please use one first.')
                await bot.send_message(events_channel, embed=embed)
                return

            else:
                get_player_inventory = config.data.get('users').get(ctx.message.author.id).get('itemlist')
                if item_recieved in get_player_inventory:
                    get_current_amount = config.data.get('users').get(ctx.message.author.id).get('itemlist').get(item_recieved)
                    new_value = get_current_amount + 1
                    config.data['users'][ctx.message.author.id]['itemlist'][item_recieved] = new_value
                    config.save()
                    embed = discord.Embed(colour=discord.Colour(0xb2ff59),
                                          description=f'{ctx.message.author.mention} you recieved {name}')
                    await bot.send_message(events_channel, embed=embed)
                    return

                else:
                    config.data['users'][ctx.message.author.id]['itemlist'][item_recieved] = 1
                    config.save()
                    embed = discord.Embed(colour=discord.Colour(0xb2ff59),
                                          description=f'{ctx.message.author.mention} you recieved {name}')
                    await bot.send_message(events_channel, embed=embed)
                    return

    else:
        await bot.say('item categories are weak, skilled and frantic.')
        return


@bot.command(pass_context=True)
async def store(ctx, message: str = None):
    if message is not None:
        await bot.say('this command does not accept parameters.')
        return

    get_items = config.data.get('items')
    embed = discord.Embed(title="Store", description=ctx.message.author.mention,
                          colour=discord.Colour(0x278d89))

    itemsort = sorted(get_items, key=lambda x: get_items[x]['cost'], reverse=False)
    items = ''
    descriptions = ''
    for item in itemsort:
        description = config.data.get('items').get(item).get('description')
        category = config.data.get('items').get(item).get('group')
        items += f'{item} ({category})\n'
        descriptions += f'{description}\n'

    embed.add_field(name='Item & category', value=items)
    embed.add_field(name='Description', value=descriptions)
    await bot.say(embed=embed)


@bot.command(pass_context=True)
async def pos(ctx, message: str = None):
    events_channel = discord.utils.get(ctx.message.server.channels, name='events', type=discord.ChannelType.text)
    if message is None:
        author = ctx.message.author
        leaderboard = sorted(users, key=lambda x: users[x]['points'], reverse=True)
        position = leaderboard.index(author.id)
        embed = discord.Embed(colour=discord.Colour(0x8e24aa),
                              description=f'{ctx.message.author.mention} you are in position {position+1}')
        await bot.send_message(events_channel, embed=embed)
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
                    embed = discord.Embed(colour=discord.Colour(0x8e24aa),
                                          description=f'<@{user}> is in position {position}')
                    await bot.send_message(events_channel, embed=embed)


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
    events_channel = discord.utils.get(ctx.message.server.channels, name='events', type=discord.ChannelType.text)
    if message is None:
        try:
            get_inventory = config.data.get('users').get(ctx.message.author.id).get('itemlist')
            embed = discord.Embed(title="Inventory", description=ctx.message.author.mention,
                                  colour=discord.Colour(0xffeb3b))
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
            await bot.send_message(events_channel, embed=embed)
        except:
            embed = discord.Embed(title="Inventory", description=ctx.message.author.mention,
                                  colour=discord.Colour(0xffeb3b))
            embed.add_field(name='Item & Amount', value="None")
            embed.add_field(name='Description', value='None')
            await bot.send_message(events_channel, embed=embed)

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
                                              colour=discord.Colour(0xffeb3b))
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
                        await bot.send_message(events_channel, embed=embed)
                    except:
                        embed = discord.Embed(title="Inventory", description='<@{}>'.format(stripmessage),
                                              colour=discord.Colour(0xffeb3b))
                        embed.add_field(name='Item & Amount', value="None")
                        embed.add_field(name='Description', value='None')
                        await bot.send_message(events_channel, embed=embed)

            else:
                await bot.say('The message needs to start with a mention.')
                return


async def top10(server):
    l_channel = discord.utils.get(server.channels, name='leaderboard', type=discord.ChannelType.text)
    await bot.wait_until_ready()
    while not bot.is_closed:
        async for message in bot.logs_from(l_channel):
            print(message)

        await bot.delete_message(message)

        await bot.send_typing(l_channel)
        leaderboard = sorted(users, key=lambda x: users[x]['points'], reverse=True)
        leaderboard = list(enumerate(leaderboard))
        embed = discord.Embed(colour=discord.Colour(0x278d89))
        embed.set_thumbnail(url='https://cgg.website/lb.png')
        players_list = ''
        points_list = ''
        for place, entry in leaderboard[:10]:
            user_points = users[entry]['points']
            player = await bot.get_user_info(entry)
            players_list += f'**#{place+1}** {player.mention}\n'
            points_list += f'{user_points}\n'

        embed.add_field(name='Players', value=players_list)
        embed.add_field(name='Points', value=points_list)
        now = time.ctime()
        embed.set_footer(text=f'Last update at {now}')
        await bot.send_message(l_channel, embed=embed)
        await asyncio.sleep(1800)


async def item_timer(player, emoji, server):
    counter = 0
    while True:
        user_list = []
        for user in users:
            user_list.append(user)

        randomperson = random.choice(user_list)
        if randomperson == player:
            while randomperson == player:
                randomperson = random.choice(user_list)

        events_channel = discord.utils.get(server.channels, name='events', type=discord.ChannelType.text)
        counter = counter + 1
        points = config.data.get('users').get(randomperson).get('points')
        value = config.data.get('items').get(emoji).get('value')
        new_points = points + value
        if new_points <= 0:
            new_points = 0
        config.data['users'][randomperson]['points'] = int(new_points)
        config.save()
        embed = discord.Embed(colour=discord.Colour(0xc62828),
                              description=f'<@{player}> '
                                          f'used <{emoji}> on <@{randomperson}>, they now have {new_points} points!')
        await bot.send_message(events_channel, embed=embed)

        if counter == 10:
            break
        else:
            await  asyncio.sleep(180)


async def remove_item(player, item, amount):
    new_amount = amount - 1
    config.data['users'][player]['itemlist'][item] = int(new_amount)
    if new_amount == 0:
        config.data['users'][player]['itemlist'].pop(item, None)
    config.save()


@bot.command(pass_context=True)
async def use(ctx, emoji: discord.Emoji):
    events_channel = discord.utils.get(ctx.message.server.channels, name='events', type=discord.ChannelType.text)

    itemlist = config.data.get('items')

    if isinstance(emoji, discord.Emoji):
        emoji = emoji.name

    list_items = []
    for item in itemlist:
        list_items.append(item)

    if emoji not in list_items:
        await bot.say('Thats not an item')
        return

    if emoji is None:
        await bot.say('you didn\'t try to use anything')
        return

    if emoji in list_items:
        above = config.data.get('items').get(emoji).get('above')
        below = config.data.get('items').get(emoji).get('below')
        cost = config.data.get('items').get(emoji).get('cost')
        target = config.data.get('items').get(emoji).get('target')
        value = config.data.get('items').get(emoji).get('value')
        amount = config.data.get('users').get(ctx.message.author.id).get('itemlist').get(emoji)
        description = config.data.get('items').get(emoji).get('description')

        if amount == 0 or amount is None:
            await bot.say(f'you have no {emoji} to use')
            return

        if cost is 5:
            embed = discord.Embed(colour=discord.Colour(0x00bcd4),
                                  description=f'{ctx.message.author.mention} used {emoji} : "{description}"')
            await bot.send_message(events_channel, embed=embed)
        if cost is 15:
            embed = discord.Embed(colour=discord.Colour(0x1976d2),
                                  description=f'{ctx.message.author.mention} used {emoji} : "{description}"')
            await bot.send_message(events_channel, embed=embed)
        if cost is 30:
            embed = discord.Embed(colour=discord.Colour(0x1a237e),
                                  description=f'{ctx.message.author.mention} used {emoji} : "{description}"')
            await bot.send_message(events_channel, embed=embed)

        leaderboard = sorted(users, key=lambda x: users[x]['points'], reverse=True)
        position = leaderboard.index(ctx.message.author.id)
        get_emoji = discord.utils.get(ctx.message.server.emojis, name=emoji)
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
                    embed = discord.Embed(colour=discord.Colour(0xc62828),
                                          description=f'{ctx.message.author.mention}\'s {get_emoji} just hit '
                                          f'<@{leaderboard[position-1]}>! They now have {new_points_above} points!')
                    await bot.send_message(events_channel, embed=embed)
            bot.loop.create_task(remove_item(ctx.message.author.id, emoji, amount))

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
                    embed = discord.Embed(colour=discord.Colour(0xc62828),
                                          description=f'{ctx.message.author.mention}\'s {get_emoji} just hit '
                                          f'<@{leaderboard[position+1]}>! They now have {new_points_below} points!')
                    await bot.send_message(events_channel, embed=embed)
                    return

        if target is not None:
            if target == "random":
                if emoji == "ink":
                    bot.loop.create_task(item_timer(ctx.message.author.id, emoji, ctx.message.server))
                    bot.loop.create_task(remove_item(ctx.message.author.id, emoji, amount))
                    return

                if emoji == "sprinkler":
                    bot.loop.create_task(item_timer(ctx.message.author.id, emoji, ctx.message.server))
                    bot.loop.create_task(remove_item(ctx.message.author.id, emoji, amount))
                    return

                if emoji == "boo":
                    bot.loop.create_task(item_timer(ctx.message.author.id, emoji, ctx.message.server))
                    return

                else:
                    leaderboard = sorted(users, key=lambda x: users[x]['points'], reverse=True)
                    pick_random_user = random.choice(leaderboard)

                    if pick_random_user == ctx.message.author.id:
                        while pick_random_user == ctx.message.author.id:
                            pick_random_user = random.choice(leaderboard)

                    points_old = config.data.get('users').get(pick_random_user).get('points')
                    new_points_random = int(points_old) + int(value)

                    if new_points_random <= 0:
                        new_points_random = int(0)
                    config.data['users'][pick_random_user]['points'] = int(new_points_random)
                    config.save()
                    embed = discord.Embed(colour=discord.Colour(0xc62828),
                                          description=f'{ctx.message.author.mention}\'s {get_emoji} hit '
                                          f'<@{pick_random_user}>! They now have {new_points_random} points!')
                    await bot.send_message(events_channel, embed=embed)
                    bot.loop.create_task(remove_item(ctx.message.author.id, emoji, amount))
                    return

            if target == "all":
                await bot.say(f'target is {value} {target}')
                return

            if target == "self":
                points_old_self = config.data.get('users').get(ctx.message.author.id).get('points')
                value = config.data.get('items').get(emoji).get('value')
                new_points_self = points_old_self + value
                config.data['users'][ctx.message.author.id]['points'] = int(new_points_self)
                config.save()
                embed = discord.Embed(colour=discord.Colour(0xc62828),
                                      description=f'{ctx.message.author.mention}\'s used {get_emoji} and gained '
                                                  f'{value} points, for a total of {new_points_self} points.')
                await bot.send_message(events_channel, embed=embed)
                bot.loop.create_task(remove_item(ctx.message.author.id, emoji, amount))
                return

            if target == "steal":
                user_list = []
                for user in users:
                    user_list.append(user)

                target = None
                while not target:
                    target = random.choice(user_list)
                    items = config.data.get('users').get(target).get('itemlist')
                    if target == ctx.message.author.id:
                        target = None
                    if len(items) == 0:
                        target = None

                item_list = []
                targets_items = config.data.get('users').get(target).get('itemlist')
                for item in targets_items:
                    item_list.append(item)
                item_to_steal = random.choice(item_list)

                amount_item_target = config.data.get('users').get(target).get('itemlist').get(item_to_steal)
                new_amount_item_target = amount_item_target - 1
                if new_amount_item_target == 0:
                    config.data['users'][target]['itemlist'].pop(item_to_steal, None)
                config.save()
                player_items = config.data.get('users').get(ctx.message.author.id).get('itemlist')
                player_items_list = []
                for item in player_items:
                    player_items_list.append(item)

                if item_to_steal in player_items_list:
                    amount = config.data.get('users').get(ctx.message.author.id).get('itemlist').get(item_to_steal)
                    new_amount = amount + 1
                    config.data['users'][ctx.message.author.id]['itemlist'][item_to_steal] = new_amount
                config.save()

                if item_to_steal not in player_items_list:
                    config.data['users'][ctx.message.author.id]['itemlist'][item_to_steal] = 1
                config.save()

                value = config.data.get('items').get(emoji).get('value')
                if value > 0:
                    get_points = config.data.get('users').get(ctx.message.author.id).get('points')
                    new_points = get_points + value
                    config.data['users'][ctx.message.author.id]['points'] = new_points
                config.save()
                await remove_item(ctx.message.author.id, emoji, amount)
                name = config.data.get('items').get(item_to_steal).get('name')
                embed = discord.Embed(colour=discord.Colour(0xc62828),
                                      description=f'{ctx.message.author.mention}\'s {get_emoji} hit '
                                                  f'<@{target}> and stole {name}!')
                await bot.send_message(events_channel, embed=embed)

            if target == "targeted":
                mention_list = []
                for mention in ctx.message.mentions:
                    mention_list.append(mention.id)

                if len(mention_list) < 1:
                    await bot.say('you need to include a mention')
                    return

                if len(mention_list) >= 2:
                    await bot.say('you should include only one mention')
                    return

                if mention_list[0] == ctx.message.author.id:
                    await bot.say('you cant use it on yourself....')
                    return

                if len(mention_list) == 1:
                    bot.loop.create_task(remove_item(ctx.message.author.id, emoji, amount))
                    target = mention_list[0]
                    points_old = config.data.get('users').get(target).get('points')
                    new_points_target = int(points_old) + int(value)
                    if new_points_target <= 0:
                        new_points_target = int(0)
                    config.data['users'][target]['points'] = int(new_points_target)
                    config.save()
                    embed = discord.Embed(colour=discord.Colour(0xc62828),
                                          description=f'{ctx.message.author.mention}\'s {get_emoji} just hit <@{target}>!'
                                                      f' They now have {new_points_target} points!')
                    await bot.send_message(events_channel, embed=embed)
                    return

            if target == "top":
                if position == 0:
                    await bot.say('you cant use this, you are in first')
                    return
                bot.loop.create_task(remove_item(ctx.message.author.id, emoji, amount))
                leaderboard = sorted(users, key=lambda x: users[x]['points'], reverse=True)
                points_old = config.data.get('users').get(leaderboard[0]).get('points')
                new_points = points_old + value
                config.data['users'][leaderboard[0]]['points'] = int(new_points)
                config.save()
                embed = discord.Embed(colour=discord.Colour(0xc62828),
                                      description=f'{ctx.message.author.mention}\'s {get_emoji} just hit '
                                                  f'<@{leaderboard[0]}>! They now have {new_points} points!')
                await bot.send_message(events_channel, embed=embed)
                return
    else:
        await bot.say('shrug')
        return


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
