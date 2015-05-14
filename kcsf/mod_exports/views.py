from flask import Blueprint
from flask import send_file, current_app, request
import os
import xlsxwriter
from bson import json_util
from kcsf import mod_api

mod_exports = Blueprint('exports', __name__, url_prefix='/exports')


def create_report(q2, response, title, title2):
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
    worksheet.write('A3', 'Pergjigja e Pyetjes 1', bold)
    if q2 != "":
        worksheet.write('B3', 'Pergjigja e Pyetjes 2', bold)
        worksheet.write('C3', 'Totali', bold)
        worksheet.write(1, 0, "Pyetja 2: " + title2, bold_question)
    else:
        worksheet.write('B3', 'Totali', bold)
    worksheet.write(0, 0, "Pyetja 1: " + title, bold_question)

    for i, item in enumerate(response['result']):
        tipi = item['type']
        totali = item['count']
        worksheet.write(i + 3, 0, tipi, font_size)
        if q2 != "":
            tipi1 = item['type1']
            worksheet.write(i + 3, 1, tipi1, value_column)
            worksheet.write(i + 3, 2, totali, value_column)
        else:
            worksheet.write(i + 2, 1, totali, value_column)

    workbook.close()
    return fn


@mod_exports.route('/export', methods=['GET'])
def export_reports():
    if(len(request.args) > 0):
        question = request.args.get('questionID')
        question2 = request.args.get('question2ID')
        questionTittle = request.args.get('questionTitle')
        question2Tittle = request.args.get('question2_title')
        data = request.args.get('data')
    if data:
        json_obj_data = json_util.loads(data)
        if question2 != "":
            aggregation = mod_api.views.aggregation(question, question2, json_obj_data['match'])
        else:
            aggregation = mod_api.views.aggregation(question, "", json_obj_data['match'])

    print aggregation
    fn = create_report(question2, aggregation, questionTittle, question2Tittle)
    path = os.path.join(current_app.config['EXCEL_DOC_DIR'], fn)
    return send_file(path, mimetype='application/vnd.ms-excel')
