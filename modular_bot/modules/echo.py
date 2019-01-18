from matrix_bot_api.matrix_bot_api import MatrixBotAPI

class MatrixModule:
    def matrix_callback(self, room, event):
        args = event['content']['body'].split()
        args.pop(0)

        # Echo what they said back
        room.send_text(' '.join(args))
