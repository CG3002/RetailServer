from retailserver import app
import requests
from flask import request, make_response, jsonify
import database

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
	if request.method=="DELETE":
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
	if request.method=="PUT":
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
		return make_response(jsonify({'barcode': data.get('barcode'), 'error': False}), 200)			





