from app import create_app

app = create_app()
app.run('0.0.0.0', debug=True, port=5000)
