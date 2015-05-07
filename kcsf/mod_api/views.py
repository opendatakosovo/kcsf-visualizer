from flask import Blueprint
from flask import Response, request
from bson import json_util
from kcsf import mongo

mod_api = Blueprint('api', __name__, url_prefix='/api')


@mod_api.route('/data', methods=['POST'])
def route():
    json_string = request.data
    json_obj = json_util.loads(json_string)
    json_obj_qID = json_obj['questionID']
    if json_string:
        json_response = aggregation(json_obj_qID, json_string)
    else:
        json_response = aggregation(json_obj_qID)
    resp = Response(
        response=json_util.dumps(json_response['result']),
        mimetype='application/json')
    return resp


def aggregation(tipi, match_str=None):
    questions_array = []
    for i in range(1, 99):
        questions_array.append("q" + str(i))

    match_fields = {}
    if match_str:
        json_obj = json_util.loads(match_str)
        for item in json_obj:
            if item == "municipality":
                match_fields["organisation.municipality.name"] = {
                    "$in": json_obj[item],
                    "$nin": [""]
                }
            if item == "type":
                match_fields["organisation.type"] = {
                    "$in": json_obj[item],
                    "$nin": [""]
                }
            if item == "year":
                year_array = []
                for i in json_obj[item]:
                    year_array.append(int(i))
                match_fields["organisation.foundingYear"] = {
                    "$in": year_array,
                    "$nin": [""]
                }
            if item == "isRegistered":
                match_fields["organisation.registered.isRegistered"] = {
                    "$in": json_obj[item],
                    "$nin": [""]
                }
            if item == "registration-form":
                match_fields["organisation.registered.registrationForm"] = {
                    "$in": json_obj[item],
                    "$nin": [""]
                }
            if item in questions_array:
                match_fields["organisation.%s.answer" % item] = {
                    "$in": json_obj[item],
                    "$nin": [""]
                }
    else:
        if tipi == "municipality":
            match_fields["organisation.%s.name" % tipi] = {
                    "$nin": [""]
                }
        if tipi == "type":
            match_fields["organisation.type"] = {
                "$nin": [""]
            }
        if tipi == "year":
            match_fields["organisation.foundingYear"] = {
                "$nin": [""]
            }
        if tipi == "isRegistered":
            match_fields["organisation.registered.isRegistered"] = {
                "$nin": [""]
            }
        if tipi == "registration-form":
            match_fields["organisation.registered.registrationForm"] = {
                "$nin": [""]
            }
        if tipi in questions_array:
            match_fields["organisation.%s.answer" % tipi] = {
                        "$nin": [""]
                }

    group_variable = ""
    questions_with_array_answers = [
        "q44", "q3", "q5", "q8", "q36", "q38", "q58",
        "q21", "q91", "q15", "q16", "q10", "q12", "q88",
        "q64", "q68", "q61", "q63", "q55", "q57", "q59"]
    unwind = {}
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

        if group_variable in match_fields:
            match_fields[group_variable]['$nin'].append("")
        else:
            match_fields[group_variable] = {
                "$nin": [""]
            }

        match = {
            "$match": match_fields
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

            if group_variable in match_fields:
                match_fields[group_variable]['$nin'].append("")
            else:
                match_fields[group_variable] = {
                    "$nin": [""]
                }

            match = {
                "$match": match_fields
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

            if group_variable in match_fields:
                match_fields[group_variable]['$nin'].append("")
            else:
                match_fields[group_variable] = {
                    "$nin": [""]
                }

            match = {
                "$match": match_fields
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
