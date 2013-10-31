from retailserver import database
from retailserver import constants
import datetime
from retailserver import views
import time
from sqlalchemy import func
import requests
import simplejson

# date=datetime.date.today()
for day in range(1,31):
	date=datetime.date(2013,9,day)
	timestamp=time.mktime(date.timetuple())
	payload = {}
	payload['outlet_url'] = str(constants.RETAIL_SERVER_URL)
	payload['history'] = []
	temp_dict = {'barcode': 0, 'quantity': 0, 'timestamp' : timestamp}
	for barcode, quantity in database.db.session.query(database.TransactionDetails.barcode, func.sum(database.TransactionDetails.quantity)).\
											join(database.TransactionTimestamp).\
											filter(database.TransactionTimestamp.timestamp==timestamp).\
											group_by(database.TransactionDetails.barcode).all():
		temp_dict['barcode'] = barcode
		temp_dict['quantity'] = quantity
		payload['history'].append(temp_dict.copy())
	headers = {'content-type' : 'application/json'}
	data = simplejson.dumps(payload)
	url = constants.HQ_SERVER_URL + "/transactions/sync/"
	resp = requests.post(url, data=data, headers=headers)
	