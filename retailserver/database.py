from retailserver import app
from flask.ext.sqlalchemy import SQLAlchemy, before_models_committed
import time
import os
import views

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/hari/retailtest.db'
# app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = os.urandom(24)
db = SQLAlchemy(app)

class Product(db.Model):
	__tablename__="Retail Products"
	barcode=db.Column(db.Integer, primary_key=True)
	discount=db.Column(db.Integer)
	current_stock=db.Column(db.Integer)
	max_stock=db.Column(db.Integer)
	min_stock=db.Column(db.Integer)
	bundle_unit=db.Column(db.Integer)

	def __init__(self, barcode, discount=0, current_stock=0, max_stock=0, min_stock=0, bundle_unit=0):
		self.barcode=barcode
		self.discount=discount
		self.current_stock=current_stock
		self.max_stock=max_stock
		self.min_stock=min_stock
		self.bundle_unit=bundle_unit

	def __repr__(self):
		return '<Retail Product Barcode: %r Min_Stock: %r Max_Stock: %r Discount: %r' % (self.barcode, self.min_stock, self.max_stock, self.discount)
