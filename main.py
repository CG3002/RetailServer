from retailserver import app
from retailserver.database import db

if __name__ == "__main__":
	db.create_all()

	app.debug = True
	app.run('127.0.0.1', 8000)