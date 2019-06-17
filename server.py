import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.gen
from tornado.options import define, options
import os
import io
import time
import multiprocessing
import serialworker
import json
import datetime

from PIL import Image

import pygame.camera
import pygame.image

define("port", default=8080, help="run on the given port", type=int)

clients = []
img_clients = set()

input_queue = multiprocessing.Queue()
output_queue = multiprocessing.Queue()


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

class StaticFileHandler(tornado.web.RequestHandler):
	def get(self):
		self.render('main.js')

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print 'new connection'
        clients.append(self)
        self.write_message("connected")

    def on_message(self, message):
        print 'tornado received from client: %s' % json.dumps(message)
        #self.write_message('ack')
        input_queue.put(message)

    def on_close(self):
        print 'connection closed'
        clients.remove(self)

    def check_origin(self, origin):
        return True


class ImageWebSocketHandler(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):
        # Allow access from every origin
        return True

    def open(self):
        img_clients.add(self)
        print("WebSocket opened from: " + self.request.remote_ip)
        self.write_message("camera connected")

        pygame.camera.init()
        camera_name = pygame.camera.list_cameras()[0]
        self._cam = pygame.camera.Camera(camera_name, (640, 480))
        self._cam.start()

        tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(seconds=1), self.timeout_loop)

    def on_message(self, message):
        print 'tornado received from client: %s' % json.dumps(message)

    def on_close(self):
        img_clients.remove(self)

        print("WebSocket closed from: " + self.request.remote_ip)

        self._cam.stop()

    def timeout_loop(self):
        jpeg_bytes = self.get_jpeg_image_bytes()

        for c in img_clients:
            c.write_message(jpeg_bytes, binary=True)

        tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(seconds=30), self.timeout_loop)

    def get_jpeg_image_bytes(self):
        img = self._cam.get_image()
        imgstr = pygame.image.tostring(img, "RGB", False)
        pimg = Image.frombytes("RGB", img.get_size(), imgstr)
        with io.BytesIO() as bytesIO:
            pimg.save(bytesIO, "JPEG", quality=70, optimize=True)
            return bytesIO.getvalue()


## check the queue for pending messages, and rely that to all connected clients
def checkQueue():
	if not output_queue.empty():
		message = output_queue.get()
		for c in clients:
			c.write_message(message)


if __name__ == '__main__':
	## start the serial worker in background (as a deamon)
	sp = serialworker.SerialProcess(input_queue, output_queue)
	sp.daemon = True
	sp.start()
	tornado.options.parse_command_line()
	app = tornado.web.Application(
	    handlers=[
	        (r"/", IndexHandler),
	        (r"/static/(.*)", tornado.web.StaticFileHandler, {'path':  './static/'}),
	        (r"/ws", WebSocketHandler),
	        (r"/camera", ImageWebSocketHandler)
	    ]
	)
	httpServer = tornado.httpserver.HTTPServer(app)
	httpServer.listen(options.port)
	print "Listening on port:", options.port

	mainLoop = tornado.ioloop.IOLoop.instance()
	## adjust the scheduler_interval according to the frames sent by the serial port
	scheduler_interval = 100
	scheduler = tornado.ioloop.PeriodicCallback(checkQueue, scheduler_interval, io_loop = mainLoop)
	scheduler.start()
	mainLoop.start()
