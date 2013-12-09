from retailserver import app
import requests
from flask import request, make_response, jsonify, json, render_template
import simplejson
import database
import constants
import tasks
import transactions

@app.route('/', methods=['DELETE', 'GET', 'POST', 'PUT'])
def index():
	print request.headers
	return make_response(jsonify({'barcode': "test", 'error' : False}), 200)

# @app.route('/trolley/price/', methods=['GET', ])
# def get_price():
# 	data=request.get_json
# 	trolley=request.get('trolley')

@app.route('/quantity/validate/<barcode>', methods=['POST', 'GET'])
def validate_quantity(barcode=None):
	quantity=request.args.get('quantity')
	print quantity
	if barcode is None:
		return make_response(jsonify({'error': 'Enter Product Name'}), 200)
	else:
		product = database.Product.query.get(barcode)
		available_stock = product.current_stock-product.min_stock
		if available_stock >= int(quantity):
			if int(quantity) > 0:
				return make_response(jsonify({'success': 'true'}), 200)
			else:
				return make_response(jsonify({'error' : 'Quantity must be positive'}), 200)
		else:
			return make_response(jsonify({'error': 'Quantity must be less than '+str(available_stock)}),200)



@app.route('/sync/', methods=['DELETE', 'POST', 'PUT'])
def product_sync():
	if request.method=="POST":
		data=request.get_json()
		barcode=data.get('barcode')
		MRP=data.get('product_MRP')
		bundle_unit=data.get('product_bundle_unit')
		product=database.Product.query.get(barcode)
		if product is None:
			new_product=database.Product(barcode=barcode, MRP=MRP, bundle_unit=bundle_unit)
			database.db.session.add(new_product)
			database.db.session.commit()
		else:
			product.MRP=MRP
			product.bundle_unit=bundle_unit
			product.adjust_price()
			database.db.session.commit()
		return make_response(jsonify({'barcode': data.get('barcode'), 'error' : False}), 200)
	elif request.method=="DELETE":
		data=request.get_json()
		barcode=data.get('barcode')
		print data
		product=database.Product.query.get(barcode)
		if product is not None:
			database.db.session.delete(product)
			database.db.session.commit()
			return make_response(jsonify({'barcode': data.get('barcode'), 'error' : False}), 200)
		else:
			return make_response(jsonify({'error': True}), 412)
	elif request.method=="PUT":
		data=request.get_json()
		print data
		barcode=data.get('barcode')
		MRP=data.get('product_MRP')
		bundle_unit=data.get('product_bundle_unit')
		product=database.Product.query.get(barcode)
		if product is None:
			new_product=database.Product(barcode=barcode, MRP=MRP, bundle_unit=bundle_unit)
			database.db.session.add(new_product)
			database.db.session.commit()	
		else:
			product.MRP=MRP
			product.bundle_unit=bundle_unit
			product.adjust_price()
			database.db.session.commit()
		return make_response(jsonify({'barcode': data.get('barcode'), 'error': False}), 200)
	else:
		return make_response(jsonify({'error': True}), 403)

def restock(product_obj):
	url = constants.HQ_SERVER_URL + "/restock/"
	data = product_obj.serialize
	headers = {'content-type' : 'application/json'}
	data['outlet_url'] = str(constants.RETAIL_SERVER_URL)
	data = simplejson.dumps(data, use_decimal=True)
	resp = requests.post(url, data=data, headers=headers)	
	if resp.status_code==200:
		product_obj.current_stock=product_obj.max_stock
		database.db.session.commit()

def hq_stock_level_sync(product_obj):
	url = constants.HQ_SERVER_URL + "/sync/"	
	data = product_obj.serialize()
	headers = {'content-type' : 'application/json'}
	data['outlet_url'] = str(constants.RETAIL_SERVER_URL)
	data = simplejson.dumps(data, use_decimal=True)
	resp = requests.put(url, data=data, headers=headers)
	print resp
	if resp.status_code == 200:
		print product_obj.max_stock
		print product_obj.current_stock
		product_obj.current_stock = product_obj.max_stock
		database.db.session.commit()

@app.route('/prices/adjust/', methods=['POST'])
def adjust_prices():
	tasks.adjust_prices()
	return make_response(jsonify({'error': False}), 200)

@app.route('/products/restock/', methods=['POST'])
def restock_products():
	tasks.restock()
	return make_response(jsonify({'error': False}), 200)

@app.route('/transactions/sync/', methods=['POST'])
def sync_transactions():
	tasks.sync_transactions()
	return make_response(jsonify({'error': False}), 200)

@app.route('/get/price/', methods=['POST'])
def return_trolley_price():
	items_list=request.get_json()
	price=transactions.calculate_price(items_list)
	return make_response(jsonify({'price': price}), 200)