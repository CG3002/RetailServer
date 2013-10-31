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
	for item in items_list:
		try:
			barcode=item['barcode']
			quantity=item['quantity']
			product=database.Product.query.get(barcode)
			if product is not None:
				new_trans_description=database.TransactionDescription(new_transaction.transaction_id, barcode, quantity)
				database.db.session.add(new_trans_description)
			else:
				database.db.session.delete(new_transaction)
				database.db.session.commit()
				return "Product does not exist"
		except:
			database.db.session.delete(new_transaction)
			database.db.session.commit()
			return "Error while creating transaction"
	database.db.session.commit()


