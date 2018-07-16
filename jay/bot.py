from discord.ext import commands
import asyncio

token = ''

bot = commands.Bot(command_prefix='!')
ranks = {
    "Founder": "⓪",
    "Leader": "①",
    "High Council": "②",
    "Warlord": "③",
    "Council": "④",
    "Officer": "⑤",
    "Elder": "⑥",
    "Elite Member": "⑦",
    "Veteran": "⑧",
    "Experienced Member": "⑨",
    "Proud Member": "⑩",
    "Member": "⑪",
    "Applicant": "⑫",
    "Ex-Misfit": "⑬",
    "Clan Friend": "⑭",
    "Special Guest": "⑮",
    "Guest": "⑮",
}

@bot.event
async def on_ready():
    print('Logged in as: ' + bot.user.name)
    print('Bot ID: ' + bot.user.id)
    for server in bot.servers:
        asyncio.ensure_future(rename(server))


async def connect():
    print('Logging in...')
    while not bot.is_closed:
        try:
            await bot.start(token)
        except:
            await asyncio.sleep(5)


@bot.command(pass_context=True)
async def reroll(ctx):
    if ctx.message.author.id != '227222904843141132':
        return

    await bot.delete_message(ctx.message)

    for member in ctx.message.server.members:
        if member is ctx.message.server.owner:
            pass
        for role in member.roles:
            if role.name in ranks:
                rank = ranks.get(role.name)
                if member.nick != f'{rank} {member.name}':
                    try:
                        print(f'COMMAND: {member.name} trying to update')
                        await bot.change_nickname(member, f'{rank} {member.name}')
                        print(f'COMMAND: {member.name} has updated')
                    except:
                        print(f'COMMAND: failed to change rank of {member.name}')
                        pass
                else:
                    print(f'COMMAND: {member.name}\'s name is already "{rank} {member.name}"')
                    pass


async def rename(server):
    while not bot.is_closed:
        await asyncio.sleep(3600)
        for member in server.members:
            if member is server.owner:
                pass
            for role in member.roles:
                if role.name in ranks:
                    rank = ranks.get(role.name)
                    if member.nick != f'{rank} {member.name}':
                        try:
                            print(f'TIMER: {member.name} trying to update')
                            await bot.change_nickname(member, f'{rank} {member.name}')
                            print(f'TIMER: {member.name} has updated')
                        except:
                            print(f'TIMER: failed to change rank of {member.name}')
                            continue
                    else:
                        print(f'TIMER: {member.name}\'s name is already "{rank} {member.name}"')


bot.loop.run_until_complete(connect())

