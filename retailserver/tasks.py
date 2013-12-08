import database
import constants
import datetime
import views
import time
from sqlalchemy import func
import requests
import simplejson
from retailserver import celery

# date=datetime.date.today()
# for day in range(1,30):

@celery.task
def sync_transactions():
	date=datetime.date.today()
	timestamp=time.mktime(date.timetuple())
	payload = {}
	payload['outlet_url'] = str(constants.RETAIL_SERVER_URL)
	payload['history'] = []
	temp_dict = {'barcode': 0, 'quantity': 0, 'timestamp' : timestamp, 'total_revenue' : 0}
	for barcode, quantity in database.db.session.query(database.TransactionDetails.barcode, func.sum(database.TransactionDetails.quantity)).\
											join(database.TransactionTimestamp).\
											filter(database.TransactionTimestamp.timestamp==timestamp).\
											group_by(database.TransactionDetails.barcode).all():
		
		transactions_product=database.db.session.query(database.TransactionDetails).\
											join(database.TransactionTimestamp).\
											filter(database.TransactionTimestamp.timestamp==timestamp).\
											filter(database.TransactionDetails.barcode==barcode).\
											order_by(database.TransactionDetails.barcode).all()

		total_price = 0
		for transaction in transactions_product:
			product = database.Product.query.get(transaction.barcode)
			total_price += product.total_price(transaction.quantity)
		temp_dict['total_revenue'] = "%.2f" % total_price
		temp_dict['barcode'] = barcode
		temp_dict['quantity'] = quantity
		payload['history'].append(temp_dict.copy())
	headers = {'content-type' : 'application/json'}
	print payload
	data = simplejson.dumps(payload)
	url = constants.HQ_SERVER_URL + "/transactions/sync/"
	resp = requests.post(url, data=data, headers=headers)

@celery.task
def adjust_prices():
	products=database.Product.query.all()
	print "Hi"

	for product in products:
		print product.barcode
		product.adjust_price()
		database.db.session.commit()

@celery.task
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