from flask import Blueprint, render_template

mod_visualisation = Blueprint('visualisation', __name__)


@mod_visualisation.route('/visualisation', methods=['GET'])
def visualisation():
    '''
    Show map page.
    '''
    return render_template('index.html')
