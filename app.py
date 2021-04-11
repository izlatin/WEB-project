from app import create_app

app = create_app()
app.run('127.0.0.1', debug=True, port=5000, ssl_context='adhoc')
