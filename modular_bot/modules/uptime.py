from matrix_bot_api.matrix_bot_api import MatrixBotAPI
import time

class MatrixModule:
    def matrix_start(self, bot):
        self.starttime = time.time()

    def matrix_callback(self, bot, room, event):
        room.send_text('Uptime: ' + str(int(time.time() - self.starttime)) + ' seconds.')

    def matrix_stop(self, bot):
        pass

    def help(self):
        return('Tells how many seconds the bot has been up.')
