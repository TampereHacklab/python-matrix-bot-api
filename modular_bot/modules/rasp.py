from matrix_bot_api.matrix_bot_api import MatrixBotAPI
import urllib.request

class MatrixModule:
    def matrix_callback(self, bot, room, event):
        args = event['content']['body'].split()
        day = 0
        hour = 12
        if len(args) >= 2:
            day = int(args[1]) - 1
        if len(args) == 3:
            hour = int(args[2])

        imgurl = 'http://ennuste.ilmailuliitto.fi/' + str(day) + '/wstar_bsratio.curr.' + str(hour) + '00lst.d2.png'
        print("URL:", imgurl, day, hour)
        urllib.request.urlretrieve(imgurl, '/tmp/rasp.png')
        mxc = bot.client.upload(open('/tmp/rasp.png', "rb").read(), 'image/png')
        room.send_image(mxc, 'RASP_paiva_' + str(day+1) + '_klo_' + str(hour) + '00.png')

    def help(self):
        return('Rasp-ennuste. Käyttö: !rasp [päivä] [kello], jossa päivä 1 on tämä päivä, 2 huominen jne. Kellonaika tunteina, esim 14.')
