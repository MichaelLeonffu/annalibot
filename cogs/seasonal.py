# seasonal.py

# Seasonal


# Config
import config.config as config
# This is the discord
import discord
from discord.ext import commands
# Regex
import re
# Time
import time
import datetime
# mongodb
import pymongo
# pprint
import pprint
# random
import random
# AsyncIo
import asyncio

def utc_to_local(utc_dt):
	return utc_dt.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)

# Our seasonal cog
class SeasonalCog(commands.Cog, name="Seasonal"):
	"""SeasonalCog"""

	SEASONAL_REACT_RATE = 0.1

	# Allows us to have bot defined and passed in
	def __init__(self, bot):
		self.bot = bot

		# Connect the mongodb client
		self.client = pymongo.MongoClient(config.DB_URI)
		self.db = self.client.kakera

		# Get seasonal emotes ready
		self.SEASONAL_EMOTES = config.EMOJI_SEASONAL

	# Attempt to read emotes for tracking rolls
	@commands.Cog.listener()
	async def on_message(self, message):

		# If a non-bot message
		if message.author.bot == True:
			return

		date = datetime.datetime.now()

		# Halloween!
		if date.strftime("%d/%m") == "31/10"\
			and random.random() < SEASONAL_REACT_RATE:
			await message.add_reaction(random.choice(['👻', '🎃', '🍬', '🍭']))
			
		# Thanksgiving! On the 4th thrusday of november meaning thrusday on 22-28 inclusive
		if date.strftime("%a/%m") == "Thu/11"\
			and int(date.strftime("%d")) in range(22,29)\
			and random.random() < SEASONAL_REACT_RATE:
			await message.add_reaction(random.choice(['🦃', '🍂', '🌽', '🥖']))

		# Christmas!
		if date.strftime("%d/%m") == "25/12"\
			and random.random() < SEASONAL_REACT_RATE:
			await message.add_reaction(random.choice(['❄️', '⛄', '☃️', '🎅', '🎁', '🎄']))

		# New years!
		if date.strftime("%d/%m") == "01/01"\
			and random.random() < SEASONAL_REACT_RATE:
			await message.add_reaction(random.choice(['🍺', '🍻', '🥂🍷', '🥃', '🍸', '🍾', '🎊', '🎉', '🎆']))

		# On random chance add the emote
		if random.random() < 0.0025:
			await message.add_reaction(random.choice(self.SEASONAL_EMOTES))

			# Should remove the react after some time

	# When the bot notices a reaction to a message
	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):

		# If a non-bot message
		if reaction.message.author.bot == True:
			return

		# If it isn't our emote
		if str(reaction) not in self.SEASONAL_EMOTES:
			return

		# Remove the reactions if there are 2 or more of our reactions on it
		if reaction.count == 2:

			# Find the reacter
			users = await reaction.users().flatten()

			await reaction.clear()

			congrats = await reaction.message.channel.send("Congrats! +1pt " + str(users[1]))
			await asyncio.sleep(1)
			await congrats.edit(content="Don't tell anyone!")
			await congrats.delete(delay=1)


# Give the cog to the bot
def setup(bot):
	bot.add_cog(SeasonalCog(bot))