__author__ = 'Przemyslaw "Blasto" Wentrys'

import umysql

from config.configuration import SQL


class MySQL_Connection():
    def __init__(self):
        pass

    def execute_query(self, server_name, query):
        cnn = umysql.Connection()

        server = SQL['MySQL'][server_name]

        try:
            cnn.connect(
                server['ADDRESS'],
                server['PORT'],
                server['USERNAME'],
                server['PASSWORD'],
                server['DATABASE']
            )

            result = cnn.query(query)
            return result
        except Exception as error:
            return error
        finally:
            cnn.close()
