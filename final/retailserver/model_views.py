'''
This file contains the Model Views for Flask admin
'''
from flask.ext.admin.contrib import sqla
from flask.ext.admin.model import typefmt

MY_DEFAULT_FORMATTERS = dict(typefmt.BASE_FORMATTERS)
MY_DEFAULT_FORMATTERS.update({
        type(None): typefmt.null_formatter
    })

class ProductAdmin(sqla.ModelView):
	can_create = False
	can_delete = False
	column_display_pk = True
	column_filters = ('barcode', 'max_discount', 'max_stock', 'min_stock', 'current_price', 'current_stock')
	form_columns = ['max_discount', 'max_stock', 'min_stock']

class TransactionDescAdmin(sqla.ModelView):
	can_create = False
	can_delete = False
	column_display_pk = True
	column_filters = ('transaction_id', 'barcode')

class TransactionStampAdmin(sqla.ModelView):
	can_create = False
	can_delete = False
	column_display_pk = True
	column_filters = ('transaction_id', 'cashier_id', 'timestamp')

class PriceDisplayUnitAdmin(sqla.ModelView):
	column_display_pk = True
	column_type_formatters = MY_DEFAULT_FORMATTERS
	form_columns = ['pdu_id', 'product']
	column_filters = ('pdu_id', 'barcode')