from discord.ext import commands
import discord
import pyson

config = pyson.Pyson('lfc.json')
token = config.data.get('config').get('token')
bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print(f'https://discordapp.com/oauth2/authorize?client_id={bot.user.id}&scope=bot&permissions=16')
    print('------')


@bot.command()
async def lfc(ctx, ship_name: str=None, amount: str=None):
    """!lfc <ship_name> <amount_of_people> | ship names are galleon, brigantine, brig, or sloop"""
    if not ship_name or not amount or not amount.isdigit():
        await ctx.send('Not valid format, try "!help lfc"')
        return

    ship_name_list = ['galleon', 'brigantine', 'brig', 'sloop']
    if ship_name not in ship_name_list:
        await ctx.send('That is not a valid ship name! Try galleon, brigantine, brig, or sloop')
        return

    amount = int(amount)
    if amount >= 5:
        await ctx.send('Group too big!')
        return

    for category in ctx.guild.categories:
        if category.name == "lfc":

            channel_names = []
            for channel in ctx.guild.channels:
                channel_names.append(channel.name)

            new_channel = f"{ship_name}-{amount}"
            if new_channel in channel_names:
                await ctx.send(f'Already a channel named {new_channel}, maybe you should join that?')
                return

            if str(ctx.message.author.id) not in config.data.get('lfc'):
                create_channel = await ctx.guild.create_text_channel(new_channel, category=category)
                config.data['lfc'][str(ctx.message.author.id)] = create_channel.id
                config.save()
                await create_channel.send("When you no longer need crewmates, please type !done to close this channel")
                return

            else:
                await ctx.send('You already have a channel created...')
                return

    else:
        await ctx.guild.create_category_channel("lfc")
        await ctx.send('no category was created yet - ive created it now')


@bot.command()
async def done(ctx: str=None, chan: str=None):
    """!done - closes your channel"""
    if ctx.message.author is ctx.message.guild.owner or str(ctx.message.author.id) in config.data.get('lfc'):
        if str(ctx.message.author.id) in config.data.get('lfc'):
            channel_id = config.data.get('lfc').get(str(ctx.message.author.id))
            chan = discord.utils.get(ctx.guild.text_channels, id=channel_id)
            chan_to_delete = bot.get_channel(chan.id)
            await chan_to_delete.delete()
            config.data['lfc'].pop(str(ctx.message.author.id), None)
            config.save()
            return

        if ctx.message.author is ctx.message.guild.owner:
            if not chan:
                await ctx.send('Please specify the channel.')
                return

            chan_to_get = discord.utils.get(ctx.guild.text_channels, name=chan)
            if not chan_to_get:
                await ctx.send('No channel found by that name.')
                return

            print(config.data.get('lfc'))
            for key, value in config.data.get('lfc').items():
                if value == chan_to_get.id:
                    config.data['lfc'].pop(key, None)
                    config.save()
                    await ctx.message.author.send('Channel deleted.')
                    return


            chan_to_delete = bot.get_channel(chan_to_get.id)
            await chan_to_delete.delete()

    else:
        await ctx.send('You dont seem to have a created channel.')
        return

bot.run(token)
