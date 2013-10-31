from retailserver import app
from flask.ext.sqlalchemy import SQLAlchemy
import time
import os
import views
import datetime

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/hari/retailtest.db'
# app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = os.urandom(24)
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

	def __init__(self, barcode, MRP, discount=0, max_discount=0, current_price=None, current_stock=0, max_stock=0, min_stock=0, bundle_unit=0, date_last_restock=None):
		self.barcode=barcode
		self.MRP=MRP
		if current_price is None:
			self.current_price=self.MRP
		else: 
			self.current_price=current_price
		if date_last_restock is None:
			self.date_last_restock=datetime.datetime.now()
		else:
			self.date_last_restock=date_last_restock
		self.discount=discount
		self.max_discount=max_discount
		self.current_stock=current_stock
		self.max_stock=max_stock
		self.min_stock=min_stock
		self.bundle_unit=bundle_unit

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



