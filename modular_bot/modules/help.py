from matrix_bot_api.matrix_bot_api import MatrixBotAPI

class MatrixModule:
    def matrix_callback(self, bot, room, event):
        room.send_text('Known commands: ' + ', '.join(bot.modules.keys()))
