'''
Python script for inserting Product objects from Inventory files
'''
from retailserver import database
import codecs, time, datetime
# file_object=codecs.open("hqserver/Inventory_5000.txt", 'r', 'utf-8')
# for line in file_object:
# 	line_split=line.split(':')
# 	product_name=line_split[0]
# 	category=line_split[1]
# 	manufacturer_name=line_split[2]
# 	barcode=line_split[3]
# 	product_MRP=line_split[4]
# 	product_bundle_unit=line_split[7]
# 	product=database.Product(barcode=barcode, product_name=product_name, category=category, 
# 					manufacturer_name=manufacturer_name, product_MRP=product_MRP, product_bundle_unit=product_bundle_unit)
# 	database.db.session.add(product)
# 	database.db.session.commit()
# file_object=codecs.open("Trans_1000_20_9_26223.txt", 'r', 'utf-8')
# for line in file_object:
# 	line_split=line.split(':')
# 	transaction_id=line_split[0]
# 	cashier_id=line_split[1]
# 	barcode=line_split[3]
# 	quantity=line_split[4]
# 	date=line_split[5].strip()
# 	timestamp=time.mktime(datetime.datetime.strptime(date, "%d/%m/%Y").timetuple())
# 	temp=database.TransactionTimestamp.query.get(transaction_id)
# 	if temp is None:
# 		new_transaction_timestamp=database.TransactionTimestamp(transaction_id=transaction_id, cashier_id=cashier_id, timestamp=timestamp)
# 		database.db.session.add(new_transaction_timestamp)
# 		database.db.session.commit()
# 	else:
# 		continue

file_object=codecs.open("Trans_1000_20_9_26223.txt", 'r', 'utf-8')
for line in file_object:
	line_split=line.split(':')
	transaction_id=line_split[0]
	cashier_id=line_split[1]
	barcode=line_split[3]
	quantity=line_split[4]
	date=line_split[5].strip()
	temp=time.mktime(datetime.datetime.strptime(date, "%d/%m/%Y").timetuple())
	timestamp=temp*100
	new_transaction_detail=database.TransactionDetails(transaction_id=transaction_id, barcode=barcode, quantity=quantity)
	database.db.session.add(new_transaction_detail)
	database.db.session.commit()

