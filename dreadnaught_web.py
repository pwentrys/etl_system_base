__author__ = 'Przemyslaw "Blasto" Wentrys'

from flask import Flask, render_template, request

from config.configuration import WEB_IP, WEB_PORT
from sql.mysql import MySQL_Connection
from sql.mssql import MSSQL_Connection
from sql.functions import MySQL_Functions, MSSQL_Functions
from forms import Query
import json


app = Flask(__name__, static_folder='static', static_url_path='', template_folder='templates')
app.config.from_object(__name__)
app.secret_key = u'rawr'


@app.route('/')
def index():
    return 'Hello World!'


@app.route('/mysql/testt')
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

    execute = MySQL_Connection().execute_query
    query = MySQL_Functions()
    form = Query(request.form)
    template = 'sql/result_table_multiple.html'

    server = 'Naboo'
    database = 'jira'
    table = 'jiraissue'
    columns = '*'

    if request.method == 'POST':
        if form.validate():
            result_raw = execute(server, str(form.query.data))
            result_formatted = query.datatables_output(result_raw)
            return render_template(template, form=form, title=str(form.query.data),
                                   jira_data=result_formatted)
        else:
            return render_template(template, form=form, title=str(form.query.data),
                                   jira_data='ERROR')
    elif request.method == 'GET':
        result_raw = execute(server, query.check_for_existence(database, table, columns))
        result_formatted = query.datatables_output(result_raw)

        return render_template(template, form=form, title="Jira Issues",
                               jira_data=result_formatted)
    else:
        return str(request.method) + 'NOT ALLOWED'


@app.route('/mysql/datatables_accordion', methods=['GET', 'POST'])
def mysql_datatables_no_pagination_accordion():

    execute = MySQL_Connection().execute_query
    query = MySQL_Functions()
    form = Query(request.form)
    template = 'sql/result_table_accordion.html'
    server = 'Naboo'


    schema_raw = execute(server, query.get_schema())
    result_dict = {}
    for schema, table, column in schema_raw.rows:
        result_dict[str(schema)] = {}

    for schema, table, column in schema_raw.rows:
        result_dict[str(schema)][str(table)] = []

    for schema, table, column in schema_raw.rows:
        result_dict[str(schema)][str(table)].append(str(column))


    schema_nav = ''
    col_names = ''

    for col_name in schema_raw.fields:
        col_names += '{0}"class": "center", "title": "{1}"{2},'.format('{', col_name[0], '}')

    for schema in result_dict.iterkeys():
        schema_nav += '{0} \'text\': \'{1}\','.format('{', schema)
        schema_nav += '\'children\': {0}'.format('[')
        for table in result_dict[schema].iterkeys():
            schema_nav += '{0} \'text\': \'{1}\','.format('{', table)
            schema_nav += '\'children\': {0}'.format('[')
            for column in result_dict[schema][table]:
                schema_nav += '{0}\'text\': \'{1}\''.format('{', column)
                schema_nav += '{0}'.format('},')
                print column, schema, table
            schema_nav = schema_nav[:-1] + '{0}'.format(']')
            schema_nav += '{0}'.format('},')

        schema_nav = schema_nav[:-1] + '{0}'.format(']')
        schema_nav += '{0}'.format('},')

    if request.method == 'POST':
        if form.validate():
            result_raw = execute(server, str(form.query.data))
            result_formatted = query.datatables_output(result_raw)
            return render_template(template, form=form, schema=str(json.dumps(schema_nav))[1:-1],
                                   title=str(form.query.data),
                                   data=result_formatted)
        else:
            return render_template(template, form=form, schema=str(json.dumps(schema_nav))[1:-1],
                                   title=str(form.query.data),
                                   data='ERROR')
    elif request.method == 'GET':
        result_raw = execute(server, query.check_for_existence('jira', 'jiraissue', 'ID as "id", issuenum as "Issue Num", PROJECT as "Project", ASSIGNEE as "Assignee", PRIORITY as "Priority", issuestatus as "Issue Status"'))
        result_formatted = query.datatables_output(result_raw)

        return render_template(template, form=form, schema=str(json.dumps(schema_nav))[1:-1],
                               title=query.check_for_existence('jira', 'jiraissue', 'ID as "id", issuenum as "Issue Num", PROJECT as "Project", ASSIGNEE as "Assignee", PRIORITY as "Priority", issuestatus as "Issue Status"'),
                               data=result_formatted,)
    else:
        return str(request.method) + 'NOT ALLOWED'


@app.route('/mysql/datatables_accordion_formatted', methods=['GET', 'POST'])
@app.route('/mysql/test', methods=['GET', 'POST'])
def mysql_datatables_no_pagination_accordion_formatted():

    execute = MySQL_Connection().execute_query
    query = MySQL_Functions()
    form = Query(request.form)
    template = 'sql/result_table_accordion_formatted.html'
    server = 'Naboo'


    schema_raw = execute(server, query.get_schema())
    result_dict = {}
    for schema, table, column in schema_raw.rows:
        result_dict[str(schema)] = {}

    for schema, table, column in schema_raw.rows:
        result_dict[str(schema)][str(table)] = []

    for schema, table, column in schema_raw.rows:
        result_dict[str(schema)][str(table)].append(str(column))


    schema_nav = ''
    col_names = ''

    for col_name in schema_raw.fields:
        col_names += '{0}"class": "center", "title": "{1}"{2},'.format('{', col_name[0], '}')

    for schema in result_dict.iterkeys():
        schema_nav += '{0} \'text\': \'{1}\','.format('{', schema)
        schema_nav += '\'children\': {0}'.format('[')
        for table in result_dict[schema].iterkeys():
            schema_nav += '{0} \'text\': \'{1}\','.format('{', table)
            schema_nav += '\'children\': {0}'.format('[')
            for column in result_dict[schema][table]:
                schema_nav += '{0}\'text\': \'{1}\''.format('{', column)
                schema_nav += '{0}'.format('},')
                print column, schema, table
            schema_nav = schema_nav[:-1] + '{0}'.format(']')
            schema_nav += '{0}'.format('},')

        schema_nav = schema_nav[:-1] + '{0}'.format(']')
        schema_nav += '{0}'.format('},')

    if request.method == 'POST':
        if form.validate():
            result_raw = execute(server, str(form.query.data))
            result_formatted = query.datatables_output(result_raw)
            return render_template(template, form=form, schema=str(json.dumps(schema_nav))[1:-1],
                                   title=str(form.query.data),
                                   data=result_formatted)
        else:
            return render_template(template, form=form, schema=str(json.dumps(schema_nav))[1:-1],
                                   title=str(form.query.data),
                                   data='ERROR')
    elif request.method == 'GET':
        result_raw = execute(server, query.check_for_existence('jira', 'jiraissue', 'ID as "id", issuenum as "Issue Num", PROJECT as "Project", ASSIGNEE as "Assignee", PRIORITY as "Priority", issuestatus as "Issue Status"'))
        result_formatted = query.datatables_output(result_raw)

        return render_template(template, form=form, schema=str(json.dumps(schema_nav))[1:-1],
                               title=query.check_for_existence('jira', 'jiraissue', 'ID as "id", issuenum as "Issue Num", PROJECT as "Project", ASSIGNEE as "Assignee", PRIORITY as "Priority", issuestatus as "Issue Status"'),
                               data=result_formatted,)
    else:
        return str(request.method) + 'NOT ALLOWED'


@app.route('/mssql/test', methods=['GET', 'POST'])
def mssql_test():
    execute = MSSQL_Connection().execute_query
    get_schemas = MSSQL_Connection().get_schemas
    query = MSSQL_Functions()
    form = Query(request.form)
    template = 'sql/mssql_result_table_accordion_formatted.html'
    server = 'Dagobah'

    schema_raw = get_schemas(server, query.get_schema())
    result_dict = {}
    for schema, table, column in schema_raw.rows:
        result_dict[str(schema)] = {}

    for schema, table, column in schema_raw.rows:
        result_dict[str(schema)][str(table).split('.')[0]] = {}

    for schema, table, column in schema_raw.rows:
        result_dict[str(schema)][str(table).split('.')[0]][str(table).split('.')[1]] = []

    for schema, table, column in schema_raw.rows:
        result_dict[str(schema)][str(table).split('.')[0]][str(table).split('.')[1]].append(str(column))

    schema_nav = ''
    col_names = ''

    for col_name in schema_raw.fields:
        col_names += '{0}"class": "center", "title": "{1}"{2},'.format('{', col_name[0], '}')

    for database in result_dict.iterkeys():
        schema_nav += '{0} \'text\': \'{1}\','.format('{', database)
        schema_nav += '\'children\': {0}'.format('[')
        for schema in result_dict[database].iterkeys():
            schema_nav += '{0} \'text\': \'{1}\','.format('{', schema)
            schema_nav += '\'children\': {0}'.format('[')
            for table in result_dict[database][schema]:
                schema_nav += '{0} \'text\': \'{1}\','.format('{', table)
                schema_nav += '\'children\': {0}'.format('[')
                for column in result_dict[database][schema][table]:
                    schema_nav += '{0}\'text\': \'{1}\''.format('{', column)
                    schema_nav += '{0}'.format('},')
                schema_nav = schema_nav[:-1] + '{0}'.format(']')
                schema_nav += '{0}'.format('},')
            schema_nav = schema_nav[:-1] + '{0}'.format(']')
            schema_nav += '{0}'.format('},')

        schema_nav = schema_nav[:-1] + '{0}'.format(']')
        schema_nav += '{0}'.format('},')

    if request.method == 'POST':
        if form.validate():
            result_raw = execute(server, str(form.query.data))
            result_formatted = query.datatables_output(result_raw)
            return render_template(template, form=form, schema=str(json.dumps(schema_nav))[1:-1],
                                   title=str(form.query.data),
                                   data=result_formatted)
        else:
            return render_template(template, form=form, schema=str(json.dumps(schema_nav))[1:-1],
                                   title=str(form.query.data),
                                   data='ERROR')
    elif request.method == 'GET':
        result_raw = execute(server, query.check_for_existence('sys', 'databases', '*'))
        result_formatted = query.datatables_output(result_raw)

        return render_template(template, form=form, schema=str(json.dumps(schema_nav))[1:-1],
                               title=query.check_for_existence('sys', 'databases', '*'),
                               data=result_formatted,)
    else:
        return str(request.method) + 'NOT ALLOWED'

if __name__ == '__main__':
    app.run(host=WEB_IP, port=WEB_PORT, debug=True)