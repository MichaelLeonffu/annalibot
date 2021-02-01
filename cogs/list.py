# list.py

# Keeping a List


# Config
import config.config as config
# This is the discord
import discord
from discord.ext import commands
# Time
import time
import datetime
# mongodb
import pymongo
# pprint
import pprint
# asyncio
import asyncio


def utc_to_local(utc_dt):
	return utc_dt.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)

# Our list cog
class ListCog(commands.Cog, name="List"):
	"""ListCog"""

	# Allows us to have bot defined and passed in
	def __init__(self, bot):
		self.bot = bot

		# Connect the mongodb client
		self.client = pymongo.MongoClient(config.DB_URI)
		self.db = self.client.lists



	async def fetch_user_list(self, user, ctx):

		# Fetch the user data from the db
		user_data = self.db.lists.find_one({
			'_id': {
				'uid': user.id,
				'list': "main"
			}
		})

		# End
		if user_data != None:
			return user_data

		# Some fancy messages
		message = await ctx.send("No data found for you!")
		await asyncio.sleep(1)
		await message.edit(content="Initializing list...")

		# If user is not found then inialize it:
		init_data_doc = {
			'_id': {
				'uid': user.id,
				'list': "main"
			},
			'items': []
		}

		# Attempt to add this user to the database
		insert_result = self.db.lists.insert_one(init_data_doc)

		# Some fancy messages
		await message.edit(content="Done! Welcome to list!")
		await message.delete(delay=2)

		# Fetch the user data from the db
		user_data = self.db.lists.find_one({
			'_id': insert_result.inserted_id
		})

		return user_data


	@commands.command(
		name='list_add',
		aliases=['la'],
		brief='Add to List',
		description='Add an item to your list!',
		help='lol help? anna li list_add make help for list_add')
	async def _list_add(self, ctx, *, item):

		# Validation
		if len(item) < 0 or len(item) > 64:
			return ctx.send("⚠️ Message length must be between 0 and 64!")

		user = ctx.message.author

		# Check for an existing list
		user_data = await self.fetch_user_list(user, ctx)

		query = {
			'_id': {
				'uid': user.id,
				'list': "main"
			}
		}

		# Add the item to their list
		update = {
			"$push": { 'items': item}
		}

		# Update the data
		result = self.db.lists.update_one(query, update)

		await ctx.send("✅ Added item to list!")


	# @_list_add.error
	# async def _list_add_error(self, ctx, error):
	# 	if isinstance(error, commands.BadArgument):
	# 		await ctx.send(error)
	# 	else:
	# 		print(error)


	@commands.command(
		name='list_read',
		aliases=['lr'],
		brief='Read from list',
		description='Read out your list',
		help='lol help? anna li list_add make help for list_add')
	async def _list_read(self, ctx):

		user = ctx.message.author

		# Check for an existing list
		user_data = await self.fetch_user_list(user, ctx)

		query = {
			'_id': {
				'uid': user.id,
				'list': "main"
			}
		}

		# Update the data
		result = self.db.lists.find_one(query)

		# embed it
		embed = discord.Embed(
			title=user.name + "'s " + result['_id']['list'] + " list!",
			# description='description',
			colour=discord.Colour.green()
		)

		# embed.set_image(url='https://cdn.discordapp.com/attachments/618692088137252864/739351037781213204/ffbbff.png')
		# embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/618692088137252864/739352396144312360/bbbbff.png')
		# embed.set_footer(text='footer')
		# embed.set_author(name='Author')
	
		embed.add_field(
			name="Main list:",
			value="\n".join(result['items']),
			inline=False
		)

		await ctx.send(embed=embed)


	# @_list_read.error
	# async def _list_read_error(self, ctx, error):
	# 	if isinstance(error, commands.BadArgument):
	# 		await ctx.send(error)
	# 	else:
	# 		print(error)


# Give the cog to the bot
def setup(bot):
	bot.add_cog(ListCog(bot))