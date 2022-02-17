# metrics.py

# All commands will go through this global check.


# This is the discord
import discord
from discord.ext import commands


# Global check
def global_check(ctx):
    print(ctx.command)
    return True


# Add the check
def setup(bot):
    bot.add_check(global_check, call_once=False)

# Remove the check
def teardown(bot):
    bot.remove_check(global_check, call_once=False)