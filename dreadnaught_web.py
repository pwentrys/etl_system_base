__author__ = 'Przemyslaw "Blasto" Wentrys'

from flask import Flask, render_template, request
import json

from config.configuration import WEB_IP, WEB_PORT
from helpers.sql.mysql.mysql import MySQL_Connection
from helpers.sql.mssql.mssql import MSSQL_Connection
from helpers.sql.mysql.functions import MySQL_Functions
from helpers.sql.mssql.functions import MSSQL_Functions
from helpers.forms.web import Query


app = Flask(__name__, static_folder='static', static_url_path='', template_folder='templates')
app.config.from_object(__name__)
app.secret_key = u'rawr'


@app.route('/')
def index():
    return 'Hello World!'

@app.route('/mysql/test', methods=['GET', 'POST'])
def mysql_test():

    execute = MySQL_Connection().execute_query
    query = MySQL_Functions()
    form = Query(request.form)
    template = 'sql/result_table_accordion_formatted.html'
    server = 'Naboo'
    schema_nav = ''
    col_names = ''

    schema_raw = execute(server, query.get_schema())
    result_dict = {}
    for schema, table, column in schema_raw.rows:
        result_dict[str(schema)] = {}

    for schema, table, column in schema_raw.rows:
        result_dict[str(schema)][str(table)] = []

    for schema, table, column in schema_raw.rows:
        result_dict[str(schema)][str(table)].append(str(column))

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
    get_schemas = MSSQL_Connection().execute_query_schemas
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