import constants
import database
import datetime
import time
import simplejson
import requests

def add_transaction(items_list):
	'''
	Expects a list of dictionaries in the following format
	[
		{ 
			'barcode' : something,
			'quantity' : something
		},
		{
			'barcode' : something,
			'quantity' : something
		}
	]
	'''
	new_transaction=database.TransactionTimestamp()
	database.db.session.add(new_transaction)
	database.db.session.commit()
	total_price = 0
	for item in items_list:
		try:
			barcode=item['barcode']
			quantity=item['quantity']
			product=database.Product.query.get(barcode)
			if product is not None and quantity > 0:
				if (product.current_stock - quantity) >= 0:				
					product.current_stock = product.current_stock - quantity
					database.db.session.commit()
					new_trans_description=database.TransactionDetails(transaction_id=new_transaction.transaction_id, barcode=barcode, quantity=quantity)
					database.db.session.add(new_trans_description)
					total_price += product.total_price(quantity)
				else:
					database.db.session.delete(new_transaction)
					database.db.session.commit()
					return -1
			else:
				database.db.session.delete(new_transaction)
				database.db.session.commit()
				return -2
		except:
			database.db.session.delete(new_transaction)
			database.db.session.commit()
			return -3
	database.db.session.commit()
	return new_transaction.transaction_id

def checkout_trolley(trolley_id):
	url=constants.HQ_SERVER_URL+"/get/trolley/"
	data=simplejson.dumps({'trolley': trolley_id})
	headers = {'content-type' : 'application/json'}
	print data
	resp=requests.post(url, data=data, headers=headers)
	items_list=resp.json()
	if not isinstance(items_list, list):
		return -1
	print items_list
	new_transaction=database.TransactionTimestamp()
	database.db.session.add(new_transaction)
	database.db.session.commit()
	total_price = 0
	for item in items_list:
		try:
			barcode=item['barcode']
			quantity=item['quantity']
			product=database.Product.query.get(barcode)
			if product is not None and quantity > 0:
				if (product.current_stock - quantity) >= 0:				
					product.current_stock = product.current_stock - quantity
					database.db.session.commit()
					new_trans_description=database.TransactionDetails(transaction_id=new_transaction.transaction_id, barcode=barcode, quantity=quantity)
					database.db.session.add(new_trans_description)
					total_price += product.total_price(quantity)
				else:
					database.db.session.delete(new_transaction)
					database.db.session.commit()
					return -1
			else:
				database.db.session.delete(new_transaction)
				database.db.session.commit()
				return -2
		except:
			database.db.session.delete(new_transaction)
			database.db.session.commit()
			return -3
	database.db.session.commit()
	return total_price

def calculate_price(items_list):
	total_price=0
	print items_list
	for item in items_list:
		barcode=item['barcode']
		quantity=item['quantity']
		product=database.Product.query.get(barcode)
		if product is not None and quantity > 0:
			if (product.current_stock - quantity) >= 0:				
				total_price += product.total_price(quantity)
			else:
				return -1
		else:
			return -2
	print total_price	
	return total_price

def get_trolley_items(trolley_id):
	url=constants.HQ_SERVER_URL+"/get/trolley/"
	data=simplejson.dumps({'trolley': trolley_id})
	headers = {'content-type' : 'application/json'}
	print data
	resp=requests.post(url, data=data, headers=headers)
	items_list=resp.json()
	if not isinstance(items_list, list):
		return -1
	return items_list


	

