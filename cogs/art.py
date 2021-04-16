# art.py

# art gallery


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
# io
import io
# aiohttp
import aiohttp


def utc_to_local(utc_dt):
	return utc_dt.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)

# Our art cog
class ArtCog(commands.Cog, name="Art"):
	"""ArtCog"""

	# Allows us to have bot defined and passed in
	def __init__(self, bot):
		self.bot = bot

		# Connect the mongodb client
		self.client = pymongo.MongoClient(config.DB_URI)
		self.db = self.client.art


	@commands.command(
		name='art_reply_upload',
		aliases=['aru'],
		brief='Upload your art using a reply!',
		description='Then we can see all the art together',
		help='Reply to a message that has art and use "annali aru"')
	async def _art_reply_upload(self, ctx):

		album = "bin"

		# If album is too long or empty then it's wrong
		if len(album) == 0 or len(album) > 16:
			return await ctx.send("⚠️ Album length is bad size: 1-16 inclusive, but given: ", len(album))

		# Should have a reply
		if ctx.message.reference is None:
			return await ctx.send("⚠️ No reply found!")

		async def convert_to_message(mess_id):
			# Convert mess_id to message
			mes = await commands.MessageConverter().convert(ctx, str(mess_id))

			# Read in the file attachment
			if len(mes.attachments) < 1:
				raise ValueError("Wrong number of files: " + str(len(mes.attachments)) + " < 1")

			return mes

		messages = [await convert_to_message(ctx.message.reference.message_id)]

		# aiohttp
		async with aiohttp.ClientSession() as session:
			for message in messages:
				for attachment in message.attachments:

					data = aiohttp.FormData(
						{
							'album': album,
							'discord_id': str(message.author.id),
							'art_url': attachment.url,
							'datetime': message.created_at
						}
					)

					async with session.post('http://localhost:1337/arts', data=data) as res:

						# Check upload result
						if str(res.status) == "200":
							#TODO include link to art
							await ctx.send("✅ 1 Art uploaded!!! Check it out at cookieandrock.dev/art")
						else:
							await ctx.send(res.status)
							await ctx.send(await res.text())


	@commands.command(
		name='art_upload',
		aliases=['au'],
		brief='Upload your art!',
		description='Then we can see all the art together',
		help='Provide the message id, you cannot delete the message otherwise the art will be lost')
	async def _art_upload(self, ctx, *messages_id):

		album = "bin"

		# If album is too long or empty then it's wrong
		if len(album) == 0 or len(album) > 16:
			return await ctx.send("⚠️ Album length is bad size: 1-16 inclusive, but given: ", len(album))

		async def convert_to_message(mess_id):
			# Convert mess_id to message
			mes = await commands.MessageConverter().convert(ctx, mess_id)

			# Read in the file attachment
			if len(mes.attachments) < 1:
				raise ValueError("Wrong number of files: " + str(len(ctx.message.attachments)) + " < 1")

			return mes

		messages = [await convert_to_message(mes) for mes in messages_id]

		# Find the attachment
		# attachments = [attachment.url for attachment in mes.attachments for mes in messages]

		# docs 
		docs = []
		for message in messages:
			for attachment in message.attachments:
				# Prepare doc
				docs.append({
					'owner': 		message.author.id,
					'url': 			attachment.url,
					'bin': 			album,
					'datetime':		message.created_at
				})

		# Upload data to server
		self.db.art_bin.insert_many(docs)
		# await ctx.send(" ".join(attachments))
		# await ctx.send(docs)

		# Check upload result
		await ctx.send("✅ {} Art(s) uploaded!!!".format(len(docs)))


	@commands.command(
		name='art_view',
		aliases=['av'],
		brief='View your art!',
		description='Then we can see all the art together',
		help='Provide the author')
	async def _art_view(self, ctx, author_id=None, album="bin", limit=100):

		album = "bin"

		# If album is too long or empty then it's wrong
		if len(album) == 0 or len(album) > 16:
			return await ctx.send("⚠️ Album length is bad size: 1-16 inclusive, but given: ", len(album))

		# If no argument is given for the author then fill in as the calling user
		if author_id == None:
			user = ctx.message.author
		else:
			user = await commands.UserConverter().convert(ctx, author_id)

		# Search the database for this author
		return await ctx.send("Not ready yet; will send you the link to the art gallery")


	@_art_reply_upload.error
	@_art_upload.error
	@_art_view.error
	async def _any_error(self, ctx, error):
		await ctx.send('⚠️' + str(error))
		# if isinstance(error, commands.BadArgument):
		# 	await ctx.send(error)
		# else:
		# 	print(error)

# Give the cog to the bot
def setup(bot):
	bot.add_cog(ArtCog(bot))
