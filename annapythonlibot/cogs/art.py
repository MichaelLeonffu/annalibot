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
					'bin': 			album
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

		time_start = time.time()

		# The main structure which contains all the pics
		html_template = """ <!DOCTYPE html>
		<html>
			<head>
				<style>
					* {{box-sizing: border-box;}}

					.container {{
						position: relative;
						/*width: 50%;*/
						max-width: 225px;
					}}

					.image {{
						display: block;
						width: 100%;
						height: auto;
					}}

					.overlay {{
						position: absolute; 
						bottom: 0; 
						background: rgb(0, 0, 0);
						background: rgba(0, 0, 0, 0.5); /* Black see-through */
						color: #f1f1f1; 
						width: 100%;
						transition: .5s ease;
						opacity:0;
						color: white;
						font-size: 20px;
						padding: 20px;
						text-align: center;
					}}

					.container:hover .overlay {{
						opacity: 1;
					}}

					div {{
						float: left;
						width: 50%;
						height: 25%;
					}}
				</style>
				<title>Arts!</title>
			</head>
			<body>

				<h1>{0}'s Arts</h1>
				<!-- <p>This is a paragraph.</p> -->

				{1}

			</body>
		</html> """


		# Do a basic search
		arts = self.db.art_bin.find({'owner': int(user.id)})[:limit]

		# Fits in the template
		pic_html_template = '<img src="{0}" alt="{1}" style="width:225px;height:350px;">'
		pic_html_template = '<img src="{0}" alt="{1}">'


		# pic_html_template = """
		# <div class="container">
		# 	<img src="{0}" alt="{1}" style="width:225px;height:350px;" class="image">
		# 	<div class="overlay">{1} #{2}</div>
		# </div>
		# """

		# List of all the populated pic html templates
		pics_html = [pic_html_template.format(art['url'], art['bin']) for art  in arts]
		# pics_html = [pic_html_template.format(waifu['pic'], waifu['_id'], waifu['likes']) for waifu in waifu_order]

		# Join all the pics together and then place it in the main template
		html_file = html_template.format(user.name, "".join(pics_html))

		# Convert the string into bytes so it can be made into a file
		html_bytes = bytes(html_file, 'utf8')

		# From bytes we need to get it into a file like object using io.BytesIO
		html_buffer = io.BytesIO()
		html_buffer.write(html_bytes)

		# Reset the reading to the start
		html_buffer.seek(0)

		# Report the time it took to compute this
		time_end = time.time()
		compute_time = "Time: " + str(round(time_end - time_start, 2)) + "s"

		# Completed
		return await ctx.send("Done, " + compute_time, file=discord.File(html_buffer, filename=user.name+'_arts.html'))


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
