# pfp_tracker.py

# Tracks pfp for users to create a timeline view of their pfp.


# Config
import config.config as config
# This is the discord
import discord
from discord.ext import commands
# mongodb
import pymongo
# os
import os
# time
import time
import datetime
# sys
import sys


# Generic safe dir creator
def mkdir_after(prefix, new_dir, verbose=False):
    """
        Makes new_dir after prefix if prefix exists already.

        prefix: string, must be an existing path to a dir
        new_dir: string, appended to prefix
        verbose: bool (False), If True, logs all dir creation

        returns: None if failed, else returns full path

        TODO: make a logging system which can be input into here.

        requires: os, 
    """

    # Check if prefix exists, if not then return None
    if not os.path.isdir(prefix):
        return None

    path = os.path.join(prefix, new_dir)
    # It's ok if the path exists already
    os.makedirs(path, exist_ok=True)
    return path

# Admin check
def is_admin(ctx):
    return ctx.message.author.id == config.ADMIN_ID

# Our pfp_tracker cog
class pfp_tracker_cog(commands.Cog, name="pfp_tracker"):
    """pfp_tracker cog"""

    # Allows us to have bot defined and passed in
    def __init__(self, bot):
        self.bot = bot

        # Connect the mongodb client
        self.client = pymongo.MongoClient(config.DB_URI)
        self.db = self.client.pfp_tracker
        self.dat_pfp = os.path.join(config.DATA_PATH, config.PFP_DATA_PATH)

        # Initialize the dir if it is not there
        if not os.path.isdir(self.dat_pfp):
            self.dat_pfp = mkdir_after(config.DATA_PATH, config.PFP_DATA_PATH)
            if self.dat_pfp is None:
                print("ERRO|{}pfp_tracker|{}".format(
                        time.ctime(),
                        "Could not make dat_pfp path: " + self.dat_pfp),
                    file=sys.stderr)

                # Fatal... Or just disable the cog?
                exit()

    # Helper method
    async def save_pfp(self, user: discord.User):
        """No return"""

        # Get url to the avatar as either webp or gif, gif if animated
        user_avatar_asset = user.avatar_url_as(format=None, static_format='webp', size=4096)

        # TODO: check for insert errors

        doc = {
            'time': datetime.datetime.utcnow(),
            'user': user.id,
        }

        # Upload data to server and get id
        file_name = str(self.db.pfp.insert_one(doc).inserted_id)

        # Check if path is valid
        full_path = mkdir_after(self.dat_pfp, file_name[:2])
        if full_path is None:
            print("ERRO|{}|pfp_tracker|{}".format(time.ctime(), "bad dat_pfp path."), file=sys.stderr)

            # TODO: Fatal? or not
            exit()

        # TODO: make remove the await to make it async?

        # Save avatar
        try:
            byte_count = await user_avatar_asset.save(os.path.join(full_path, file_name))
            print("INFO|{}|pfp_tracker|{}".format(
                time.ctime(),
                "Saved pfp: [{:>7}] {}".format(byte_count, file_name)))
        except Exception as e:
            print("ERRO|{}|pfp_tracker|{}".format(time.ctime(), e), file=sys.stderr)


    @commands.command(
        name='pfp_snapshot',
        aliases=['ps'],
        hidden=True,
        brief='Take a snapshot of all Users pfp',
        description='ADMIN only; expensive operation...',
        help='Add the word "confirm" to actually run the routine')
    @commands.check(is_admin)
    async def _pfp_snapshot(self, ctx, confirm=None):

        # Convert to a bool
        if confirm is None:
            confirm = False
        else:
            confirm = confirm.lower() == "confirm"

        await ctx.send("Total Users: " + str(len(self.bot.users)))

        if not confirm:
            return await ctx.send("**Dry run**. Add \'confirm\' to end of command to do a real run")

        # TODO: Add rate limit and verbose
        # List of all users bot can see
        for user in self.bot.users:
            await self.save_pfp(user)

        return await ctx.send("📷 You took a snapshot of everyone!")


    @_pfp_snapshot.error
    async def _any_error(self, ctx, error):
        await ctx.send('⚠️' + str(error))


    # When a User updates their profile.
    @commands.Cog.listener()
    async def on_user_update(self, before, after):

        # TODO: make it not await?
        await self.save_pfp(after)



# Give the cog to the bot
def setup(bot):
    bot.add_cog(pfp_tracker_cog(bot))
