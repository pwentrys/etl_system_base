__author__ = 'Przemyslaw "Blasto" Wentrys'


from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from app import app
from config.configuration import WEB_PORT_PROD as WEB_PORT, WEB_IP


if __name__ == "__main__":
    http_server = HTTPServer(WSGIContainer(app))
    http_server.bind(WEB_PORT, address=WEB_IP)
    http_server.start(num_processes=5)
    IOLoop.instance().start()