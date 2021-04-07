# from app import app
from flask import render_template, Blueprint

main_page = Blueprint('main_main', __name__)


@main_page.route('/')
@main_page.route('/index')
def index():
    return render_template('index.html')
    # return 'index'


@main_page.route('/login')
def login():
    return 'login'


@main_page.route('/register')
def sign_up():
    return 'register'