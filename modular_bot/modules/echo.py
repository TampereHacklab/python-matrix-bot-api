from matrix_bot_api.matrix_bot_api import MatrixBotAPI

class MatrixModule:
    def matrix_callback(self, bot, room, event):
        args = event['content']['body'].split()
        args.pop(0)

        # Echo what they said back
        room.send_text(' '.join(args))
    def help(self):
        return('Echoes back what user has said')
