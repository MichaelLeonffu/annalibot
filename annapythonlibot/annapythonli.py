# annapythonli.py

# Config
import config.config as config
# This is the discord
import discord
from discord.ext import commands


# The bot
bot = commands.Bot(
	command_prefix	= ('!', '%', 'a!', 'annali!', 'annali'),
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


# Connect the client to discord
bot.run(config.DISCORD_TOKEN, bot=True, reconnect=True)


# # HELP

# # Remove the default help (here by default)
# bot.remove_command('help')

# # Add custom help command


# Pretty print
# import pprint
# Regex
# import re
# Context
import contextvars as ctxvar
# Async
import asyncio