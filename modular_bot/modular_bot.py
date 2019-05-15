"""
A simple modular bot using the Python Matrix Bot API

Test it out by adding it to a group chat and say:
!echo this is a test!

Modules for the bot must contain class MatrixModule
which must contain function matrix_callback(self, bot, room, event)
Nothing else is needed!

See echo.py for example.

For modules needing lifecycle management, you can have optional 
matrix_start(self, bot) and matrix_stop(self, bot) functions.

See uptime.py for example.

Modules that want to poll stuff can use matrix_poll() function
which is called every 10 seconds.

Run the bot like this, from modular_bot directory:

MATRIX_USERNAME="@username:matrix.org" MATRIX_PASSWORD="password" MATRIX_SERVER="https://matrix.org" PYTHONPATH=.. python3 modular_bot.py

All commands can be listed with !help command.

To simulate bot in console (without matrix user):

SIMULATE=yes PYTHONPATH=.. python3 modular_bot.py

Some things won't work when simulating.
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

class FakeRoom:
    def send_text(self, text):
        print("<bot> " + text)
    def send_image(self, mxc, text):
        print("Image: ", mxc, text)

class FakeClient:
    def upload(self, data, type):
        mxc = "mxc:666"
        print("(Fake uploading ", len(data), " bytes of data, type ", type, " as mxc" + mxc + ")")
        return mxc
    def get_rooms(self):
        return dict()

class FakeBot:
    client = FakeClient()
    running = True

# Stop bot on ctrl-c
def signal_handler(sig, frame):
    bot.running = False

def modular_callback(room, event):
    global bot

    # Figure out the command
    body = event['content']['body']
    if len(body) == 0:
        return
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
    try:
        module = importlib.import_module('modules.' + modulename)
        cls = getattr(module, 'MatrixModule')
        return cls()
    except ModuleNotFoundError:
        print('Module ', modulename, ' failed to load!')
        traceback.print_exc(file=sys.stderr)
        return None

def load_modules():
    modulefiles = glob.glob('./modules/*.py')
    modules = dict()
    for modulefile in modulefiles:
        modulename = os.path.splitext(os.path.basename(modulefile))[0]
        moduleobject = load_module(modulename)
        if moduleobject:
            modules[modulename] = moduleobject
    return modules

def run_bot(modules):
    global bot

    # Create an instance of the MatrixBotAPI
    bot = MatrixBotAPI(os.environ['MATRIX_USERNAME'], os.environ['MATRIX_PASSWORD'], os.environ['MATRIX_SERVER'])

    # Add a handler waiting for any command
    modular_handler = MCommandHandler("", modular_callback)
    bot.add_handler(modular_handler)

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
    pollcount = 0
    while bot.running:
        for modulename, moduleobject in modules.items():
            try:
                moduleobject.matrix_poll(bot, pollcount)
            except AttributeError:
                pass
            except:
                print('Polling module', modulename, 'failed:')
                traceback.print_exc(file=sys.stderr)
        time.sleep(10)
        pollcount = pollcount + 1

    # Call matrix_stop on each module
    for modulename, moduleobject in modules.items():
        try:
            moduleobject.matrix_stop(bot)
        except AttributeError:
            pass

def simulate_bot(modules):
    global bot
    bot =  FakeBot()
    bot.modules = modules
    room = FakeRoom()
    event = dict()
    event['content'] = dict()
    event['sender'] = "@console:matrix.org"
    for modulename, moduleobject in modules.items():
        try:
            moduleobject.matrix_start(bot)
        except AttributeError:
            print('Startup of ', modulename, ' failed')
            traceback.print_exc(file=sys.stderr)
            pass
    line = ''
    print('Simulating bot. Say quit to quit.')
    pollcount = 0
    while(bot.running):
        if(line == 'quit'):
            bot.running = False
        else:
            line = input(" > ")
            event['content']['body'] = line
            modular_callback(room, event)

            for modulename, moduleobject in modules.items():
                try:
                    moduleobject.matrix_poll(bot, pollcount)
                except AttributeError:
                    pass
            pollcount = pollcount + 1

    # Call matrix_stop on each module
    for modulename, moduleobject in modules.items():
        try:
            moduleobject.matrix_stop(bot)
        except AttributeError:
            pass

def main():
    modules = load_modules()

    if(os.getenv("SIMULATE") is None):
        run_bot(modules)
    else:
        simulate_bot(modules)

if __name__ == "__main__":
    main()
