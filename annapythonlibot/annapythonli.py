# annapythonli.py

# Config
import config.config as config
# This is the discord
import discord
from discord.ext import commands
# Timeit
import timeit
# Time
import time
# Subprocess
import subprocess


# The bot
bot = commands.Bot(
	command_prefix	= ('%', 'a!', 'annali!', 'annali ', 'annali', 'anna li ', 'anna li'),
	activity		= discord.Game(name="with fire"),
	case_insensitive= True
)

# Cogs
cogs = ['cogs.kakTracker', 'cogs.misc', 'cogs.testing', 'cogs.voice', 'cogs.metrics', 'cogs.waifureader', 'cogs.cat']

# Load the cogs
if __name__ == '__main__':
	for cog in cogs:
		bot.load_extension(cog)

		# Add a try catch to this later sometime?


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

	time = timeit.timeit(lambda: [bot.reload_extension(cog) for cog in cogs], number=1)

	await confirmation.edit(content="Done! ({:.4f}s)".format(time))

def git_pull(result):
	bash = "git pull"
	process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
	result['output'], result['error'] = process.communicate()

# Perform a git pull
@bot.command(
	name="git_pull",
	aliases=['pull'],
	hidden=True
)
@commands.check(is_admin)
async def _git_pull(ctx):
	confirmation = await ctx.send("Pulling")

	result = {'output': '', 'error': ''}

	time = timeit.timeit(lambda: [git_pull(result)], number=1)

	res = result[(['error', 'output'][result['error'] == None])].decode()

	await confirmation.edit(content="```bash\n{}```Done! ({:.4f}s)".format(res, time))

@_reload.error
@_git_pull.error
async def _admin_error(self, ctx, error):
	if isinstance(error, commands.CheckFailure):
		await ctx.send("B-Baka!!! ><")
	else:
		print(error)


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
	global time_start
	await ctx.send(time_pretty(time.time() - time_start))


def time_pretty(dTime):
	hours, remainder = divmod(dTime, 3600)
	minutes, seconds = divmod(remainder, 60)
	return '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))


# Connect the client to discord
bot.run(config.DISCORD_TOKEN, bot=True, reconnect=True)


# # HELP

# # Remove the default help (here by default)
# bot.remove_command('help')

# # Add custom help command