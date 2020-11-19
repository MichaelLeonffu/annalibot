# AnnaLiBot
Anna Li <3


## Installing

Installing annalibot requires that you have populated the config file and remove the `template` from the name of the file. Information includes discord bot api key as well as mongodb information.

#### Python

For python use [pip freeze](https://pip.pypa.io/en/stable/reference/pip_freeze/) to download all required libraries/packages

`pip3 install -r requirements.txt`

## Running

Running annalibot with a simple command:

`python3 -B annapythonli.py`

If you want her to reboot after running `annali close` command then run with:

`python3 -B annali_marathon.py`

## Maintenance/DevOps

To keep annalibot up-to-date is easy to do even from discord!

* `annali pull` Performs a git pull
* `annali reload` Reloads all cogs (do this after a pull)
* `annali close` Closes the annapythonli.py instance (run with marathon for automatic reboot)
* `annali xload` Runtime cog controler
* `annali free` Checks memeory on machine (only for linux)
* `annali press` Sets presence

## Development

Developing on annalibot is easy!

### Setting up stack (WIP)

Make sure to get a working mongodb instance running always. annalibot uses this to save data.

### Development method

(Working on getting unit tests...) But for testing on the fly I do:
0. Change config to have differet bot prefix (`$`) and set `DEV_MODE=True`
1. Make change and save file
2. If it is not changing config/annapythonli.py then in discord type `&reload`
3. Test changes made

This is much faster than rebooting annalibot since reloading cogs takes very little effort
