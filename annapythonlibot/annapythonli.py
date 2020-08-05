# annapythonli.py

# Config
import config.config as config
# This is the discord
import discord
from discord.ext import commands
# Timeit
import timeit


# The bot
bot = commands.Bot(
	command_prefix	= ('!', '%', 'a!', 'annali!', 'annali ', 'annali', 'anna li ', 'anna li'),
	activity		= discord.Game(name="with fire")
)

# Cogs
cogs = ['cogs.kakTracker', 'cogs.misc', 'cogs.testing']

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

@_reload.error
async def _reload_error(self, ctx, error):
	if isinstance(error, commands.CheckFailure):
		await ctx.send("B-Baka!!! ><")
	else:
		print(error)


# Connect the client to discord
bot.run(config.DISCORD_TOKEN, bot=True, reconnect=True)


# # HELP

# # Remove the default help (here by default)
# bot.remove_command('help')

# # Add custom help command