__author__ = 'Przemyslaw "Blasto" Wentrys'

from flask import Flask, render_template, request

from config.configuration import WEB_IP, WEB_PORT
from sql.mysql import MySQL_Connection
from sql.functions import MySQL_Functions


app = Flask(__name__, static_folder='static', static_url_path='', template_folder='templates')
app.config.from_object(__name__)
app.secret_key = u'rawr'


@app.route('/')
def index():
    return 'Hello World!'


@app.route('/mysql/test')
def mysql_test():
    execute = MySQL_Connection().execute_query
    query = MySQL_Functions()

    server = 'Naboo'
    database = 'jira'
    table = 'jiraissue'
    columns = '*'

    return str(execute(server, query.check_for_existence(database, table, columns)).rows)


@app.route('/mysql/formatted')
def mysql_formatted():
    execute = MySQL_Connection().execute_query
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


@app.route('/mysql/datatables')
def mysql_datatables_no_pagination():
    execute = MySQL_Connection().execute_query
    query = MySQL_Functions()

    final_result = []
    col_names = ''
    server = 'Naboo'
    database = 'jira'
    table = 'jiraissue'
    columns = '*'

    result_raw = execute(server, query.check_for_existence(database, table, columns))

    for col_name in result_raw.fields:
        col_names += '{0}"class": "center", "title": "{1}"{2},'.format('{', col_name[0], '}')

    result_formatted = {
        'col_names': col_names[:-1],
        'data': list(result_raw.rows)
    }

    for row_index in range(0, len(result_formatted['data'])):
        loop_result = []
        row = result_formatted['data'][row_index]
        print row

        for col_index in range(0, len(row)):
            column = row[col_index]
            print column

            try:
                loop_result.append(int(column))
            except:
                loop_result.append(str(column))

        final_result.append(loop_result)

    final_result = {'col_names': result_formatted['col_names'], 'data': final_result}

    print final_result

    return render_template('sql/result_table.html', jira_data=final_result)


@app.route('/mysql/datatables_multiple', methods=['GET', 'POST'])
def mysql_datatables_no_pagination_multiple():
    from forms import Query

    execute = MySQL_Connection().execute_query
    query = MySQL_Functions()
    form = Query(request.form)

    server = 'Naboo'
    database = 'jira'
    table = 'jiraissue'
    columns = '*'

    # result_raw = execute(server, query.check_for_existence(database, table, columns))
    if request.method == 'POST':
        if form.validate():
            result_raw = execute(server, str(form.query.data))
            result_formatted = query.datatables_output(result_raw)
            return render_template('sql/result_table_multiple.html', form=form, title=str(form.query.data),
                                   jira_data=result_formatted)
        else:
            return """ VALIDATION ERROR """
    elif request.method == 'GET':
        result_raw = execute(server, query.check_for_existence(database, table, columns))
        result_formatted = query.datatables_output(result_raw)

        return render_template('sql/result_table_multiple.html', form=form, title="Jira Issues",
                               jira_data=result_formatted)
    else:
        return str(request.method) + 'NOT ALLOWED'

if __name__ == '__main__':
    app.run(host=WEB_IP, port=WEB_PORT, debug=True)