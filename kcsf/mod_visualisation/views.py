from flask import Blueprint, render_template

mod_visualisation = Blueprint('visualisation', __name__)


@mod_visualisation.route('/', methods=['GET'])
def visualisation():
    return render_template('index.html')
