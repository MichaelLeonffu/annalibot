# misc.py

# Just some random commands (loose ends)


# This is the discord
import discord
from discord.ext import commands
# Time
import time
# Context
import contextvars as ctxvar


# Our simple cog
class MiscCog(commands.Cog, name="Misc Commands"):
	"""MiscCog"""

	# Allows us to have bot defined and passed in
	def __init__(self, bot):
		self.bot = bot

		# Time keeping
		self.time_start_var = ctxvar.ContextVar('time_start')
		self.time_start_var.set(time.time())


	@commands.command(
		name='add',
		aliases=['a'],
		brief='Adds two numbers',
		description='So I\' hear that you wana add two numbers ;)',
		help='Well, with the `add` command you can do just that!',
		usage='%add(int a, int b)')
	async def _add(self, ctx, a: int, b: int):
		await ctx.send(a + b)

	@_add.error
	async def _add_error(self, ctx, error):
		if isinstance(error, commands.BadArgument):
			await ctx.send(error)


	@commands.command(
		name='mul',
		aliases=['m'],
		brief='Mulitplies two numbers',
		description='So I\' hear that you wana multiply two numbers ;)',
		help='Well, with the `mul` command you can do just that!',
		usage='%mul(int a, int b)')
	async def _mul(self, ctx, a: int, b: int):
		await ctx.send(a * b)

	@_mul.error
	async def _mul_error(self, ctx, error):
		if isinstance(error, commands.BadArgument):
			await ctx.send(error)


	@commands.command(
		name='time',
		aliases=['t'],
		brief='How long Anna Li has been running',
		description='The amount of time hr:min:sec Anna Li has been running',
		help='(More like the amount of time Anna Li bot has not been updated',
		usage='%time')
	async def _time(self, ctx):
		await ctx.send(time_pretty(time.time() - self.time_start_var.get()))


def time_pretty(dTime):
	hours, remainder = divmod(dTime, 3600)
	minutes, seconds = divmod(remainder, 60)
	return '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))



# Give the cog to the bot
def setup(bot):
	bot.add_cog(MiscCog(bot))