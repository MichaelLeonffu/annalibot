# misc.py

# Just some random commands (loose ends)


# This is the discord
import discord
from discord.ext import commands


# Our simple cog
class MiscCog(commands.Cog, name="Misc Commands"):
	"""MiscCog"""

	# Allows us to have bot defined and passed in
	def __init__(self, bot):
		self.bot = bot


	@commands.command(
		name='add',
		aliases=['a'],
		brief='Adds two numbers',
		description='So I\' hear that you wana add two numbers ;)',
		help='Well, with the `add` command you can do just that!',
		usage='%add(number a, number b)')
	async def _add(self, ctx, a: float, b: float):
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
		usage='%mul(number a, number b)')
	async def _mul(self, ctx, a: float, b: float):
		await ctx.send(a * b)

	@_mul.error
	async def _mul_error(self, ctx, error):
		if isinstance(error, commands.BadArgument):
			await ctx.send(error)



# Give the cog to the bot
def setup(bot):
	bot.add_cog(MiscCog(bot))