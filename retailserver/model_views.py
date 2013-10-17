'''
This file contains the Model Views for Flask admin
'''
from flask.ext.admin.contrib import sqla

class ProductAdmin(sqla.ModelView):
	can_create = False
	column_display_pk = True
	form_columns = ['discount', 'current_price', 'current_stock', 'max_stock', 'min_stock']