import time
import serial
import random
from retailserver import database
from retailserver import transactions

ser = serial.Serial(port=6, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_TWO, timeout=0.05) 
ser.isOpen()
connected=False

cash_reg = [ 0 ]
dac_index = []

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

print 'start transmission'
while 1 :

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
		
			if buffer == '@0/':	
				got_response = 1
				print 'No data'
			
			elif buffer =='$/':
				print 'got $'
				got_response = 1
				zero_flag = 0
				content = []
				for index in cash_reg:
					if  zero_flag == 0 :
						zero_flag = 1
					else:
						qty = index[10:]
						qty = qty[:-1]
						barcode = index[1:9]
						print str(barcode) + str(qty)
						info = {
							'barcode':  int(barcode),
							'quantity': int(qty)
						}
						content.append(info)
						print content
						value = transactions.add_transaction(content)
						if value>0:
							print 'Success '+ str(value)
						elif value==-1:
							print 'Invalid quantity'
						elif value==-2:
							print 'Invalid barcode'
						elif value==-3:
							print 'Database error'
				ser.write('/')
				while 1:
					ack = ser.readline()
					if ack == '@0/' :
						break
			elif buffer == '%/'
				got_response = 1
				cash_reg = cash_reg[:-1]
				ser.write('/')
				while 1:
					ack = ser.readline()
					if ack == '@0/' :
						break
						
			elif len(buffer):
				if buffer[0] == '~':
					got_response =1
					barcode = buffer
					products=database.Product.query.get(barcode[1:9])
					if products is not None:
						print 'at least one product'
						quantity = barcode[10:]
						quantity = quantity[:-1]
						print 'quantity = '+ quantity
						price = products.total_price(int(quantity))
						print price
						
						cash_reg.append(barcode)
						print cash_reg
						total_price = cash_reg[0]
						total_price+=price
						cash_reg[0] = total_price
						print cash_reg
						barcode = ''
						
						send_price = '&'
						total_price *= 100
						hundred_thousand_place = int(total_price/10000000)
						total_price-=hundred_thousand_place*10000000
						ten_thousand_place = int(total_price/1000000) 
						total_price-=ten_thousand_place*1000000
						thousands_place = int(total_price/100000)
						print 'T '+str(thousands_place)
						total_price-= thousands_place*100000
						hundreds_place = int(total_price/10000)
						total_price-= hundreds_place*10000
						tens_place = int(total_price/1000)
						total_price-= tens_place*1000
						ones_place = int(total_price/100)
						total_price-= ones_place*100
						point_1_place = int(total_price/10)
						total_price-= point_1_place*10
						point_2_place = int(total_price)
						print hundred_thousand_place
						send_price+=str(hundred_thousand_place)
						print ten_thousand_place
						send_price+=str(ten_thousand_place)
						print thousands_place
						send_price+=str(thousands_place)
						print hundreds_place
						send_price+=str(hundreds_place)
						print tens_place
						send_price+=str(tens_place)
						print ones_place
						send_price+=str(ones_place)
						print point_1_place
						send_price+=str(point_1_place)
						print point_2_place
						send_price+=str(point_2_place)
						print send_price
						send_price+='#'
						#hundred - 28
						#thousand - 29
						if(hundred_thousand_place):
							send_price+= str(hundred_thousand_place)+'#L#'
						if(ten_thousand_place>1):
							if ten_thousand_place == 2: send_price+='D#'
							elif ten_thousand_place == 3: send_price+='E#'
							elif ten_thousand_place == 4: send_price+='F#'
							elif ten_thousand_place == 5: send_price+='G#'
							elif ten_thousand_place == 6: send_price+='H#'
							elif ten_thousand_place == 7: send_price+='I#'
							elif ten_thousand_place == 8: send_price+='J#'
							elif ten_thousand_place == 9: send_price+='K#'
							
							if (thousands_place):
								send_price+=str(thousands_place)+'#'
						elif ten_thousand_place==1:	
							if thousands_place == 0: send_price+=':#'
							if thousands_place == 1: send_price+=';#'
							if thousands_place == 2: send_price+='<#'
							if thousands_place == 3: send_price+='=#'
							if thousands_place == 4: send_price+='>#'
							if thousands_place == 5: send_price+='?#'
							if thousands_place == 6: send_price+='@#'
							if thousands_place == 7: send_price+='A#'
							if thousands_place == 8: send_price+='B#'
							if thousands_place == 9: send_price+='C#'
						else:
							if (thousands_place):
								send_price+= str(thousands_place)+'#M#'
						if (hundreds_place):
							send_price+= str(hundreds_place)+'#L#'
						# 20-20 30-21 40-22 50-23 60-24 70-25 80-26 90-27
						if (tens_place>1):
							if tens_place == 2: send_price+='D#'
							elif tens_place == 3: send_price+='E#'
							elif tens_place == 4: send_price+='F#'
							elif tens_place == 5: send_price+='G#'
							elif tens_place == 6: send_price+='H#'
							elif tens_place == 7: send_price+='I#'
							elif tens_place == 8: send_price+='J#'
							elif tens_place == 9: send_price+='K#'
							
							if (ones_place):
								send_price+=str(ones_place)+'#'
						elif tens_place==1:	
							if ones_place == 0: send_price+=':#'
							if ones_place == 1: send_price+=';#'
							if ones_place == 2: send_price+='<#'
							if ones_place == 3: send_price+='=#'
							if ones_place == 4: send_price+='>#'
							if ones_place == 5: send_price+='?#'
							if ones_place == 6: send_price+='@#'
							if ones_place == 7: send_price+='A#'
							if ones_place == 8: send_price+='B#'
							if ones_place == 9: send_price+='C#'
							
						# and x cents
							
						if (point_1_place>1):
							if point_1_place == 2: send_price+='D#'
							elif point_1_place == 3: send_price+='E#'
							elif point_1_place == 4: send_price+='F#'
							elif point_1_place == 5: send_price+='G#'
							elif point_1_place == 6: send_price+='H#'
							elif point_1_place == 7: send_price+='I#'
							elif point_1_place == 8: send_price+='J#'
							elif point_1_place == 9: send_price+='K#'
							
							if (point_2_place):
								send_price+=str(point_2_place)+'#'
						elif point_1_place==1:	
							if point_2_place == 0: send_price+=':#'
							if point_2_place == 1: send_price+=';#'
							if point_2_place == 2: send_price+='<#'
							if point_2_place == 3: send_price+='=#'
							if point_2_place == 4: send_price+='>#'
							if point_2_place == 5: send_price+='?#'
							if point_2_place == 6: send_price+='@#'
							if point_2_place == 7: send_price+='A#'
							if point_2_place == 8: send_price+='B#'
							if point_2_place == 9: send_price+='C#'
						else:
							send_price+='0#'
						
						send_price = send_price[:-1]
						send_price+='/'
						print send_price
						ser.write(send_price)
						
						while 1:
							ack = ser.readline()
							if ack == '@0/' :
								break
						break
					else:
						print 'barcode doesnt exist'
						barcode = ''
						while 1:
							ack = ser.readline()
							if ack == '@0/' :
								break
		barcode = ''
		got_response = 0