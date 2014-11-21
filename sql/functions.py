__author__ = 'Przemyslaw "Blasto" Wentrys'


class MySQL_Functions():
    def __init__(self):
        pass

    def check_for_existence(self, database, table, columns):
        return 'select {2} from `{0}`.`{1}`;'.format(database, table, columns)