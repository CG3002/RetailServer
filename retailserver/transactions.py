import constants
import database
import datetime
import time


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
				if (product.current_stock - product.min_stock) >= 0:				
					product.current_stock = product.current_stock - quantity
					new_trans_description=database.TransactionDetails(transaction_id=new_transaction.transaction_id, barcode=barcode, quantity=quantity)
					database.db.session.add(new_trans_description)
					total_price += product.total_price(quantity)
				else:
					database.db.session.delete(new_transaction)
					database.db.session.commit()
					return "Invalid quantity"
			else:
				database.db.session.delete(new_transaction)
				database.db.session.commit()
				return "Invalid barcode/quantity"
		except:
			database.db.session.delete(new_transaction)
			database.db.session.commit()
			return "Error while creating transaction"
	database.db.session.commit()
	return total_price


