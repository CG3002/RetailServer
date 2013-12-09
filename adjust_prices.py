from retailserver import database
from retailserver import constants
from retailserver import views
from retailserver import celery

@celery.task()
def adjust_prices():
	products=database.Product.query.all()
	print "Hi"

	for product in products:
		product.adjust_price()
		database.db.session.commit()
	# views.hq_stock_level_sync(product)