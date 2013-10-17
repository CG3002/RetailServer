from retailserver import app
from retailserver.database import db, Product
from retailserver.model_views import ProductAdmin
from flask.ext.admin import Admin

if __name__ == "__main__":
	
	#create DB
	db.create_all()

	#create admin
	admin = Admin(app, name="Retail Server")

	#add model views
	admin.add_view(ProductAdmin(Product, db.session))

	app.debug = True
	app.run('127.0.0.1', 8000)