'''
This file contains the Model Views for Flask admin
'''
from flask.ext.admin.contrib import sqla

class ProductAdmin(sqla.ModelView):
	can_create = False
	can_delete = False
	column_display_pk = True
	column_filters = ('barcode', )
	form_columns = ['max_discount', 'current_price', 'current_stock', 'max_stock', 'min_stock']

class TransactionDescAdmin(sqla.ModelView):
	can_create = False
	can_delete = False
	column_display_pk = True
	column_filters = ('transaction_id', 'barcode')

class TransactionStampAdmin(sqla.ModelView):
	can_create = False
	can_delete = False
	column_display_pk = True
	column_filters = ('transaction_id', 'cashier_id')