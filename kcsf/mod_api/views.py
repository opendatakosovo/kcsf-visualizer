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
    json_obj_q2ID = json_obj['question2ID']
    json_obj_match_str = json_obj['match']
    if json_obj_q2ID != "":
        json_response = aggregation(json_obj_qID, json_obj_q2ID, json_obj_match_str)
    else:
        json_response = aggregation(json_obj_qID, "",  json_obj_match_str)
    resp = Response(
        response=json_util.dumps(json_response['result']),
        mimetype='application/json')
    return resp


def aggregation(tipi, q2, match_str):
    questions_array = []
    for i in range(1, 99):
        questions_array.append("q" + str(i))

    match_fields = {}
    get_aggregation_match_filter(match_str, match_fields, questions_array, tipi)
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
    group_variable1 = ""
    if q2 != "":
        if q2 not in questions_array:
            group_variable1 = get_questionID_primary(q2)
        else:
            group_variable1 = "organisation.%s.answer" % q2
    if tipi not in questions_array:
        group_variable = get_questionID_primary(tipi)
        get_aggregation_match(group_variable, match_fields)
        group = get_aggregation_group(group_variable)
        match = {
            "$match": match_fields
        }
        aggregation = get_q2_aggregation(group_variable1, match, group, project, sort, q2, match_fields, questions_with_array_answers)
    else:
        if tipi not in questions_with_array_answers:
            group_variable = "organisation.%s.answer" % tipi

            get_aggregation_match(group_variable, match_fields)

            match = {
                "$match": match_fields
            }
            group = get_aggregation_group(group_variable)
            aggregation = get_q2_aggregation(group_variable1, match, group, project, sort, q2, match_fields, questions_with_array_answers)
        else:
            group_variable = "organisation.%s.answer" % tipi
            unwind = {
                "$unwind": "$%s" % group_variable
            }

            match = {
                "$match": match_fields
            }

            get_aggregation_match(group_variable, match_fields)
            group = get_aggregation_group(group_variable)
            aggregation = get_q2_aggregation(group_variable1, match, group, project, sort, q2, match_fields, questions_with_array_answers)
            aggregation.insert(0, unwind)

    rezultati = mongo.db.ikshc.aggregate(aggregation)
    return rezultati


def get_aggregation_match_filter(match_str, match_fields, questions_array, tipi):
    if match_str != {}:
        for item in match_str:
            if item == "municipality":
                match_fields["organisation.municipality.name"] = {
                    "$in": match_str[item],
                    "$nin": [""]
                }
            if item == "type":
                match_fields["organisation.type"] = {
                    "$in": match_str[item],
                    "$nin": [""]
                }
            if item == "year":
                year_array = []
                for i in match_str[item]:
                    year_array.append(int(i))
                match_fields["organisation.foundingYear"] = {
                    "$in": year_array,
                    "$nin": [""]
                }
            if item == "isRegistered":
                match_fields["organisation.registered.isRegistered"] = {
                    "$in": match_str[item],
                    "$nin": [""]
                }
            if item == "registration-form":
                match_fields["organisation.registered.registrationForm"] = {
                    "$in": match_str[item],
                    "$nin": [""]
                }
            if item in questions_array:
                match_fields["organisation.%s.answer" % item] = {
                    "$in": match_str[item],
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


def get_q2_aggregation(group_variable1, match, group, project, sort, q2, match_fields, questions_with_array_answers):
    aggregation = []
    if group_variable1 != "":
        match['$match'][group_variable1] = {"$nin": [""]}
        group['$group']['_id']['type1'] = "$" + group_variable1
        project['$project']['type1'] = "$_id.type1"
        sort['$sort'] = {"type1": 1}
        aggregation = [match, group, project, sort]
        if q2 in questions_with_array_answers:
            unwind1 = {"$unwind": "$" + group_variable1}
            match = {
                "$match": match_fields
            }
            aggregation = [unwind1, match, group, project, sort]
        else:
            aggregation = [match, group, project, sort]
    else:
        aggregation = [match, group, project, sort]
    return aggregation


def get_aggregation_group(variable):
    group = {
                "$group": {
                    "_id": {
                        "type": "$" + variable
                    },
                    "count": {
                        "$sum": 1
                    }
                }
            }
    return group


def get_aggregation_match(variable, match_fields):
    if variable in match_fields:
        match_fields[variable]['$nin'].append("")
    else:
        match_fields[variable] = {
            "$nin": [""]
        }


def get_questionID_primary(question):
    group_variable = ""
    if question == "municipality":
        group_variable = "organisation.municipality.name"
    elif question == "type":
        group_variable = "organisation.type"
    elif question == "isRegistered":
        group_variable = "organisation.registered.isRegistered"
    elif question == "year":
        group_variable = "organisation.foundingYear"
    elif question == "registration-form":
        group_variable = "organisation.registered.registrationForm"

    return group_variable

@mod_api.route('/comparison', methods=['GET'])
def comparison():
    '''
    questions_with_array_answers = [
        "q44", "q3", "q5", "q8", "q36", "q38", "q58",
        "q21", "q91", "q15", "q16", "q10", "q12", "q88",
        "q64", "q68", "q61", "q63", "q55", "q57", "q59"]
    '''
    '''
    {
        "$unwind": "$organisation.q8.answer",
    },
    {
        "$unwind": "$organisation.q5.answer"
    },
    '''
    aggregation = [
            {
                "$unwind": "$organisation.q8.answer"
            },
            {
                "$unwind": "$organisation.q3.answer"
            },
            {
                "$match": {
                    "organisation.q8.answer": {
                        "$nin": [""]
                    },
                    "organisation.q3.answer": {
                        "$nin": [""]
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "type": "$organisation.q8.answer",
                        "type1": "$organisation.q3.answer"
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
                    "type1": "$_id.type1",
                    "count": "$count"
                }
            },
            {
                '$sort': {
                    "type2": 1
                }
            }
        ]
    rezultati = mongo.db.ikshc.aggregate(aggregation)
    resp = Response(
        response=json_util.dumps(rezultati['result']),
        mimetype='application/json')
    return resp
