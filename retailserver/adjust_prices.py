import database
import constants
import datetime
import views
import math

def adjust_prices():
	products=database.Product.query.all()
	for product in products:
		current_date=datetime.datetime.now()
		last_restock_date=product.date_last_restock
		difference=current_date - last_restock_date
		if difference.days != 0:
			exp_factor=(10/difference.days)
		elif difference.days == 0:
			exp_factor=10
		ratio_to_be_raised = (product.current_stock-product.min_stock)/float(product.max_stock-product.min_stock)
		print ratio_to_be_raised
		new_discount = product.max_discount * (ratio_to_be_raised ** exp_factor)
		product.discount=math.floor(new_discount)
		database.db.session.commit()
		views.hq_stock_level_sync(product)


