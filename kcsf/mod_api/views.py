from flask import Blueprint
from flask import Response, request
from bson import json_util
from kcsf import mongo
from slugify import slugify

mod_api = Blueprint('api', __name__, url_prefix='/api')


@mod_api.route('/data', methods=['GET', 'POST'])
def route():
    if(len(request.args) > 0):
        tipi = request.args.get('questionID')
        data = request.args.get('data')

    if data:
        json_response = aggregation(tipi, data)
    else:
        json_response = aggregation(tipi)
    resp = Response(
                response=json_util.dumps(json_response['result']),
                mimetype='application/json')
    return resp


def aggregation(tipi, match_str=None):
    questions_array = []
    for i in range(1, 99):
        questions_array.append("q" + str(i))

    match_fields = {}
    match_in_array = []
    if match_str:
        json_obj = json_util.loads(match_str)
        for item in json_obj:
            if item[:-1] == "municipality":
                match_in_array.append(slugify(json_obj[item]))
                match_fields["organisation.municipality.slug"] = {
                    "$in": match_in_array,
                    "$nin": [""]
                }
            if item[:-1] == "type":
                match_in_array.append(json_obj[item])
                match_fields["organisation.type"] = {
                    "$in": match_in_array,
                    "$nin": [""]
                }
            if item[:-1] == "year":
                match_in_array.append(int(json_obj[item]))
                match_fields["organisation.foundingYear"] = {
                    "$in": match_in_array,
                    "$nin": [""]
                }
            if item[:-1] == "isRegistered":
                match_in_array.append(json_obj[item])
                match_fields["organisation.registered.isRegistered"] = {
                    "$in": match_in_array,
                    "$nin": [""]
                }
            if item[:-1] == "registration-form":
                match_in_array.append(json_obj[item])
                match_fields["organisation.registered.registrationForm"] = {
                    "$in": match_in_array,
                    "$nin": [""]
                }
            if item[:-1] in questions_array:
                match_in_array.append(json_obj[item])
                match_fields["organisation.%s.answer" % item[:-1]] = {
                    "$in": match_in_array,
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
