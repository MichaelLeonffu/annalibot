# annapythonli.py

# Config
import config.config as config
# This is the discord
import discord
from discord.ext import commands
# Time
import time
# asyncio
import asyncio

# The bot
bot = commands.Bot(
    command_prefix  = (config.PREFIX*2, config.PREFIX) + config.PREFIXES,
    case_insensitive= True,
    intents         = discord.Intents.all()
    # intents         = discord.Intents(members=True)
)

# When the bot connects to discord
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

# Admin check
def is_admin(ctx):
    return ctx.message.author.id == config.ADMIN_ID

# Reloading exentions (cogs and listeners)
@bot.command(
    name="reload",
    hidden=True
)
@commands.check(is_admin)
async def _reload(ctx):
    confirmation = await ctx.send("Reloading")

    try:
        for cog in config.COGS_LIST:
            await bot.reload_extension(cog)
    except Exception as err:
        return await confirmation.edit(content="Failed! " + str(err))

    await confirmation.edit(content="Done!")

# (Un)Load exentions (cogs and listeners)
@bot.command(
    name="xload",
    hidden=True
)
@commands.check(is_admin)
async def _xload(ctx, xload, ext):
    confirmation = await ctx.send("Reloading")

    if xload == "load":
        await bot.load_extension(ext)
    elif xload == "unload":
        await bot.unload_extension(ext)
    elif xload == "reload":
        await bot.reload_extension(ext)
    elif xload == "list":
        await confirmation.edit(content="`{}`".format("\n".join([cog for cog in bot.cogs])))
        return
    else:
        await confirmation.edit(content="`xload ([,un,re]load) cogs.name`")
        raise ValueError("Bad ([,un,re]load)")

    await confirmation.edit(content="Done!")

# Close
@bot.command(
    name="close",
    hidden=True
)
@commands.check(is_admin)
async def _close(ctx):
    await ctx.send("Closing... 😢")
    await bot.close()

@_reload.error
@_xload.error
@_close.error
async def _admin_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("B-Baka!!! ><")
    elif isinstance(error, ValueError):
        print(error)
    else:
        await ctx.send(error)


# Keep track of time
time_start = time.time()

@bot.command(
    name='time',
    aliases=['t'],
    brief='How long Anna Li has been running',
    description='The amount of time hr:min:sec Anna Li has been running',
    help='(More like the amount of time Anna Li bot has not been updated',
    usage='%time')
async def _time(ctx):
    await ctx.send(time_pretty(time.time() - time_start))

def time_pretty(dTime):
    hours, remainder = divmod(dTime, 3600)
    minutes, seconds = divmod(remainder, 60)
    return '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))


async def main():
    async with bot:

        # load all the cogs
        for cog in config.COGS_LIST:
            await bot.load_extension(cog)
            # Add a try catch to this later sometime?

        # Connect the client to discord
        await bot.start(config.DISCORD_TOKEN, reconnect=True)

# Start the bot
if __name__ == '__main__':

    asyncio.run(main())


# # HELP

# # Remove the default help (here by default)
# bot.remove_command('help')

# # Add custom help command