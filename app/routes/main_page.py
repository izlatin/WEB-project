# from app import app
from flask import render_template, Blueprint

page = Blueprint('page', __name__)

@page.route('/')
@page.route('/index')
def index():
    # return render_template('index.html')
    return 'index'


@page.route('/login')
def login():
    return 'login'


@page.route('/register')
def sign_up():
    return 'register'