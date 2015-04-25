from flask import Blueprint, render_template

mod_visualisation = Blueprint('visualisation', __name__)

@mod_visualisation.route('/', methods=['GET'])
def home():
    '''
    Show map page.
    '''
    return render_template('home.html')

@mod_visualisation.route('/visualisation', methods=['GET'])
def visualisation():
    '''
    Show map page.
    '''
    return render_template('index.html')
