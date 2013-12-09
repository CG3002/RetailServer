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

cash_reg = [ ]
dac_index = []
prev_cost = 0
prev_len = 0
stream_flag = 1
print_val = ''

reg = ['@r1']	
flag = 1
start_rec = 0
wrong_id = 0
start_count = 0
correct_id = 0
r_flag = 0
getting_barcode = 0
prod = 0
quan = 0
qty = ''
barcode = ''
total_price = 0
ack_flag = 0
cancel_transaction = 0
got_response = 0
timeout = time.time() + 3
language_flag = 0

pdu_update_flag = 0
oldtime = 0
print_flag = 0
ended_trans = 0
last_trans = []

def update_pdu():
	global pdu_update_flag, ser, pdu_list
	pdu_list=PriceDisplayUnit.query.all()
	for item in pdu_list:
		pdu = PriceDisplayUnit.query.get(item.pdu_id)
		if pdu is not None:
			ser.write('~')
			while 1:
				ack = ser.readline()
				if ack=='@0/':
					break
			products=database.Product.query.get(pdu.barcode)
			#raw_input("Press Enter to continue...")
			send_msg = '@'+item.pdu_id+str(pdu.barcode)+':$'+str("%.2f"%products.current_price)+'/'
			print send_msg
			ser.write(str(send_msg))
	
def print_receipt(tot_price, trans_id, cashier_id, amount_paid, amount_rem):
	global last_trans, canvas, base, values, currentprinter, canvas
	print str(tot_price)+' '+str(trans_id)+' '+str(cashier_id)+str(last_trans)
	#raw_input("Press Enter to continue...")
	canvas = canvas.Canvas("receipt.pdf", pagesize=letter)
	canvas.setLineWidth(.3)
	canvas.setFont('Helvetica', 12)

	canvas.drawString(30,750,'CASHIER ID: '+str(cashier_id))
	canvas.drawString(30,735,'TRANSACTION ID: '+str(trans_id))

	canvas.drawString(500,750,time.strftime("%d/%m/%Y"))
	canvas.line(480,747,580,747)
	 
	canvas.drawString(275,725,'TOTAL PRICE:')
	canvas.drawString(500,725,"$"+str(tot_price))
	canvas.line(378,723,580,723)
	 
	canvas.drawString(30,703,'PRODUCTS:')
	canvas.drawString(120,703,'<Barcode>')
	canvas.drawString(190,703,'<Quantity>')
	canvas.drawString(260,703,'<Price>')

	#items = ['10005058 2 24.00', '10005058 2 24.00']
	base = 683
	print last_trans
	for check in last_trans:
		values = check.split()
		print values
		#raw_input('print check')
		left= 120
		for value in values:
			canvas.drawString(left,base,str(value))
			left+=70
		base=base-30

	canvas.line(120,base,580,base)
	base-=30
	canvas.drawString(120,base,'AMOUNT PAID: $ %.2f'%amount_paid)
	canvas.line(120,base-10,580,base-10)
	base-=30
	canvas.drawString(120,base,'CHANGE: $ %.2f'%amount_rem)
	base-=30
	canvas.line(120,base-10,580,base-10)
	canvas.save()
	currentprinter = win32print.GetDefaultPrinter()
	if len(currentprinter):
		win32print.SetDefaultPrinter(currentprinter)
		win32api.ShellExecute(0, "print", 'receipt.pdf', None,  ".",  0)	
	threading.Timer(15, lambda: os.remove('receipt.pdf') ).start()
	
def event_stream():
	count = 0
	while True:
		gevent.sleep(2)
		yield 'data %s\n\n' % count
		count+=1

def event_barcode():
	global cash_reg,dac_index,prev_cost,prev_len,stream_flag,reg,flag,start_rec,wrong_id,start_count,correct_id,r_flag,getting_barcode,prod,quan,qty,barcode,total_price,ack_flag,cancel_transaction,got_response,timeout,print_val, oldtime, language_flag, ser, pdu_update_view, last_trans
	ser = serial.Serial(port=6, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_TWO, timeout=0.05) 
	ser.isOpen()
	pdu_update_view = 0
	trans_id = 0
	while True:
		pdu_timeout= time.time()+10
		for item in reg:
			send_pkg = item+'/'
			ser.write(send_pkg)
			print 'sending '+ send_pkg
			timeout = time.time()+5
			ser.flush() # empty write buffer
			print 'here'
			while flag :
			
				if got_response ==1 or time.time()> timeout:
					got_response =0
					break
				#ser.flush()
				print 'check'
				buffer = ser.readline()              # read one, blocking
				print buffer
			
				if buffer == '@0/':	#no response	
					got_response = 1
					print 'No data'
				
				elif buffer =='@0/@0/':
					got_response = 1
					print 'finished update'
				
				elif buffer =='$/':	#end transaction
					print 'got $'
					got_response = 1
					content = []
					print cash_reg
					for index in cash_reg:
						check = index.split()
						print check
						print str(check[0])+' '+str(check[1])
						info = {
							'barcode':  int(check[0]),
							'quantity': int(check[1])
						}
						content.append(info)
						print content
						value = transactions.add_transaction(content)
						if value>0:
							print 'Success '+ str(value)
							trans_id = value
						elif value==-1:
							print 'Invalid quantity'
						elif value==-2:
							print 'Invalid barcode'
						elif value==-3:
							print 'Database error'
					last_trans = cash_reg
					cash_reg = []
					ended_trans = 1
					ser.write('/')
					while 1:
						ack = ser.readline()
						if ack == '@0/' :
							break
			
				elif buffer == '?/': #cancel transaction
					got_response = 1
					cash_reg = [ ]
					ser.write('/')
					while 1:
						ack = ser.readline()
						if ack == '@0/' :
							break
				
				elif buffer == '!/': #change language
					got_response = 1
					if language_flag ==0:
						language_flag = 1
					else:
						language_flag = 0
					ser.write('/')
					while 1:
						ack = ser.readline()
						if ack == '@0/' :
							break
							
				elif len(buffer):	#price process
					if buffer[0] == '~':
						got_response =1
						barcode = buffer
						products = []
						products=database.Product.query.get(barcode[1:9])
						dup_barcode = 0
						if products is not None:
							for check_barcode in cash_reg:
								first_check = check_barcode.split()
								if first_check[0] == barcode[1:9]:
									dup_barcode = 1
									break
							if dup_barcode == 0:
								quantity = barcode[10:-1]
								quan_check = int(quantity)
								print str(products.current_stock)+' '+str(quantity)
								#raw_input("Press Enter to continue...")
								product_stock=database.Product.query.get(barcode[1:9])
								if (quan_check > product_stock.current_stock) or (quan_check == 0):
									if language_flag == 0:
										send_error='&0#P#R/'
									else:
										send_error='&0#@#B/'
									ser.write(send_error)
									while 1:
										ack = ser.readline()
										if ack == '@0/' :
											break
									break
								
								price = products.current_price
								if products.bundle_unit > 0:
									if quantity >= products.bundle_unit:
										price = price*0.9
								print price
								cash_reg.append(str(barcode[1:9])+' '+str(quantity)+' '+str(price))
								print cash_reg
								send_price = '&'
								send_price += str(int(math.ceil(price*100.0)))
								send_price+='/'
								print send_price
								ser.write(send_price)
								while 1:
									ack = ser.readline()
									if ack == '@0/' :
										break
								break
							else:
								if language_flag == 0:
									send_error='&0#P#Q/'
								else:
									send_error='&0#@#A/'
								ser.write(send_error)
								while 1:
									ack = ser.readline()
									if ack == '@0/' :
										break
						else:
							print 'barcode doesnt exist'
							barcode = ''
							if language_flag == 0:
								send_error='&0#P#Q/'
							else:
								send_error='&0#@#A/'
							ser.write(send_error)
							while 1:
								ack = ser.readline()
								if ack == '@0/' :
									break
					elif buffer[0] == '^':
						got_response = 1
						trolley = buffer[1:-1]
						print 'Trolley: '+ str(trolley)
						trolresponse= transactions.checkout_trolley(int(trolley))
						trolleyresp = trolresponse.split(':')
						trolprice = float(trolleyresp[1])
						trans_id = int(trolleyresp[0])
						send_trolley='+'
						sent_price = int(math.ceil(trolprice*100.0))
						if int(sent_price)==0:
							if language_flag == 0:
								sent_price='0#P#U'
							else:
								sent_price='0#@#E'
						send_trolley+=str(sent_price)
						send_trolley+='/'
						ser.write(send_trolley)
						print send_trolley
						items = transactions.get_trolley_items(trolley)
						print items
						list = []
						listitem = '0'
						if len(items):
							for item in items:
								barcode=item['barcode']
								quantity=item['quantity']
								product=database.Product.query.get(barcode)
								price = 'N.A.'
								if product is not None:
									price = product.current_price
								listitem = str(barcode)+' '+str(quantity)+' %.2f'%(price) 
								print listitem
						if listitem!='0':
							last_trans.append(str(listitem))
						print last_trans
						#raw_input('test')
						while 1:
							ack = ser.readline()
							if ack == '@0/' :
								break
					elif buffer[0] == '>':
						got_response = 1
						splitcheck = buffer.split(')',1)
						amount_p = splitcheck[0]
						amount_rem = splitcheck[1]
						amount_p= amount_p[1:]
						actual = []
						amount_paid = amount_p
						digit_flag = 1
						val = 7
						final =''
						while val>0:
							actual.append(str(amount_paid[val]))
							val-=1
						carry_over = 0
						for digit in actual:
							actdigit = ord(digit)-48
							print digit+' '+str(actdigit)
							if actdigit==10:
								final+='0'
								carry_over = 1
							else:
								if carry_over == 1:
									digitwithcarry = actdigit+1
									if digitwithcarry == 10:
										carry_over=1
										final+='0'
										continue
									else:
										final+=str(digitwithcarry)
										carry_over = 0
										continue
								final+=str(actdigit)
								carry_over = 0
						final = final[::-1]
						amount_rem = amount_rem[:-1]
						print str(int(final))+' '+str(int(amount_rem))
						a1 = float(int(final)/100.0)
						a2 = float(int(amount_rem)/100.0)
						tot_price = float(a1-a2)
						print_flag = 1
						ended_trans = 0
						if len(str(trans_id)):
							trans =  database.TransactionTimestamp.query.get(trans_id)
							if trans is not None:
								cash_id = trans.cashier_id
						print_receipt(tot_price, trans_id, cash_id, a1, a2)
						print str(tot_price)+' '+str(trans_id)+' '+str(cash_id)
						print buffer
						print last_trans
						#raw_input("Press Enter to continue...")
						trans_id = ''
						ser.write('/')
						while 1:
							ack = ser.readline()
							if ack == '@0/' :
								break
			barcode = ''
			got_response = 0
			if len(cash_reg) != prev_len:
				prev_len = len(cash_reg)
				if len(cash_reg)>0:
					current = str(cash_reg[len(cash_reg)-1])
					current_val = current.split()
					yield 'Barcode: %s  Quantity: %s Price: %.2f\n' % (current_val[0],current_val[1],float(current_val[2]))
			gevent.sleep(0.1)

		#today_date = time.time()
		today_date = datetime.date.today()
		print today_date
		#raw_input("Press Enter to continue...")
		if today_date != oldtime:
			oldtime = today_date
			update_pdu()
		
			#print receipt
			# if print_flag == 1:
				# print_receipt()
			#update pdu
			
		var = pdu_update_view
		print 'PDU FLAG:'+' '+str(var)
		if var==1:
			print 'updating explicitly'
			pdu_update_view = 0
			update_pdu()
		
@app.route('/pduupdate/', methods=['POST'])
def handle_data():
	global pdu_update_view 
	pdu_update_view = 1
	print 'reached here'
	url = "admin/viewpdu"
	return redirect(url)
				
@app.route('/my_event_source')
def sse_request():
    return Response(event_barcode(),mimetype='text/event-stream')

class TestView(BaseView):
    def __init__(self, *args, **kwargs):
        self._default_view = True
        super(TestView, self).__init__(*args, **kwargs)
        self.admin = Admin()

class MyView(BaseView):
	@expose('/')
	def page(self):
		#return TestView().render('sse.html')
		return Response(event_barcode(),mimetype='text/event-stream')

class PduView(BaseView):
    @expose('/')
    def index(self):
        return self.render('pdu.html')
 
class HomeView(AdminIndexView):
    @expose("/")
    def index(self):
        return Response(event_barcode(),mimetype='text/event-stream')
		
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
	admin.add_view(MyView(name="Cash Register", endpoint="cashreg"))
	admin.add_view(FunctionView(name="Regular Functions"))
	app.debug = True
	threading.Timer(0.25, lambda: requests.get('http://127.0.0.1:5000/admin/cashreg') ).start()
	threading.Timer(0.25, lambda: webbrowser.open_new_tab('http://127.0.0.1:5000/admin') ).start()
	app.run('127.0.0.1', 5000, threaded=True)
