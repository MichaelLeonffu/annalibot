# cat_dev.py

# cat development features


# Config
import config.config as config
# This is the discord
import discord
from discord.ext import commands
# mongodb
import pymongo
# os
import os
# paint
import paint
# io
import io


# Dev check
def is_dev_channel(ctx):
	return ctx.message.channel.id in [774738478936096828, 778784714310942751]

img_dir = "./images/"
	

# Our cat cog
class CatUpdateCog(commands.Cog, name="Cat_Update"):
	"""CatCog"""

	# Allows us to have bot defined and passed in
	def __init__(self, bot):
		self.bot = bot

		# Connect the mongodb client
		self.client = pymongo.MongoClient(config.DB_URI)
		self.db = self.client.cat


	@commands.check(is_dev_channel)
	@commands.command(
		name='upload_cat',
		aliases=['uc'],
		hidden=True,
		brief='Dev',
		description='Dev',
		help='Dev')
	async def _upload_cat(self, ctx, cat_part, cat_name):

		# Validate inputs
		# Cat part setting
		cat_part = str(cat_part).lower()
		valid_parts = ["head", "body", "tail"]
		if cat_part not in valid_parts:
			raise ValueError(cat_part + " is not in " + " ".join(valid_parts))

		# Name length limit
		if len(cat_name) > 32:
			raise ValueError("Cat name too long! " + str(cat_name) + ">32")

		# Read in the file attachment
		if len(ctx.message.attachments) != 1:
			raise ValueError("Wrong number of files: " + str(len(ctx.message.attachments)) + " != 1")

		# Find the attachment
		attachment = ctx.message.attachments[0]

		# Check if attachment is bigger than 1MB
		if int(attachment.size) > 1048576:
			raise ValueError("Cat file is too big: " + str(int(attachment.size)) + ">1MB")

		# Filename and location
		filename = cat_name + ".png"
		path = img_dir + cat_part + "/" + filename

		# # Filename must be same as the arguments
		# if filename != attachment.filename:
		# 	raise ValueError("Filename mismatch: " + filename + " != " + attachment.filename)

		# Check if file exsists already
		if os.path.exists(path):
			raise ValueError("File exsists already! try a different name or remove the file")

		# Quick file check
		cat_bytes = await attachment.read()
		cat_bytes = io.BytesIO(cat_bytes)
		result = paint.has_align_pixel(cat_bytes, cat_part)
		if result != True:
			return await ctx.send("⚠️Failed pixel check: " + result)

		# Save the ct
		file = await attachment.save(path)

		# Tell user cat was saved
		await ctx.send("File uploaded: **{}**".format(filename))

	@commands.check(is_dev_channel)
	@commands.command(
		name='compile_cat',
		aliases=['cc'],
		hidden=True,
		brief='Dev',
		description='Dev',
		help='Dev')
	async def _compile_cat(self, ctx, cat_head_name, cat_body_name=None, cat_tail_name=None, bg_hex="f0aaf0"):

		# If only one name is given then make all names that name
		if cat_body_name == None:
			cat_body_name = cat_head_name

		if cat_tail_name == None:
			cat_tail_name = cat_head_name

		# Convert from hex to rgb if possible
		bg_hex = bg_hex.lstrip('#')
		bg_rgb = tuple(int(bg_hex[i:i+2], 16) for i in (0, 2, 4))

		im_dir = "./images/"

		# Validate inputs
		cat_head_file = im_dir + "head/" + cat_head_name + ".png"
		cat_body_file = im_dir + "body/" + cat_body_name + ".png"
		cat_tail_file = im_dir + "tail/" + cat_tail_name + ".png"

		# Name the cat
		cat_name = cat_head_name + "-" + cat_body_name + "-" + cat_tail_name

		# Draw the cat
		im_cat = paint.compile_cat(cat_head_file, cat_body_file, cat_tail_file, bg_rgb)

		# Temp file to save cat
		cat_bytes = io.BytesIO()
		im_cat.save(cat_bytes, format="png")

		# Reset the read back to the start so that discord file can read it
		cat_bytes.seek(0)

		# Make the discord file object
		discord_file = discord.File(cat_bytes, filename=cat_name + ".png")

		# Make the file object to upload to discord
		await ctx.send("compiled cat: " + cat_name, file=discord_file)

		# Remove the buffer
		cat_bytes.close()


	@commands.check(is_dev_channel)
	@commands.command(
		name='cat_bin',
		aliases=['cb'],
		hidden=True,
		brief='Dev',
		description='Dev',
		help='Dev')
	async def _cat_bin(self, ctx, cat_part):

		# Cat part setting
		cat_part = str(cat_part).lower()
		valid_parts = ["head", "body", "tail"]
		if cat_part not in valid_parts:
			raise ValueError(cat_part + " is not in " + " ".join(valid_parts))

		# Check if file exsists already
		cat_parts = ""
		for file in os.listdir(img_dir + cat_part):
			if file[-4:] == ".png":
				cat_parts += file[:-4] + "\n"

		# Output to the user
		await ctx.send("Cats in the **{}** bin:\n{}".format(cat_part, cat_parts))

	@commands.check(is_dev_channel)
	@commands.command(
		name='cat_retrieval',
		aliases=['cr'],
		hidden=True,
		brief='Dev',
		description='Dev',
		help='Dev')
	async def _cat_retrieval(self, ctx, cat_part, cat_name):

		# Validate inputs
		# Cat part setting
		cat_part = str(cat_part).lower()
		valid_parts = ["head", "body", "tail"]
		if cat_part not in valid_parts:
			raise ValueError(cat_part + " is not in " + " ".join(valid_parts))

		# Name length limit
		if len(cat_name) > 32:
			raise ValueError("Cat name too long! " + str(cat_name) + ">32")

		# Filename and location
		filename = cat_name + ".png"
		path = img_dir + cat_part + "/" + filename

		# Check if file exsists already
		if not os.path.exists(path):
			raise ValueError("File does not exist! Try a different name/check bin")

		# Open file for reading
		im_cat_part = open(path, 'rb')

		# Make the discord file object
		discord_file = discord.File(im_cat_part)

		# Make the file object to upload to discord
		await ctx.send("Cat part: " + cat_name, file=discord_file)

		# Close the file
		im_cat_part.close()

	@commands.check(is_dev_channel)
	@commands.command(
		name='cat_remove',
		aliases=['crm'],
		hidden=True,
		brief='Dev',
		description='Dev',
		help='Dev')
	async def _cat_remove(self, ctx, cat_part, cat_name):

		# Validate inputs
		# Cat part setting
		cat_part = str(cat_part).lower()
		valid_parts = ["head", "body", "tail"]
		if cat_part not in valid_parts:
			raise ValueError(cat_part + " is not in " + " ".join(valid_parts))

		# Name length limit
		if len(cat_name) > 32:
			raise ValueError("Cat name too long! " + str(cat_name) + ">32")

		# Filename and location
		filename = cat_name + ".png"
		path = img_dir + cat_part + "/" + filename

		# Check if file exsists already
		if not os.path.exists(path):
			raise ValueError("File does not exist! Try a different name/check bin")

		# Delete cat file
		os.remove(path)

		# Make the file object to upload to discord
		await ctx.send("⚠️ Cat part removed: **{}**".format(cat_name))

	@_upload_cat.error
	@_compile_cat.error
	@_cat_bin.error
	@_cat_retrieval.error
	@_cat_remove.error
	async def _any_error(self, ctx, error):
		await ctx.send('⚠️' + str(error))



# Give the cog to the bot
def setup(bot):
	bot.add_cog(CatUpdateCog(bot))