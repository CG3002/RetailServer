from retailserver import app
from retailserver.database import db, Product, TransactionTimestamp, TransactionDetails, PriceDisplayUnit
from retailserver.model_views import ProductAdmin, TransactionDescAdmin, TransactionStampAdmin, PriceDisplayUnitAdmin
from flask.ext.admin import Admin

if __name__ == "__main__":
	
	#create DB
	db.create_all()

	#create admin
	admin = Admin(app, name="Retail Server")

	#add model views
	admin.add_view(ProductAdmin(Product, db.session))
	admin.add_view(TransactionDescAdmin(TransactionDetails, db.session))
	admin.add_view(TransactionStampAdmin(TransactionTimestamp, db.session))
	admin.add_view(PriceDisplayUnitAdmin(PriceDisplayUnit, db.session))
	app.debug = True
	app.run('127.0.0.1', 5000)