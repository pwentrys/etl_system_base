__author__ = 'Przemyslaw "Blasto" Wentrys'


import pymssql
from config.configuration import SQL
from helpers.simplifiers.functions import Simplify


class MSSQL_Connection():
    def __init__(self):
        pass

    def fetch_all_return(self, server_name, query):
        """
        Run fetchall query.
        :param server_name:
        :param query:
        :return:
        """

        server = SQL['MSSQL'][server_name]

        #Ensure return is an object
        try:
            conn = pymssql.connect(host=server_name.lower(),
                                   user=server['USERNAME'],
                                   password=server['PASSWORD'],
                                   database=server['DATABASE'])
            cur = conn.cursor()
            cur.execute(query)

            result = cur.fetchall()

        except:
            result = [['ERROR']]

        finally:
            Simplify().try_pass(conn.close())
            return result

    def execute_query(self, server_name, query):
        """
        Run normal query.
        :param server_name:
        :param query:
        :return:
        """

        server = SQL['MSSQL'][server_name]

        #Ensure return is an object
        class Final(object):
            pass

        final = Final()

        try:
            conn = pymssql.connect(host=server_name.lower(),
                                   user=server['USERNAME'],
                                   password=server['PASSWORD'],
                                   database=server['DATABASE'])
            cur = conn.cursor()
            cur.execute(query)

            result = cur.fetchall()

            final.fields = list([str(i[0])] for i in cur.description)
            final.rows = list([str(y) for y in i] for i in result)

        except Exception as e:
            #Assign error message as error
            final.fields = [['Error']]
            final.rows = [[str(e)]]

        finally:
            #Kill connection
            Simplify().try_pass(conn.close())

            return final

    def execute_query_schemas(self, server_name, query):
        """
        Run normal query and then run for each db in system.
        :param server_name:
        :param query:
        :return:
        """
        class Final(object):
            pass

        final = Final()
        final.rows = []

        server = SQL['MSSQL'][server_name]
        databases = self.fetch_all_return(server_name, 'select name from sys.databases')

        for name in databases:
            try:
                conn = pymssql.connect(host=server_name.lower(),
                                       user=server['USERNAME'],
                                       password=server['PASSWORD'],
                                       database=str(name[0]))
                cur = conn.cursor()

                cur.execute(query)

                result = cur.fetchall()

                final.fields = list([str(i[0])] for i in cur.description)
                final.rows += list([str(name[0]), '{0}.{1}'.format(str(i[0]), str(i[1])), str(i[2])] for i in result)

            except:
                pass

            finally:
                Simplify().try_pass(conn.close())

        return final