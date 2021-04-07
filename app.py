# from flask import Flask, render_template, redirect
# from flask_login import current_user, LoginManager, login_user
# from flask_oauthlib.provider import OAuth2Provider

# import db_session

# def create_app():
#     app = Flask(__name__, template_folder='templates', static_folder='static')
#     app.config['SECRET_KEY'] = 'b@rter_2hop_secre3_key'    
#     app.config['TESTING'] = False
    
#     from routes import auth, main_page    
#     app.register_blueprint(main_page.main)
#     app.register_blueprint(auth.auth)
    
#     # init auth and oauth
#     login_manager = LoginManager()
#     login_manager.init_app(app)
#     oauth = OAuth2Provider(app)
    
#     # register login views
#     login_manager.blueprint_login_views = {
#         'main': '/',
#     }
#     from models import User
#     @login_manager.user_loader
#     def load_user(user_id):
#         db_sess = db_session.create_session()
#         return db_sess.query(models.User).get(user_id)

#     return app

    
    

# if __name__ == '__main__':
#     app = create_app()
    

    
#     db_session.global_init("barter.db")
    
#     app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
from app import create_app

app = create_app()
app.run('0.0.0.0', debug=True, port=5000)
