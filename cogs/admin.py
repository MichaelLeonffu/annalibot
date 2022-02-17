# admin.py

# Admin commands and meta commands


# Config
import config.config as config
# This is the discord
import discord
from discord.ext import commands
# Subprocess
import subprocess
# Timeit
import timeit


# Admin check
def is_admin(ctx):
    return ctx.message.author.id == config.ADMIN_ID

def git_pull(result):
    bash = "git pull"
    process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
    result['output'], result['error'] = process.communicate()

def free(result):
    bash = "free -m"
    process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
    result['output'], result['error'] = process.communicate()

# Our Admin cog
class AdminCog(commands.Cog, name="Admin"):
    """AdminCog"""

    # Allows us to have bot defined and passed in
    def __init__(self, bot):
        self.bot = bot

    # Perform a git pull
    @commands.command(
        name="git_pull",
        aliases=['pull'],
        hidden=True
    )
    @commands.check(is_admin)
    async def _git_pull(self, ctx):
        confirmation = await ctx.send("Pulling...")

        result = {'output': '', 'error': ''}

        time = timeit.timeit(lambda: [git_pull(result)], number=1)

        res = result[(['error', 'output'][result['error'] == None])].decode()

        await confirmation.edit(content="```bash\n{}```Done! ({:.4f}s)".format(res, time))

    # Perform free check
    @commands.command(
        name="free",
        # aliases=['free'],
        hidden=True
    )
    @commands.check(is_admin)
    async def _free(self, ctx):
        confirmation = await ctx.send("Free...")

        result = {'output': '', 'error': ''}

        time = timeit.timeit(lambda: [free(result)], number=1)

        res = result[(['error', 'output'][result['error'] == None])].decode()

        await confirmation.edit(content="```bash\n{}```Done! ({:.4f}s)".format(res, time))

    # Change presence
    @commands.command(
        name="presence",
        aliases=['press'],
        hidden=True
    )
    @commands.check(is_admin)
    async def _presence(self, ctx, status_type, activity_type, *names):
        confirmation = await ctx.send("Presence...")

        # Join the input string
        name = ' '.join(names)

        try:
            status_type = int(status_type)
            activity_type = int(activity_type)
            if name == '':
                raise ValueError
        except ValueError:
            await confirmation.edit(content="`anna li presence int int *name`")
            raise ValueError("Empty name")

        # Set activity
        activities = [
            ('Plying', 		discord.Game(name=name)),
            ('Streaming', 	discord.Streaming(name=name, url='https://www.twitch.tv/larypie')),
            ('Listening', 	discord.Activity(type=discord.ActivityType.listening, name=name)),
            ('Watching', 	discord.Activity(type=discord.ActivityType.watching, name=name))
        ]

        # Set status
        statuses = [
            ('online', 		discord.Status.online),
            ('idle', 		discord.Status.idle),
            ('dnd', 		discord.Status.dnd),
            ('invisible', 	discord.Status.invisible),
            ('offline', 	discord.Status.offline)
        ]

        try:
            activity = activities[activity_type]
            status = statuses[status_type]
        except:
            acts = '\n'.join([str(i) + " = " + activities[i][0] for i in range(0, len(activities))])
            stats = '\n'.join([str(i) + " = " + statuses[i][0] for i in range(0, len(statuses))])
            await confirmation.edit(content="```{}```".format(acts+"\n"+stats))
            raise ValueError("Out of bounds presence")

        # Set presence
        await self.bot.change_presence(status=status[1], activity=activity[1])

        await confirmation.edit(content="Presence set to `{}: {} {}`".format(status[0], activity[0], name))

    @_git_pull.error
    @_free.error
    @_presence.error
    async def _admin_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("B-Baka!!! ><")
        elif isinstance(error, ValueError):
            await ctx.send("ValueError" + str(error))
        else:
            await ctx.send(error)

# Delete Message check
async def del_message(ctx):
    if ctx.prefix == config.PREFIX*2:
        await ctx.message.delete(delay=1)
    return True

# Give the cog to the bot
def setup(bot):
    bot.add_cog(AdminCog(bot))
    bot.add_check(del_message, call_once=False)

# Remove the check
def teardown(bot):
    bot.remove_check(del_message, call_once=False)
