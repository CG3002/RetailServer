from retailserver import app
from flask.ext.sqlalchemy import SQLAlchemy
import time
import views
import datetime
import math
import constants
import requests
import simplejson

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/hari/retailtest.db'
# app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Product(db.Model):
	__tablename__="Retail Products"
	barcode=db.Column(db.Integer, primary_key=True)
	MRP=db.Column(db.Float)
	current_price=db.Column(db.Float)
	max_discount=db.Column(db.Integer)
	discount=db.Column(db.Integer)
	current_stock=db.Column(db.Integer)
	max_stock=db.Column(db.Integer)
	min_stock=db.Column(db.Integer)
	bundle_unit=db.Column(db.Integer)
	date_last_restock=db.Column(db.DateTime)

	def total_price(self, quantity=0):
		'''
		Returns total price of n items of product after applying discounts
		'''
		if self.bundle_unit > 0:
			if quantity >= self.bundle_unit:
				return quantity*self.current_price*0.9
			else:
				return quantity*self.current_price
		else:
			return quantity*self.current_price

	def adjust_price(self):
		'''
		Adjusts price based on stock level
		'''
		ratio_to_be_raised=0
		current_date=datetime.datetime.now()
		last_restock_date=self.date_last_restock
		difference=current_date - last_restock_date
		if difference.days != 0:
			exp_factor=(10/difference.days)
		elif difference.days == 0:
			exp_factor=10
		if self.current_stock > self.min_stock:
			ratio_to_be_raised = (self.current_stock-self.min_stock)/float(self.max_stock-self.min_stock)
		new_discount = self.max_discount * (ratio_to_be_raised ** exp_factor)
		self.discount=math.floor(new_discount)
		self.current_price=self.MRP - self.MRP * (self.discount/100)

	@property
	def product_name(self):
		url=constants.HQ_SERVER_URL+"/product/name/"
		payload={'barcode': self.barcode}
		headers = {'content-type' : 'application/json'}
		resp=requests.post(url, data=simplejson.dumps(payload), headers=headers)
		return resp.json().get('product_name')

	def __init__(self, **kwargs):
		self.barcode=kwargs.get('barcode')
		self.MRP=kwargs.get('MRP')
		self.date_last_restock=kwargs.get('date_last_restock',datetime.datetime.now())
		self.max_discount=kwargs.get('max_discount', 20)
		self.max_stock=kwargs.get('max_stock', 500)
		self.current_stock=kwargs.get('current_stock', self.max_stock)
		self.min_stock=kwargs.get('min_stock', 50)
		self.bundle_unit=kwargs.get('bundle_unit', 0)
		self.adjust_price()

	def __repr__(self):
		return '<Retail Product Barcode: %r Min_Stock: %r Max_Stock: %r Discount: %r' % (self.barcode, self.min_stock, self.max_stock, self.discount)

	def serialize(self):
		return {
		'barcode' : self.barcode,
		'max_stock' : self.max_stock,
		'min_stock' : self.min_stock
		}

class TransactionTimestamp(db.Model):
	__tablename__="Transaction Timestamp"
	transaction_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
	timestamp=db.Column(db.Integer)
	cashier_id=db.Column(db.Integer)

	def __init__(self, **kwargs):
		date=datetime.date.today()
		date_timestamp = time.mktime(date.timetuple())
		self.transaction_id = kwargs.get('transaction_id')
		self.timestamp = kwargs.get('timestamp', date_timestamp)
		self.cashier_id=kwargs.get('cashier_id', 1)

	def __repr__(self):
		return '<Transaction ID: %r>' % (self.transaction_id)


class TransactionDetails(db.Model):
	__tablename__="Transaction Description"
	transaction_id=db.Column(db.Integer, db.ForeignKey('Transaction Timestamp.transaction_id'), primary_key=True)
	barcode=db.Column(db.Integer, primary_key=True)
	quantity=db.Column(db.Integer)
	transaction=db.relationship('TransactionTimestamp',
		backref=db.backref('transactionID', lazy='joined'))

	def __init__(self, **kwargs):
		self.transaction_id = kwargs.get('transaction_id')
		self.barcode = kwargs.get('barcode')
		self.quantity = kwargs.get('quantity', 1)

	def __repr__(self):
		return '<Transaction ID: %r Barcode: %r>' % (self.transaction_id, self.barcode)

class PriceDisplayUnit(db.Model):
	__tablename__="Price Display Units"
	pdu_id=db.Column(db.String(100), primary_key=True)
	barcode=db.Column(db.Integer, db.ForeignKey('Retail Products.barcode', ondelete='SET NULL'), nullable=False)
	product=db.relationship('Product',
		backref=db.backref('pdu_assoc', lazy='dynamic'))

	@property
	def price(self):
		return self.product.current_price

	def __init__(self, **kwargs):
		self.pdu_id = kwargs.get('pdu_id')
		self.barcode = kwargs.get('barcode')

	def __repr__(self):
		return 'PDU ID: %r' % (self.pdu_id)





