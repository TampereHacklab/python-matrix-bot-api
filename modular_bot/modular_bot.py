"""
A super simple modular bot using the Python Matrix Bot API

Test it out by adding it to a group chat and say:
!echo this is a test!

Modules for the bot must contain class MatrixModule
which must contain function matrix_callback(self, room, event)
Nothing else is needed!

See echo.py for example.

Run the bot like this, from modular_bot directory:

MATRIX_USERNAME="@username:matrix.org" MATRIX_PASSWORD="password" MATRIX_SERVER="https://matrix.org" PYTHONPATH=.. python3 modular_bot.py
"""

import random
import importlib
import sys
import re
import os
from matrix_bot_api.matrix_bot_api import MatrixBotAPI
from matrix_bot_api.mregex_handler import MRegexHandler
from matrix_bot_api.mcommand_handler import MCommandHandler

def modular_callback(room, event):
    # Figure out the command
    command = event['content']['body'].split().pop(0)

    # Strip away non-alphanumeric characters, including leading ! for security
    command = re.sub(r'\W+', '', command)

    # Ignore empty command
    if(len(command) == 0):
        return

    # Try to load matching python file and execute callback in it
    try:
        module = importlib.import_module('modules.' + command)
        cls = getattr(module, 'MatrixModule')
        obj = cls()
        obj.matrix_callback(room, event)
    except ModuleNotFoundError:
        room.send_text(event['sender'] + ', unknown command ' + command)
    except AttributeError:
        room.send_text(event['sender'] + ', plugin for command ' + command + ' failed to load.')
    except:
        room.send_text(event['sender'] + ', plugin for command ' + command + ' caused an exception: ' + sys.exc_info()[0])
        
def main():
    # Create an instance of the MatrixBotAPI
    bot = MatrixBotAPI(os.environ['MATRIX_USERNAME'], os.environ['MATRIX_PASSWORD'], os.environ['MATRIX_SERVER'])

    # Add a handler waiting for any command
    modular_handler = MCommandHandler("", modular_callback)
    bot.add_handler(modular_handler)

    # Start polling
    bot.start_polling()

    # Infinitely read stdin to stall main thread while the bot runs in other threads
    while True:
        input()


if __name__ == "__main__":
    main()
