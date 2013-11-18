from retailserver import database
from retailserver import constants
import datetime
from retailserver import views
import time
from sqlalchemy import func
import requests
import simplejson

# date=datetime.date.today()
# for day in range(1,30):
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
