from discord.ext import commands
import discord
import asyncio
import pyson

config = pyson.Pyson('tasks.json')
tasks = config.data.get('tasklist')
token = 'token'

bot = commands.Bot(command_prefix='!')


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


@bot.command(pass_context=True, aliases=['tl', 'tasklist'])
async def task(ctx, task_name: str = None, ):
    """!task - lists all tasks not closed, if followed by task will give details for said task

    example:
    !task will produce all tasks
    !task "name" will produce info for said task eg; !task "task 11"
    """
    if not tasks:
        await bot.say("It seems there are no tasks added, try !addtask")
        return

    if task_name is None:
        embed = discord.Embed(title="Task List", colour=discord.Colour(0x278d89))
        task_to_do = ''
        task_status = ''
        assign_list = ''
        for task_item in tasks:
            get_status = tasks.get(task_item).get('status')
            get_assigned = tasks.get(task_item).get('assigned_to')
            if get_status != "closed":
                task_to_do += f'**Task:** {task_item}\n'
                task_status += f'**Status:** {get_status}\n'
                assign_list += f'**Assigned To:** {get_assigned}\n'
            else:
                pass

        if not task_to_do:
            await bot.say('No open tasks.')
            return

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


@bot.command(pass_context=True)
async def closed(ctx):
    """!closed - List all closed tasks"""
    embed = discord.Embed(title="Closed Task List", colour=discord.Colour(0x278d89))
    task_to_do = ''
    task_status = ''
    assign_list = ''
    for task in tasks:
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


@bot.command(pass_context=True)
async def addtask(ctx, task_name: str = None, task_description: str = None, assigned: str = None, status="open"):
    """!addtask <taskname> <task description> <assigned> <status>
    All variables need to be wrapped in quotes eg !addtask "task name here" "task description" "status" "assigned to"
    Assigned to needs to be a string, not a mention eg; "probsjustin"
    Assigned is optional
    example:
    !addtask "finish website" "finish the about page" ["probsjustin"]
    """
    if not task_name or not task_description:
        await bot.say("Incorrect format, <addtask> <task name> <task description> [<assigned>] [<status>]")
        return

    if task_name in tasks:
        await bot.say(f"Already a task named '{task_name}' please change the name or remove the old one.")
        return

    new_task = {f"todo": str(task_description), "status": str(status), "assigned_to": str(assigned)}
    config.data['tasklist'][f'{task_name}'] = new_task
    config.save()
    embed = discord.Embed(title="Task Added", description=f"Task: {task_name}\nStatus: {status}\nDescription: "
                                f"{task_description}\n" f"Assigned To: {assigned}\n", colour=discord.Colour(0x278d89))
    await bot.say(embed=embed)

@bot.command(pass_context=True)
async def status(ctx, task: str = None, status: str = None):
    """!status "task" - changes task status."""
    if not task:
        await bot.say('No task supplied!')
        return
    if not status:
        await bot.say('Please provide a status to change to.')
        return

    if task in tasks:
        config.data['tasklist'][f'{task}']['status'] = status
        config.save()
        await bot.say(f"status of '{task}' changed to '{status}'")
    else:
        await bot.say(f"I couldn\'t find task '{task}'")
        return


@bot.command(pass_context=True)
async def close(ctx, task: str = None):
    """!close "task" - closes a task thats not already closed."""
    if not task:
        await bot.say('No task supplied!')
        return

    if task in tasks:
        get_status = tasks.get(task).get('status')
        if get_status == "closed":
            await bot.say(f"'{task}' is already closed.")
            return

        config.data['tasklist'][f'{task}']['status'] = "closed"
        config.save()
        await bot.say(f"Closed '{task}'")
    else:
        await bot.say(f"I couldn\'t find task '{task}'")
        return


bot.loop.run_until_complete(connect())
