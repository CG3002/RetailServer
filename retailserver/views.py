from retailserver import app
import requests
from flask import request, make_response, jsonify, json
import simplejson
import database
import constants

@app.route('/sync/', methods=['DELETE', 'POST', 'PUT'])
def product_sync():
	if request.method=="POST":
		data=request.get_json()
		barcode=data.get('barcode')
		MRP=data.get('product_MRP')
		bundle_unit=data.get('bundle_unit')
		product=database.Product.query.get(barcode)
		if product is None:
			new_product=database.Product(barcode=barcode, MRP=MRP, bundle_unit=bundle_unit)
			database.db.session.add(new_product)
			database.db.session.commit()
		else:
			product.MRP=MRP
			product.bundle_unit=bundle_unit
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
		bundle_unit=data.get('bundle_unit')
		product=database.Product.query.get(barcode)
		if product is None:
			new_product=database.Product(barcode=barcode, MRP=MRP, bundle_unit=bundle_unit)
			database.db.session.add(new_product)
			database.db.session.commit()	
		else:
			product.MRP=MRP
			product.bundle_unit=bundle_unit
			database.db.session.commit()
		return make_response(jsonify({'barcode': data.get('barcode'), 'error': False}), 200)
	else:
		return make_response(jsonify({'error': True}), 403)		


def hq_stock_level_sync(product_obj, db_action):
	if db_action == 'update':
		url = constants.HQ_SERVER_URL + "/sync/"	
		data = product_obj.serialize()
		headers = {'content-type' : 'application/json'}
		data['outlet_url'] = str(request.url_root)
		data = simplejson.dumps(data, use_decimal=True)
		resp = requests.put(url, data=data, headers=headers)
		print resp.text
