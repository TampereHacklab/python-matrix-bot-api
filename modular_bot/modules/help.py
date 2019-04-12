from matrix_bot_api.matrix_bot_api import MatrixBotAPI

class MatrixModule:
    def matrix_callback(self, bot, room, event):
        msg = 'This is Tampere Hacklab Matrix bot. Known commands:\n\n'
        # Call matrix_stop on each module
        for modulename, moduleobject in bot.modules.items():
            msg = msg + '!' + modulename
            try:
                msg = msg + ' - ' + moduleobject.help() + '\n'
            except AttributeError:
                pass
            msg + msg + '\n'
        msg = msg + "\nAdd your own commands at https://github.com/TampereHacklab/python-matrix-bot-api"
        room.send_text(msg)

    def help(self):
        return('Prints help on commands')
