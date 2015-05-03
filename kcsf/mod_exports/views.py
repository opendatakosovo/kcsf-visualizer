from flask import Blueprint
from flask import send_file, current_app, request
import os
import xlsxwriter
from kcsf import mod_api

mod_exports = Blueprint('exports', __name__, url_prefix='/exports')


def create_report(response, title):
    fn = '%s/Reports.xlsx' % current_app.config['EXCEL_DOC_DIR']

    workbook = xlsxwriter.Workbook(fn)
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 10})
    bold_question = workbook.add_format({'bold': True, 'font_size': 10})
    font_size = workbook.add_format({'font_size': 10})
    value_column = workbook.add_format({'font_size': 10, 'align': 'center'})

    worksheet.set_column('A:A', 30)
    worksheet.set_column('B:B', 30)

    worksheet.write('A1', "Pyetja", bold)
    worksheet.write('A2', 'Tipi', bold)
    worksheet.write('B2', 'Totali', bold)
    worksheet.write(0, 0, title, bold_question)

    for i, item in enumerate(response['result']):
        tipi = item['type']
        totali = item['count']

        worksheet.write(i + 2, 0, tipi, font_size)
        worksheet.write(i + 2, 1, totali, value_column)

    workbook.close()
    return fn


@mod_exports.route('/export', methods=['GET'])
def export_reports():
    if(len(request.args) > 0):
        question = request.args.get('questionID')
        questionTittle = request.args.get('questionTitle')
        data = request.args.get('data')

    if data:
        aggregation = mod_api.views.aggregation(question, data)
    else:
        aggregation = mod_api.views.aggregation(question)
    fn = create_report(aggregation, questionTittle)
    path = os.path.join(current_app.config['EXCEL_DOC_DIR'], fn)
    return send_file(path, mimetype='application/vnd.ms-excel')
