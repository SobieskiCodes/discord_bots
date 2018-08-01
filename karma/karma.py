import discord
from discord.ext import commands
from .utils import Pyson, checks


class Karma:
    def __init__(self, bot):
        self.bot = bot
        self.currency = Pyson('cogs/data/currency')
        self.check_default()

    def check_default(self):
        if 'name' not in self.currency.data:
            self.currency.data['name'] = 'dollars'

    def check_id(self, ID):
        if ID not in self.currency.data:
            self.currency.data[ID] = {
                'bank': 0,
                'rank': None,
            }
            self.currency.save()

    @commands.command()
    async def profile(self, user: discord.User):
        ''': profile'''
        avatar = user.avatar_url
        self.check_id(user.id)
        currency = self.currency.data["name"]
        amount = self.currency.data.get(user.id).get('bank')
        rank = self.currency.data.get(user.id).get('rank')
        embed = discord.Embed(title=f"{user.name}", description=f'', colour=discord.Colour(0x0AFA02))
        embed.add_field(name=f'{currency}', value=f'{amount}')
        embed.add_field(name='Rank', value=f'{rank}', inline=True)
        embed.set_thumbnail(url=avatar)
        await self.bot.say(embed=embed)

    @commands.command(pass_context=True, aliases=['+'])
    async def pluskarma(self, ctx, mention: str=None):
        ''': add karma'''
        if not mention or not ctx.message.raw_mentions:
            await self.bot.say('No mention!')
            return

        if len(ctx.message.raw_mentions) >= 2:
            await self.bot.say('Too many mentions.')
            return

        if ctx.message.raw_mentions[0] == ctx.message.author.id:
            await self.bot.say('You cant change your own karma you fuck.')
            return
        self.check_id(ctx.message.raw_mentions[0])

        self.currency.data[ctx.message.raw_mentions[0]]['bank'] += 1
        self.currency.save()
        ranks = list(self.currency.data.get('ranks'))
        position = 0
        for rank in ranks:
            if self.currency.data.get(ctx.message.raw_mentions[0]).get('bank') >= self.currency.data.get('ranks').get(rank):
                if rank != (ranks[-1]):
                    position += 1
                    pass
                else:
                    self.currency.data[ctx.message.raw_mentions[0]]['rank'] = rank
                    self.currency.save()
                    break

            if self.currency.data.get(ctx.message.raw_mentions[0]).get('bank') <= self.currency.data.get('ranks').get(rank):
                if rank != (ranks[0]):
                    self.currency.data[ctx.message.raw_mentions[0]]['rank'] = ranks[position-1]
                    self.currency.save()
                    break
                else:
                    self.currency.data[ctx.message.raw_mentions[0]]['rank'] = ranks[position]
                    self.currency.save()
                    break

        user_rank = self.currency.data.get(ctx.message.raw_mentions[0]).get('rank')
        mention_roles = ctx.message.server.get_member(ctx.message.raw_mentions[0])
        if not user_rank:
            role_oject = discord.utils.get(ctx.message.server.roles, name=ranks[0])
            await self.bot.add_roles(mention_roles, role_oject)

        if user_rank:
            role_oject = discord.utils.get(ctx.message.server.roles, name=user_rank)
            await self.bot.replace_roles(mention_roles, role_oject)

        mention_user = ctx.message.server.get_member(ctx.message.raw_mentions[0])
        await self.bot.say(f'{mention_user.mention}\'s karma has been updated, thank you.')

    @commands.command(pass_context=True, aliases=['-'])
    async def minuskarma(self, ctx, mention: str=None):
        ''': remove karma'''
        if not mention or not ctx.message.raw_mentions:
            await self.bot.say('No mention!')
            return

        if len(ctx.message.raw_mentions) >= 2:
            await self.bot.say('Too many mentions.')
            return

        if ctx.message.raw_mentions[0] == ctx.message.author.id:
            await self.bot.say('You cant change your own karma you fuck.')
            return
        self.check_id(ctx.message.raw_mentions[0])

        self.currency.data[ctx.message.raw_mentions[0]]['bank'] -= 1
        self.currency.save()
        ranks = list(self.currency.data.get('ranks'))
        position = 0
        for rank in ranks:
            if self.currency.data.get(ctx.message.raw_mentions[0]).get('bank') >= self.currency.data.get('ranks').get(rank):
                if rank != (ranks[-1]):
                    position += 1
                    pass
                else:
                    self.currency.data[ctx.message.raw_mentions[0]]['rank'] = rank
                    self.currency.save()
                    break

            if self.currency.data.get(ctx.message.raw_mentions[0]).get('bank') <= self.currency.data.get('ranks').get(rank):
                if rank != (ranks[0]):
                    self.currency.data[ctx.message.raw_mentions[0]]['rank'] = ranks[position-1]
                    self.currency.save()
                    break
                else:
                    self.currency.data[ctx.message.raw_mentions[0]]['rank'] = ranks[position]
                    self.currency.save()
                    break

        user_rank = self.currency.data.get(ctx.message.raw_mentions[0]).get('rank')
        mention_roles = ctx.message.server.get_member(ctx.message.raw_mentions[0])
        if not user_rank:
            role_oject = discord.utils.get(ctx.message.server.roles, name=ranks[0])
            await self.bot.add_roles(mention_roles, role_oject)

        if user_rank:
            role_oject = discord.utils.get(ctx.message.server.roles, name=user_rank)
            await self.bot.replace_roles(mention_roles, role_oject)

        mention_user = ctx.message.server.get_member(ctx.message.raw_mentions[0])
        await self.bot.say(f'{mention_user.mention}\'s karma has been updated, thank you.')

    @checks.is_admin()
    @commands.command(pass_context=True, aliases=['arr'])
    async def addrolerank(self, ctx, value: str=None, role: discord.Role = None):
        ''': add role and value to a rank !arr number role (as spelled in roles, case sensitive)'''
        if not value or not value.isdigit() or not role:
            await self.bot.say('Not the correct format, try !help addrolerank')
            return

        if role in ctx.message.server.roles:
            self.currency.data['ranks'][role.name] = int(value)
            self.currency.save()
            await self.bot.say(f'{role.name} added to ranks list.')

        ranks = self.currency.data.get('ranks')
        sortroles = sorted(ranks, key=lambda x: ranks[x], reverse=False)
        sorted_dict = {}
        for rank in sortroles:
            value = self.currency.data.get('ranks').get(rank)
            sorted_dict.update(({f'{rank}': value}))
        self.currency.data['ranks'] = sorted_dict
        self.currency.save()

    @commands.command(pass_context=True, aliases=['rr'])
    async def roleranks(self, ctx):
        ''': list all roles/values for rank.'''
        roles = ''
        value = ''
        embed = discord.Embed(colour=discord.Colour(0x278d89))
        for role in self.currency.data.get('ranks'):
            roles += f'{role} \n'
            value += f"{self.currency.data.get('ranks').get(role)} \n"
        if roles:
            embed.add_field(name='role', value=roles)
            embed.add_field(name='value', value=value)
            await self.bot.say(embed=embed)
            return
        else:
            await self.bot.say('Nothing to show.')


def setup(bot):
    bot.add_cog(Karma(bot))
