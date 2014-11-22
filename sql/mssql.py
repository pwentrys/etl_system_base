__author__ = 'Przemyslaw "Blasto" Wentrys'


import pyodbc
import pymssql
from config.configuration import SQL


class MSSQL_Connection():
    def __init__(self):
        pass

    def execute_query(self, server, query):
        class final(object):
            pass

        final = final()
        server_name = server
        user = SQL['MSSQL'][server_name]['USERNAME']
        password = SQL['MSSQL'][server_name]['PASSWORD']
        database = SQL['MSSQL'][server_name]['DATABASE']

        conn = pymssql.connect(host=server_name.lower(),
                               user=user,
                               password=password,
                               database='master')
        cur = conn.cursor()

        cur.execute(query)

        result = cur.fetchall()

        final.fields = list([str(i[0])] for i in cur.description)
        final.rows = list([str(y) for y in i] for i in result)

        conn.close()

        return final

    def get_schemas(self, server, query):
        class final(object):
            pass

        final = final()
        final.rows = []
        server_name = server
        user = SQL['MSSQL'][server_name]['USERNAME']
        password = SQL['MSSQL'][server_name]['PASSWORD']
        database = SQL['MSSQL'][server_name]['DATABASE']

        conn = pymssql.connect(host=server_name.lower(),
                               user=user,
                               password=password,
                               database=database)
        cur = conn.cursor()

        cur.execute('select name from sys.databases')

        databases = cur.fetchall()

        conn.close()

        for name in databases:
            conn = pymssql.connect(host=server_name.lower(),
                                   user=user,
                                   password=password,
                                   database=str(name[0]))
            cur = conn.cursor()

            cur.execute(query)

            result = cur.fetchall()

            final.fields = list([str(i[0])] for i in cur.description)
            final.rows += list([str(name[0]), '{0}.{1}'.format(str(i[0]), str(i[1])), str(i[2])] for i in result)
            conn.close()

        return final