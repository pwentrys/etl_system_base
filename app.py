__author__ = 'Przemyslaw "Blasto" Wentrys'


import json

from flask import Flask, render_template, request, redirect, url_for, current_app
from helpers.sql.mysql.mysql import MySQL_Connection
from helpers.sql.mssql.mssql import MSSQL_Connection
from helpers.sql.mysql.functions import MySQL_Functions
from helpers.sql.mssql.functions import MSSQL_Functions
from helpers.forms.web import Query
from config.configuration import WEB

app = Flask(__name__, static_folder='static', static_url_path='', template_folder='templates')
app.config.from_object(__name__)
app.secret_key = u'rawr'


@app.route('/')
def index():
    paths = []
    paths_sub_string = '<a href="{0}">{1}</a><br>'
    paths_string = paths_sub_string.format(url_for('index'), 'Index')
    base_url = request.host.split(':')[0]

    dev = '{0}:{1}'.format(base_url, 1225)
    prod = '{0}:{1}'.format(base_url, 80)

    for path in current_app.url_map.iter_rules():
        if "GET" in path.methods and len(path.arguments) == 0:
            paths.append(str(path))

    for x in range(0, len(sorted(paths))):
        if sorted(paths)[x][1:] in ('', 'index'):
            pass
        else:
            path_name = sorted(paths)[x]
            paths_string += paths_sub_string.format(sorted(paths)[x][1:], path_name[1:- int(len(path_name)-2)].upper() + path_name[2:].replace('/', ' -> '))

    return render_template('base.html', title=WEB['title'], paths=paths_string, base_url=base_url, dev=dev, prod=prod)


@app.route('/index')
def index_redirect():
    return redirect('/')


@app.route('/codiad')
def codiad():
    from config.configuration import CODIAD_PORT
    return redirect('{0}{1}:{2}'.format('http://', request.host.split(':')[0], CODIAD_PORT))


@app.route('/jira')
def jira():
    from config.configuration import JIRA_PORT
    return redirect('{0}{1}:{2}'.format('http://', request.host.split(':')[0], JIRA_PORT))


@app.route('/mysql', methods=['GET', 'POST'])
def mysql():

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


@app.route('/mssql', methods=['GET', 'POST'])
def mssql():
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