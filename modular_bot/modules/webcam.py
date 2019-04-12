#!/usr/bin/env python3

import subprocess
import os
import urllib.request

class MatrixModule:
    def matrix_callback(self, bot, room, event):
        args = event['content']['body'].split()
        if len(args) == 2:
            preset = int(args[1])
            preset_url = "http://tamperehacklab.tunk.org:38001/nphControlCamera?Direction=Preset&Data=" + str(preset) + "&Resolution=640x480&Quality=Clarity&RPeriod=0&Size=STD&PresetOperation=Move&Language=0&Type=Preset"
            urllib.request.urlopen(preset_url).read()

        filename = "/tmp/snapshot.jpg"
        mjpeg_url = "http://tamperehacklab.tunk.org:38001/nphMotionJpeg?Resolution=640x480&Quality=Clarity"

        subprocess.run(['ffmpeg', '-f', 'MJPEG', '-y', '-i', mjpeg_url, '-r', '1', '-vframes', '1', '-q:v', '1', '/tmp/snapshot.jpg'], check=True, timeout=5)
        mxc = bot.client.upload(open(filename, "rb").read(), 'image/jpeg')
        room.send_image(mxc, 'Tampere Hacklab Webcam')
        os.remove(filename)

    def help(self):
        return('Tampere hacklab webcam. Usage: !webcam [position], where position is number of programmed camera position.')
