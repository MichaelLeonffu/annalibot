# AnnaLiBot
Anna Li <3

A discord bot to help a developer.
Maybe after prototyping here I'll build out one of her features onto a dedicate bot.

## Features

annalibot is feature rich, each cog contains multiple features.

Use: `annali help` in discord for a list of commands.

cogs:
- kakTracker: *Helps manage waifus and track kakera for the popular Mudae discord bot.*
- short: *Link shortener service, utilizes [cookieandrock.dev](cookieandrock.dev) web service.*

[List of all features.](./FEATURES.md)

## Installing

Installing annalibot requires that you have populated the config file and remove the `template` from the name of the file. Information includes discord bot api key as well as mongodb information.

### Python

**It's highly recommended to use a [virtual environment](https://docs.python.org/3/library/venv.html) before continuing.**

Use the [pip freeze](https://pip.pypa.io/en/stable/reference/pip_freeze/) python module to download all required packages.

    pip3 install -r requirements.txt

## Running

Running annalibot with a simple command:

    python3 -B annapythonli.py

If you want her to reboot after running `annali close` command then run with:

    python3 -B annali_marathon.py

If you want logging and persistance after logging off:

    nohup python -B annapythonli.py >> /path/to/log/file.log 2>> /path/to/log/file.err.log &

example:

    nohup python -B annapythonli.py >> ../log/annapythonli.log 2>> ../log/annapythonli.err.log &

**Replace the paths with proper paths to your log dirs.**

## Maintenance/DevOps

To keep annalibot up-to-date is easy to do even from discord!

- `annali pull` Performs a git pull
- `annali reload` Reloads all cogs (do this after a pull)
- `annali close` Closes the `annapythonli.py` instance (run with marathon for automatic reboot)
- `annali xload` Runtime cog controller
- `annali free` Checks memory on machine (only for linux)
- `annali press` Sets presence

## Development

Developing on annalibot is easy!

    source ../venv/bin/activate; python -B annapythonli.py >> ../log/annapythonli.log 2>> ../log/annapythonli.err.log

### Setting up stack (WIP)

Make sure to get a working mongodb instance running always. annalibot uses this to save data.

### Development method

(Working on getting unit tests...) But for testing on the fly I do:
0. Change config to have differet bot prefix (`$`) and set `DEV_MODE=True`
0. Make change and save file
0. If it is not changing config/annapythonli.py then in discord type `&reload`
0. Test changes made

This is much faster than rebooting annalibot since reloading cogs takes very little effort
