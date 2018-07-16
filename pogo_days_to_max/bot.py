from discord.ext import commands
import discord
import asyncio
import datetime

token = ''

bot = commands.Bot(command_prefix='~')


@bot.event
async def on_ready():
    print('Logged in as: ' + bot.user.name)
    print('Bot ID: ' + bot.user.id)


async def connect():
    print('Logging in...')
    while not bot.is_closed:
        try:
            await bot.start(token)
        except:
            await asyncio.sleep(5)


@bot.command(pass_context=True, hidden=True)
async def days(ctx, xp: str = None, start_date: str=None):
    '''Estimate how many days it will take you to reach lvl 40 at your current pace.

    Usage:
    ~days <xp> <date>
    Date format is mm/dd/yy'''
    if not xp.isdigit() or not start_date:
        help_description = bot.formatter.format_help_for(ctx, bot.commands.get('days'))[0]
        await bot.say(f'{help_description}')
        return
    else:
        try:
            start_date = datetime.datetime.strptime(start_date, '%m/%d/%Y').date()
        except:
            await bot.say('date format incorrect')
            return

    xp = int(xp)
    now = datetime.date.today()
    days = (now - start_date).days
    xpperday = xp // days
    daysleft = (20000000 - xp) // xpperday
    embed = discord.Embed(colour=discord.Colour(0x00bcd4),
                          description=f'XP/day: {xpperday:,} \nEstimated days until max level: {daysleft:,}')
    await bot.say(embed=embed)
    return

bot.loop.run_until_complete(connect())
