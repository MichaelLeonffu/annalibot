# voice.py

# Voice channel realted things


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



# Our voice cog
class VoiceCog(commands.Cog, name="Voice"):
	"""VoiceCog"""

	# Allows us to have bot defined and passed in
	def __init__(self, bot):
		self.bot = bot

		# Connect the mongodb client
		self.client = pymongo.MongoClient(config.DB_URI)
		self.db = self.client.voice



	# Attempt to read voice stats updates
	@commands.Cog.listener()
	async def on_voice_state_update(self, member, before, after):

		# print("member", member)
		# print("before", before)
		# print("after", after)
		return



# Give the cog to the bot
def setup(bot):
	bot.add_cog(VoiceCog(bot))