from flask import Blueprint
from flask import Response
from bson import json_util, SON
from kcsf import mongo

mod_api = Blueprint('api', __name__, url_prefix='/api')


@mod_api.route('/data/<string:tipi>', methods=['GET'])
def route(tipi):
    json_response = aggregation(tipi)
    resp = Response(
            response=json_util.dumps(json_response['result']),
            mimetype='application/json')

    return resp


@mod_api.route('/large-questions/<string:question>', methods=['GET'])
def route1(question):
    group = "organisation.%s.answer" % question
    result_json = {}
    for i in range(1, 5):
        a = "a" + str(i)
        rezultati = mongo.db.ikshc.aggregate([
            {
                "$group": {
                    "_id": {
                        "type": "$%s.%s.text" % (group, a)
                    },
                    "count": {
                        "$avg": "$%s.%s.value" % (group, a)
                    }
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "type": "$_id.type",
                    "count": "$count"
                }
            }
        ])

        result_json[a] = rezultati['result'][0]

        resp = Response(
                response=json_util.dumps(result_json),
                mimetype='application/json')

    return resp


@mod_api.route('/q9/<string:operator>', methods=['GET'])
def q9(operator):
    group = "organisation.q9.answer"
    result_json = {}
    for i in range(1, 7):
        a = "a" + str(i)
        rezultati = mongo.db.ikshc.aggregate([
            {
                "$match": {
                    "%s.%s.value" % (group, a): {
                        "$nin": [operator, ""]
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "type": "$%s.%s.text" % (group, a),
                        "vlera": "$%s.%s.value" % (group, a)
                    },
                    "count": {
                        "$sum": 1
                    }
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "vlera": "$_id.vlera",
                    "type": "$_id.type",
                    "count": "$count"
                }
            },
            {
                '$sort':
                    SON([
                        ('type', 1),
                        ('vlera', 1)])
            }
        ])

        result_json[a] = rezultati['result'][0]

        resp = Response(
                response=json_util.dumps(result_json),
                mimetype='application/json')

    return resp


def aggregation(tipi):
    questions_array = []
    for i in range(1, 99):
        questions_array.append("q" + str(i))

    group_variable = ""
    questions_with_array_answers = [
        "q44", "q3", "q5", "q8", "q36", "q38", "q58",
        "q21", "q91", "q15", "q16", "q10", "q12", "q88",
        "q64", "q68", "q61", "q63", "q55", "q57", "q59"]
    unwind = {}
    match = {}
    group = {}
    sort = {
            "$sort": {
                "type": 1
            }
        }
    project = {
            "$project": {
                "_id": 0,
                "type": "$_id.type",
                "count": "$count"
            }
        }
    aggregation = []

    if tipi not in questions_array:
        if tipi == "municipality":
            group_variable = "organisation.municipality.name"
        elif tipi == "type":
            group_variable = "organisation.type"
        elif tipi == "isRegistered":
            group_variable = "organisation.registered.isRegistered"
        elif tipi == "year":
            group_variable = "organisation.foundingYear"
        elif tipi == "registration-form":
            group_variable = "organisation.registered.registrationForm"

        match = {
            "$match": {
                group_variable: {
                    "$ne": ""
                }
            }
        }

        group = {
            "$group": {
                "_id": {
                    "type": "$" + group_variable
                },
                "count": {
                    "$sum": 1
                }
            }
        }

        aggregation = [match, group, project, sort]
    else:
        if tipi not in questions_with_array_answers:
            group_variable = "organisation.%s.answer" % tipi

            match = {
                "$match": {
                    group_variable: {
                        "$ne": ""
                    }
                }
            }

            group = {
                "$group": {
                    "_id": {
                        "type": "$" + group_variable
                    },
                    "count": {
                        "$sum": 1
                    }
                }
            }
            aggregation = [match, group, project, sort]
        else:
            group_variable = "organisation.%s.answer" % tipi
            unwind = {
                "$unwind": "$%s" % group_variable
            }
            match = {
                "$match": {
                    group_variable: {
                        "$ne": ""
                    }
                }
            }

            group = {
                "$group": {
                    "_id": {
                        "type": "$" + group_variable
                    },
                    "count": {
                        "$sum": 1
                    }
                }
            }
            aggregation = [unwind, match, group, project, sort]

    rezultati = mongo.db.ikshc.aggregate(aggregation)
    return rezultati
