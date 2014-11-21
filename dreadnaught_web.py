__author__ = 'Przemyslaw "Blasto" Wentrys'

from flask import Flask

from config.configuration import WEB_IP, WEB_PORT
from sql.mysql import MySQL_Connection
from sql.functions import MySQL_Functions


app = Flask(__name__, static_folder='static', static_url_path='', template_folder='templates')
app.config.from_object(__name__)


@app.route('/')
def index():
    return 'Hello World!'


@app.route('/mysql/test')
def mysql_test():
    execute = MySQL_Connection().execute
    query = MySQL_Functions()

    server = 'Naboo'
    database = 'jira'
    table = 'jiraissue'
    columns = '*'

    return str(execute(server, query.check_for_existence(database, table, columns)).rows)


@app.route('/mysql/formatted')
def mysql_formatted():
    execute = MySQL_Connection().execute
    query = MySQL_Functions()

    final_result = []
    server = 'Naboo'
    database = 'jira'
    table = 'jiraissue'
    columns = '*'

    result_raw = execute(server, query.check_for_existence(database, table, columns))

    result_formatted = {
        'col_names': list(result_raw.fields),
        'data': list(result_raw.rows)
    }

    for row_index in range(0, len(result_formatted['data'])):
        loop_result = {}
        row = result_formatted['data'][row_index]
        print row

        for col_index in range(0, len(row)):
            column = row[col_index]
            print column

            try:
                loop_result.update({result_formatted['col_names'][col_index][0]: int(column)})
            except:
                loop_result.update({result_formatted['col_names'][col_index][0]: str(column)})

        final_result.append(loop_result)

    return str(final_result)


if __name__ == '__main__':
    app.run(host=WEB_IP, port=WEB_PORT, debug=True)