from discord.ext import commands
import asyncio

token = ''

bot = commands.Bot(command_prefix='!')
ranks = {
    "400": "400+",
    "300": "300+",
    "200": "200+",
    "100": "100+",
}

@bot.event
async def on_ready():
    print('Logged in as: ' + bot.user.name)
    print('Bot ID: ' + bot.user.id)
    for server in bot.servers:
        asyncio.ensure_future(rename_users(server))


async def connect():
    print('Logging in...')
    while not bot.is_closed:
        try:
            await bot.start(token)
        except:
            await asyncio.sleep(5)


@bot.command(pass_context=True)
async def rename(ctx):
    for member in ctx.message.server.members:
        list_of_ranks = []
        if member != ctx.message.server.owner and not member.bot:
            for role in member.roles:
                for rank in ranks:
                    rank_name = ranks.get(rank)
                    print(f'rolename: {role.name} rank: {rank_name}')
                    if role.name.startswith(rank_name):
                        list_of_ranks.append(rank)
            if list_of_ranks != []:
                highest = max(list_of_ranks)
                highest_rank_name = ranks.get(highest)
                if member.nick != f'[{highest_rank_name}] {member.name}':
                    try:
                        print(f'COMMAND: trying to change {member}\'s name')
                        await bot.change_nickname(member, f'[{highest_rank_name}] {member.name}')
                        print(f'COMMAND: {member}\'s name changed')
                    except:
                        print(f'COMMAND: failed to change {member}\'s name')
                        pass
                else:
                    print(f'COMMAND: {member}\'s name already highest role')
                    pass
        else:
            pass


async def rename_users(server):
    while not bot.is_closed:
        await asyncio.sleep(3600)
        for member in server.members:
            list_of_ranks = []
            if member != server.owner and not member.bot:
                for role in member.roles:
                    for rank in ranks:
                        rank_name = ranks.get(rank)
                        if role.name.startswith(rank_name):
                            list_of_ranks.append(rank)
                if list_of_ranks != []:
                    highest = max(list_of_ranks)
                    highest_rank_name = ranks.get(highest)
                    if member.nick != f'[{highest_rank_name}] {member.name}':
                        try:
                            print(f'TIMER: trying to change {member}\'s name')
                            await bot.change_nickname(member, f'[{highest_rank_name}] {member.name}')
                            print(f'TIMER: {member}\'s name changed')
                        except:
                            print(f'TIMER: failed to change {member}\'s name')
                            pass
                    else:
                        print(f'TIMER: {member}\'s name already highest role')
                        pass
                else:
                    pass


bot.loop.run_until_complete(connect())
