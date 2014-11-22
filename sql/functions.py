__author__ = 'Przemyslaw "Blasto" Wentrys'


class MySQL_Functions():
    def __init__(self):
        pass

    def check_for_existence(self, database, table, columns):
        return 'select {2} from `{0}`.`{1}`;'.format(database, table, columns)

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
        final_result = {
            'col_names': self.datatables_columns(result.fields),
            'data': self.datatables_data(result.rows)
        }

        return final_result