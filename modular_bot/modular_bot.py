"""
A super simple modular bot using the Python Matrix Bot API

Test it out by adding it to a group chat and say:
!echo this is a test!

Modules for the bot must contain class MatrixModule
which must contain function matrix_callback(self, bot, room, event)
Nothing else is needed!

See echo.py for example.

For modules needing lifecycle management, you can have optional 
matrix_start(self, bot) and matrix_stop(self, bot) functions.

See uptime.py for example.

Run the bot like this, from modular_bot directory:

MATRIX_USERNAME="@username:matrix.org" MATRIX_PASSWORD="password" MATRIX_SERVER="https://matrix.org" PYTHONPATH=.. python3 modular_bot.py

All commands can be listed with !help command.
"""

import random
import importlib
import sys
import traceback
import re
import os
import glob
import signal
import time
from matrix_bot_api.matrix_bot_api import MatrixBotAPI
from matrix_bot_api.mregex_handler import MRegexHandler
from matrix_bot_api.mcommand_handler import MCommandHandler

# Bot has to be a global, as currently it's not accessible in 
# callbacks otherwise. 
bot = None

# Stop bot on ctrl-c
def signal_handler(sig, frame):
    bot.running = False

def modular_callback(room, event):
    global bot

    # Figure out the command
    command = event['content']['body'].split().pop(0)

    # Strip away non-alphanumeric characters, including leading ! for security
    command = re.sub(r'\W+', '', command)

    moduleobject = bot.modules.get(command)

    if not moduleobject:
        room.send_text(event['sender'] + ', unknown command ' + command)
    else:
        try:
            moduleobject.matrix_callback(bot, room, event)
        except:
            room.send_text(event['sender'] + ', plugin for command ' + command + ' caused an exception: ' + str(sys.exc_info()[0]))
            traceback.print_exc(file=sys.stderr)

def load_module(modulename):
    module = importlib.import_module('modules.' + modulename)
    cls = getattr(module, 'MatrixModule')
    return cls()

def main():
    global bot

    modulefiles = glob.glob('./modules/*.py')

    # Create an instance of the MatrixBotAPI
    bot = MatrixBotAPI(os.environ['MATRIX_USERNAME'], os.environ['MATRIX_PASSWORD'], os.environ['MATRIX_SERVER'])

    # Add a handler waiting for any command
    modular_handler = MCommandHandler("", modular_callback)
    bot.add_handler(modular_handler)

    modules = dict()
    for modulefile in modulefiles:
        modulename = os.path.splitext(os.path.basename(modulefile))[0]
        moduleobject = load_module(modulename)
        modules[modulename] = moduleobject

    # Store modules in bot to be accessible from other modules
    bot.modules = modules

    # Call matrix_start on each module
    for modulename, moduleobject in modules.items():
        try:
            moduleobject.matrix_start(bot)
        except AttributeError:
            pass

    # Start polling
    bot.start_polling()

    bot.running = True
    signal.signal(signal.SIGINT, signal_handler)
    print('Bot running, press Ctrl-C to quit..')
    # Wait until ctrl-c is pressed
    while bot.running:
        time.sleep(0.3)

    # Call matrix_stop on each module
    for modulename, moduleobject in modules.items():
        try:
            moduleobject.matrix_stop(bot)
        except AttributeError:
            pass


if __name__ == "__main__":
    main()
