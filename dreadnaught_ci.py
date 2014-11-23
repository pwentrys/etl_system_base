__author__ = 'Przemyslaw "Blasto" Wentrys'


from app import app
from config.configuration import WEB_IP, WEB_PORT_CI as WEB_PORT


if __name__ == '__main__':
    app.run(host=WEB_IP, port=WEB_PORT, debug=True)