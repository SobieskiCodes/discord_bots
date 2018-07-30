from discord.ext import commands
import discord
import asyncio
import pyson
config = pyson.Pyson('tasks.json')
tasks = config.data.get('tasklist')
token = 'token'

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
async def task(ctx, task_name: str = None,):
    if task_name is None:
        embed = discord.Embed(title="Task List", colour=discord.Colour(0x278d89))
        task_to_do = ''
        task_status = ''
        assign_list = ''
        for task_item in tasks:
            get_description = tasks.get(task_item).get('todo')
            get_status = tasks.get(task_item).get('status')
            get_assigned = tasks.get(task_item).get('assigned_to')
            if get_status != "closed":
                task_to_do += f'**Task:** {task_item}\n'
                task_status += f'**Status:** {get_status}\n'
                assign_list += f'**Assigned To:** {get_assigned}\n'
            else:
                pass

        embed.add_field(name='Task', value=task_to_do)
        embed.add_field(name='Status', value=task_status)
        embed.add_field(name='Assigned To', value=assign_list)
        await bot.say(embed=embed)
        return

    if task_name:
        if task_name in tasks:
            get_description = tasks.get(task_name).get('todo')
            get_status = tasks.get(task_name).get('status')
            get_assigned = tasks.get(task_name).get('assigned_to')
            await bot.say(f'**Task Name**: {task_name} **Description**: {get_description} '
                          f'**Status**: {get_status} **Assigned to**: {get_assigned}')
            return
        else:
            await bot.say(f"Couldn\'t find task '{task_name}'")
            return


@bot.command(pass_context=True, hidden=True)
async def closed(ctx):
    embed = discord.Embed(title="Closed Task List", colour=discord.Colour(0x278d89))
    task_to_do = ''
    task_status = ''
    assign_list = ''
    for task in tasks:
        get_description = tasks.get(task).get('todo')
        get_status = tasks.get(task).get('status')
        get_assigned = tasks.get(task).get('assigned_to')
        if get_status == "closed":
            task_to_do += f'**Task:** {task}\n'
            task_status += f'**Status:** {get_status}\n'
            assign_list += f'**Assigned To:** {get_assigned}\n'

    embed.add_field(name='Task', value=task_to_do)
    embed.add_field(name='Status', value=task_status)
    embed.add_field(name='Assigned To', value=assign_list)
    await bot.say(embed=embed)
    return


@bot.command(pass_context=True, hidden=True)
async def addtask(ctx, task_name: str = None, task_description: str = None, status: str = None, assigned: str = None):
    if not task_name or not task_description or not status or not assigned:
        await bot.say("Incorrect format, <addtask> <task name> <task description> <status> <assigned>")

    status_choices = ['closed', 'open', 'need more info']
    if status.lower() not in status_choices:
        await bot.say("Valid status is, closed, open, or need more info.")
        return


    if task_name in tasks:
        await bot.say(f"Already a task named '{task_name}' please change the name or remove the old one.")
        return

    new_task = {f"todo": str(task_description), "status": str(status), "assigned_to": str(assigned)}
    config.data['tasklist'][f'{task_name}'] = new_task
    config.save()


@bot.command(pass_context=True, hidden=True)
async def close(ctx, task: str = None):
    if not task:
        await bot.say('No task supplied!')
        return

    if task in tasks:
        get_status = tasks.get(task).get('status')
        config.data['tasklist'][f'{task}'][f'{get_status}'] = "closed"
        config.save()
        await bot.say(f"Closed '{task}'")
    else:
        await bot.say(f"I couldn\'t find task '{task}'")
        return

bot.loop.run_until_complete(connect())
