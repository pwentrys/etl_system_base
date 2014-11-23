__author__ = 'Przemyslaw "Blasto" Wentrys'


from helpers.simplifiers.functions import Simplify


class MySQL_Functions():
    def __init__(self):
        pass

    def check_for_existence(self, database, table, columns):
        return 'select {2} from `{0}`.`{1}`;'.format(database, table, columns)

    def get_schema(self):
        return 'select ' \
               'TABLE_SCHEMA as "Database", ' \
               'TABLE_NAME as "Table", ' \
               'COLUMN_NAME as "Column" ' \
               'from ' \
               'INFORMATION_SCHEMA.columns ' \
               'group by TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME;'

    def datatables_columns(self, columns):
        col_names = ''

        for col_name in columns:
            col_names += '{0}"class": "center", "title": "{1}"{2},'.format('{', col_name[0], '}')

        return col_names[:-1]

    def datatables_data(self, data):
        formatted_data = []

        for row_index in range(0, len(data)):
            loop_result = []
            row = data[row_index]

            for col_index in range(0, len(row)):
                column = row[col_index]

                try:
                    loop_result.append(int(column))
                except:
                    loop_result.append(str(column))

            formatted_data.append(loop_result)

        return list(formatted_data)

    def datatables_output(self, result):
        try:
            final_result = {
                'col_names': self.datatables_columns(result.fields),
                'data': self.datatables_data(result.rows)
            }
        except:
            final_result = {
                'col_names': '{0}"class": "center", "title": "{1}"{2},{0}"class": "center", "title": "{3}"{2}'.format(
                    '{', 'Error ID', '}', 'Error MSG'
                ),
                'data': [[str(result[0]), str(result[1])]]
            }

        return final_result