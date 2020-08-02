# annapythonli.py

# Config
import config.config as config
# This is the discord
import discord
from discord.ext import commands
# Pretty print
# import pprint
# Regex
# import re
# Time
import time
# Context
import contextvars as ctxvar
# Async
import asyncio


# Config
CONFIG_var = ctxvar.ContextVar('CONFIG')
CONFIG_var.set(config)


# Time keeping
time_start_var = ctxvar.ContextVar('time_start')
time_start_var.set(time.time())


def time_pretty(dTime):
	hours, remainder = divmod(dTime, 3600)
	minutes, seconds = divmod(remainder, 60)
	return '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))



# The client
# client = discord.Client()
# The bot
bot = commands.Bot(
	command_prefix	= ('!', '%', 'a!', 'annali!', 'annali'),
	activity		= discord.Game(name="with fire")
)

# Commands
@bot.command()
async def test(ctx, *args, hidden=True):
	await ctx.send('{} arguments: {}'.format(len(args), ', '.join(args)))

@bot.command(
	name='time',
	aliases=['t'],
	brief='How long Anna Li has been running',
	description='The amount of time hr:min:sec Anna Li has been running',
	help='(More like the amount of time Anna Li bot has not been updated',
	usage='%time')
async def _time(ctx):
	await ctx.send(time_pretty(time.time() - time_start_var.get()))

@bot.command(
	name='add',
	aliases=['a'],
	brief='Adds two numbers',
	description='So I\' hear that you wana add two numbers ;)',
	help='Well, with the `add` command you can do just that!',
	usage='%add(int a, int b)')
async def _add(ctx, a: int, b: int):
	await ctx.send(a + b)

@_add.error
async def _add_error(ctx, error):
	if isinstance(error, commands.BadArgument):
		await ctx.send(error)

@bot.command(
	name='mul',
	aliases=['m'],
	brief='Mulitplies two numbers',
	description='So I\' hear that you wana multiply two numbers ;)',
	help='Well, with the `mul` command you can do just that!',
	usage='%mul(int a, int b)')
async def _mul(ctx, a: int, b: int):
	await ctx.send(a * b)

@_add.error
async def _add_error(ctx, error):
	if isinstance(error, commands.BadArgument):
		await ctx.send(error)

@bot.command(
	name='embed',
	aliases=['em'],
	brief='Embed testing',
	description='Attempt to make things look pretty',
	help='And colorful',
	usage='%mul(int a, int b)')
async def _embed(ctx):
	embed = discord.Embed(
		title='Title',
		description='description',
		url='https://cdn.discordapp.com/attachments/618692088137252864/739352223619743882/bbffbb.png',
		colour=discord.Colour.red()
	)

	embed.set_image(url='https://cdn.discordapp.com/attachments/618692088137252864/739351037781213204/ffbbff.png')
	embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/618692088137252864/739352396144312360/bbbbff.png')
	embed.set_footer(text='footer')

	embed.set_author(name='Author')
	embed.set_author(name='Author')
	embed.add_field(
		name='field name',
		value='value',
		inline=False
	)
	embed.add_field(
		name='field name2',
		value='value2 inline',
		inline=True
	)
	# await ctx.send()
	await ctx.send(embed=embed)

@bot.command(
	name='file',
	aliases=['f'],
	brief='File testing',
	description='Uploading a file (so that I can use the url later)',
	help='Teehee',
	usage='%file')
async def _file(ctx):

	file = discord.File("images/meowpudding.jpg", filename="meowpudding.jpg", spoiler=False)

	# If the USER_ID in the config is 0 (default) then send
	# the file to the user who sent the message
	user_id = CONFIG_var.get().USER_ID
	if user_id == 0:
		user_id = ctx.message.author.id

	# message = await ctx.channel.send("file: " + str(file), file=file)

	# Begin loophole
	# Find our user (not possible to send message to self, so sending it to defined user)
	user = bot.get_user(user_id)
	# Create dm if there isn't one
	if user.dm_channel == None:
		await user.create_dm()
	# Send a message to this user (ourself)
	message = await user.dm_channel.send("file: " + str(file), file=file)


	embed = discord.Embed(
		title='Meow',
		description='And spagethit',
		# url='show a url in the embed',
		colour=discord.Colour.red()
	)

	embed.set_image(url=message.attachments[0].url)
	embed.set_footer(text='(meow)')
	embed.add_field(
		name='field name',
		value='value',
		inline=False
	)
	await ctx.send(embed=embed)


# Attempting to use othe people emotes
@bot.command(
	name='emote',
	aliases=['emo'],
	brief='Emote testing',
	description='Using custom emotes',
	help=':)',
	usage='%emote')
async def _emote(ctx):

	emojis = CONFIG_var.get().EMOJI

	await ctx.send(" ".join([emo for emo in emojis]))


# @bot.command(name='eval')
# @commands.is_owner()
# async def _eval(ctx, *, code):
# 	"""A bad example of an eval command"""
# 	await ctx.send(eval(code))


# Handles events (functions that take care of events that happen)


@bot.command()
async def pages(ctx):
    contents = ["This is page 1!", "This is page 2!", "This is page 3!", "This is page 4!"]
    pages = 4
    cur_page = 1
    message = await ctx.send(f"Page {cur_page}/{pages}:\n{contents[cur_page-1]}")
    # getting the message object for editing and reacting

    await message.add_reaction("◀️")
    await message.add_reaction("▶️")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
        # This makes sure nobody except the command sender can interact with the "menu"

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60, check=check)
            # waiting for a reaction to be added - times out after x seconds, 60 in this
            # example

            if str(reaction.emoji) == "▶️" and cur_page != pages:
                cur_page += 1
                await message.edit(content=f"Page {cur_page}/{pages}:\n{contents[cur_page-1]}")
                await message.remove_reaction(reaction, user)

            elif str(reaction.emoji) == "◀️" and cur_page > 1:
                cur_page -= 1
                await message.edit(content=f"Page {cur_page}/{pages}:\n{contents[cur_page-1]}")
                await message.remove_reaction(reaction, user)

            else:
                await message.remove_reaction(reaction, user)
                # removes reactions if the user tries to go forward on the last page or
                # backwards on the first page
        except asyncio.TimeoutError:
            await message.delete()
            break
            # ending the loop if user doesn't react after x seconds


# # HELP

# # Remove the default help (here by default)
# bot.remove_command('help')

# # Add custom help command




@bot.event
# When the bot connects to discord
async def on_ready():
	print(f'{bot.user} has connected to Discord!')

# Connect the client to discord
bot.run(config.DISCORD_TOKEN)
