from flask import Blueprint
from flask import send_file, current_app, request
import os
import xlsxwriter
import json
from kcsf import mod_api

mod_exports = Blueprint('exports', __name__, url_prefix='/exports')


def create_report(response, title):
    fn = '%s/Reports.xlsx' % current_app.config['EXCEL_DOC_DIR']

    workbook = xlsxwriter.Workbook(fn)
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': True})

    worksheet.set_column('A:A', 20)
    worksheet.set_column('B:B', 20)

    worksheet.write('A1', "Pyetja", bold)
    worksheet.write('A2', 'Tipi', bold)
    worksheet.write('B2', 'Totali', bold)
    worksheet.write(0, 0, title)

    i = 2
    for item in response['result']:
        tipi = item['type']
        totali = item['count']

        worksheet.write(i, 0, tipi)
        worksheet.write(i, 1, totali)
        i = i + 1

    workbook.close()
    return fn


@mod_exports.route('/export', methods=['GET'])
def export_reports():
    if(len(request.args) > 0):
        question = request.args.get('questionID')
        questionTittle = request.args.get('questionTitle')

    aggregation = mod_api.views.aggregation(question)
    fn = create_report(aggregation, questionTittle)
    path = os.path.join(current_app.config['EXCEL_DOC_DIR'], fn)
    return send_file(path, mimetype='application/vnd.ms-excel')


def build_cursor(cursor):
    response = json.loads('{}')
    response_to_append_to = response['result'] = []
    for idx, itm in enumerate(cursor):
        response_to_append_to.append(itm)
    return response
