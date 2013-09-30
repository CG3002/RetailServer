from retailserver import app, database, transactions, views
from retailserver.database import db, Product, TransactionTimestamp, TransactionDetails, PriceDisplayUnit
from retailserver.model_views import ProductAdmin, TransactionDescAdmin, TransactionStampAdmin, PriceDisplayUnitAdmin
from flask.ext.admin import Admin
from flask.ext.admin import BaseView, expose, AdminIndexView
from reportlab.pdfgen import canvas  
from reportlab.lib.units import cm 
import gevent
import serial, time
import gevent.monkey
from gevent.pywsgi import WSGIServer
gevent.monkey.patch_all()
from flask import Flask, request, Response, render_template, redirect
import webbrowser, threading, requests, datetime, math, os, win32print, win32api
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import newreg
		
@app.route('/pduupdate/', methods=['POST'])
def handle_data():
	newreg.pdu_update_view = 1
	print 'reached here'
	url = "admin/viewpdu"
	return redirect(url)

class PduView(BaseView):
    @expose('/')
    def index(self):
        return self.render('pdu.html')
		
class FunctionView(BaseView):
        @expose('/')
        def index(self):
			return self.render('functions.html')

if __name__ == "__main__":
	
	app.secret_key = os.urandom(24)
	#create DB
	db.create_all()

	#create admin
	admin = Admin(app, name="Retail Server")

	#add model views
	admin.add_view(ProductAdmin(Product, db.session))
	admin.add_view(TransactionDescAdmin(TransactionDetails, db.session))
	admin.add_view(TransactionStampAdmin(TransactionTimestamp, db.session))
	admin.add_view(PriceDisplayUnitAdmin(PriceDisplayUnit, db.session, category="Price Display Unit", endpoint="viewpdu", name='View'))
	admin.add_view(PduView(category="Price Display Unit", endpoint="updatepdu", name='Update'))
	admin.add_view(FunctionView(name="Regular Functions"))
	app.debug = True
	threading.Timer(0.25, lambda: webbrowser.open_new_tab('http://127.0.0.1:5000/admin') ).start()
	app.run('127.0.0.1', 5000, threaded=True)
