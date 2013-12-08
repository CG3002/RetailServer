from retailserver import database
from retailserver import constants
from retailserver import views
from retailserver import celery

@celery.task()
def restock():
	products=database.Product.query.all()
	no_of_products_at_min_stock = 0
	products_to_be_restocked = []
	for product in products:
		if product.current_stock <= product.min_stock:
			++no_of_products_at_min_stock
			products_to_be_restocked.append(product)
	if no_of_products_at_min_stock >= constants.NO_OF_PRODUCTS_BEFORE_RESTOCK:
		for product in products_to_be_restocked:
			view.hq_stock_level_sync(product)