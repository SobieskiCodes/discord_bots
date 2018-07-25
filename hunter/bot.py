import discord
from discord.ext import commands
import asyncio
from pyson import Pyson
config = Pyson('data.json')
token = config.data.get('config').get('token')
bot = commands.Bot(command_prefix='!')

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
    print('------')


async def connect():
    print('Logging in...')
    while not bot.is_closed:
        try:
            await bot.start(token)
        except:
            await asyncio.sleep(5)


@bot.command(pass_context=True)
async def add(ctx, name: str=None):
    """!add <name> - add your pro name"""
    if not name:
        await bot.say('Please provide a name for yourself.')
        return
    else:
        if ctx.message.author.id not in config.data.get('users'):
            print('made it')
            new_user = {"name": name, "wins": 0, "points": 0, "losses": 0, "streak": 0}
            config.data['users'][ctx.message.author.id] = new_user
            config.save()
            await bot.say(f'{name} added under {ctx.message.author.mention}')
        else:
            await bot.say(f'{ctx.message.author.mention} it seems you are already in the database..')
            return


@bot.command(pass_context=True)
async def lb(ctx):
    """!lb - Check the leaderboard"""
    if not config.data.get('users'):
        await bot.say('No users have been added!')
        return

    await bot.send_typing(ctx.message.channel)
    users = config.data.get('users')
    leaderboard = sorted(users, key=lambda x: users[x]['points'], reverse=True)
    leaderboard = list(enumerate(leaderboard))
    embed = discord.Embed(colour=discord.Colour(0x278d89))
    players_list = ''
    for place, entry in leaderboard[:10]:
        user_points = users[entry]['points']
        wins = users[entry]['wins']
        name = users[entry]['name']
        if len(str(wins)) is 1:
            wins = f'0{wins}'
        if len(str(user_points)) is 1:
            user_points = f'0{user_points}'
        players_list += f'**#{place+1}.**     Wins:{wins}     Points: {user_points}     {name}\n'

    embed.add_field(name='Leaderboard', value=players_list)
    await bot.say(embed=embed)


@bot.command(pass_context=True)
async def beat(ctx):
    """!beat @user - you won a duel against mentioned player"""
    if not ctx.message.raw_mentions:
        await bot.say('No mentions')
        return
    else:
        if len(ctx.message.raw_mentions) > 1:
            await bot.say('Too many mentions')
            return

        else:
            users = config.data.get('users')
            if ctx.message.raw_mentions[0] not in users:
                await bot.say(f"I couldn't find one of those users.")
                return

            bonus = {5: 5, 10: 10, 15: 15, 20: 20, 25: 25, 30: 30, 35: 35, 40: 40, 45: 45, 50: 50}
            person_to_mention = ctx.message.server.get_member(ctx.message.raw_mentions[0]) #gets the only mentions ID
            player_wins = config.data.get('users').get(ctx.message.author.id).get('wins')
            opponent_losses = config.data.get('users').get(person_to_mention.id).get('losses')
            old_player_streak = config.data.get('users').get(ctx.message.author.id).get('streak')
            player_points = config.data.get('users').get(ctx.message.author.id).get('points')
            config.data['users'][ctx.message.author.id]['wins'] = player_wins + 1
            config.data['users'][ctx.message.author.id]['streak'] = old_player_streak + 1
            config.data['users'][person_to_mention.id]['losses'] = opponent_losses + 1
            config.data['users'][person_to_mention.id]['streak'] = 0
            new_player_streak = config.data.get('users').get(ctx.message.author.id).get('streak')
            if new_player_streak in bonus:
                new_player_points = player_points + 1 + bonus.get(new_player_streak)
            else:
                new_player_points = player_points + 1
            config.data['users'][ctx.message.author.id]['points'] = new_player_points
            config.save()
            await bot.say(f'{ctx.message.author.mention} just beat {person_to_mention.mention}.')
            return


@bot.command(pass_context=True)
async def correct(ctx, p1: str=None, p2: str=None):
    """!correct @user  @user - fix win/loss of two players
    first user is the user you want to remove points/wins from
    second user is the user you wish to remove the loss from (subract one loss)
    """
    if ctx.message.author is ctx.message.server.owner:
        if not p1 or not p2:
            await bot.say('It seems the format is incorrect, please try !correct @user1 @user2')
            return

        if len(ctx.message.raw_mentions) != 2:
            await bot.say('The correct usage is !correct @user1 @user2')
            return

        else:
            p1 = ctx.message.raw_mentions[0]
            person1 = ctx.message.server.get_member(ctx.message.raw_mentions[0])
            p2 = ctx.message.raw_mentions[1]
            person2 = ctx.message.server.get_member(ctx.message.raw_mentions[1])
            p1_wins = config.data.get('users').get(p1).get('wins')
            p1_points = config.data.get('users').get(p1).get('points')
            p1_streak = config.data.get('users').get(p1).get('streak')
            p2_losses = config.data.get('users').get(p2).get('losses')
            users = config.data.get('users')
            if p1 not in users or p2 not in users:
                await bot.say(f"I couldn't find one of those users.")
                return

            if p1_wins == 0:
                await bot.say(f'{person1.mention} already has 0 wins.')
                return
            if p2_losses == 0:
                await bot.say(f'{person2.mention} already has 0 losses.')
                return
            else:
                config.data['users'][p1]['wins'] = p1_wins - 1
                config.data['users'][p2]['losses'] = p2_losses - 1
                bonus = {5: 5, 10: 10, 15: 15, 20: 20, 25: 25, 30: 30, 35: 35, 40: 40, 45: 45, 50: 50}
                p1_points_to_lose = p1_points - 1
                if p1_streak in bonus:
                    p1_points_to_lose = p1_points - 1 - bonus.get(p1_streak)
                config.data['users'][p1]['points'] = p1_points_to_lose
                p1_new_streak = 0
                if p1_streak != 0:
                    p1_new_streak = p1_streak - 1
                p1_new_streak = p1_streak - 1
                config.data['users'][p1]['streak'] = p1_new_streak
                config.save()

    else:
        await bot.say(f'{ctx.message.author.mention}, you are not authorized to use this command.')


@bot.command(pass_context=True)
async def streak(ctx):
    """!streak - Check your current win streak"""
    streak = config.data.get('users').get(ctx.message.author.id).get('streak')
    await bot.say(f'{ctx.message.author.mention}, you have a streak of {streak}')


@bot.command(pass_context=True)
async def losses(ctx):
    """!losses - Check your current losses"""
    losses = config.data.get('users').get(ctx.message.author.id).get('losses')
    await bot.say(f'{ctx.message.author.mention}, you have {losses} losses.')


@bot.command(pass_context=True)
async def wins(ctx):
    """!wins - Check your current wins"""
    wins = config.data.get('users').get(ctx.message.author.id).get('wins')
    await bot.say(f'{ctx.message.author.mention}, you have {wins} wins.')


@bot.command(pass_context=True)
async def points(ctx):
    """!points - Check your current points"""
    points = config.data.get('users').get(ctx.message.author.id).get('points')
    await bot.say(f'{ctx.message.author.mention}, you have {points} points.')


bot.loop.run_until_complete(connect())
