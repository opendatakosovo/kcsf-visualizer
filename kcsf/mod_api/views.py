from flask import Blueprint
from flask import Response
from bson import json_util
from kcsf import mongo

mod_api = Blueprint('api', __name__, url_prefix='/api')


@mod_api.route('/data/<string:tipi>', methods=['GET'])
def route(tipi):
    rezultati = []
    group = ""
    if tipi == "municipality":
        group = "organisation.municipality.name"
    elif tipi == "type":
        group = "organisation.type"
    elif tipi == "isRegistered":
        group = "organisation.registered.isRegistered"
    elif tipi == "year":
        group = "organisation.foundingYear"
    elif tipi == "organi-vendimmarres":
        group = "organisation.q1.answer"
    elif tipi == "registration-form":
        group = "organisation.registered.registrationForm"
    elif tipi == "fondacion":
        group = "organisation.q45.answer"
    elif tipi == "q33":
        group = "organisation.q67.answer.a1.value"


    rezultati = mongo.db.ikshc.aggregate([
        {
            "$match": {
                group: {
                    "$ne": ""
                }
            }
        },
        {
            "$group": {
               "_id": {
                    "type": "$" + group
                },
                "count": {
                    "$sum": 1
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "type": "$_id.type",
                "count": "$count"
            }
        },
        {
            "$sort": {
                "type": 1
            }
        }
    ])

    # pergjigjen e kthyer dhe te konvertuar ne JSON ne baze te json_util.dumps() e ruajme ne  resp
    resp = Response(
            response=json_util.dumps(rezultati['result']),
            mimetype='application/json')

    return resp
