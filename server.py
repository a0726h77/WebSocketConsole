import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.gen
from tornado.options import define, options
import os
import time
import multiprocessing
import serialworker
import json
 
define("port", default=8080, help="run on the given port", type=int)
 
clients = [] 

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
	        (r"/static/(.*)", tornado.web.StaticFileHandler, {'path':  './'}),
	        (r"/ws", WebSocketHandler)
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