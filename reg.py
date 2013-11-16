import time
import serial
from retailserver import database
import time

ser = serial.Serial(port=6, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_TWO, timeout=0) 
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

print 'start transmission'
while 1 :
	for item in reg:
		send_pkg = item+'/'
		ser.write(send_pkg)
		print 'sending '+ send_pkg
		while flag :
		
			# start_count += 1
			ser.flush() # empty write buffer
			buffer = ser.read()	#blocking call
			if buffer.isspace():
				print 'received' + buffer

			if buffer == '~':
				getting_barcode = 1
				
			if getting_barcode == 1 and buffer!='/':
				barcode+=buffer
					
			if buffer == '/' :
				print 'end round'
				if start_rec !=1:
					flag = 0
					quan = 0
					getting_barcode = 0
					print 'barcode =' +barcode
					products=database.Product.query.get(barcode[1:9])
					if products is not None:
						price = products.total_price(int(barcode[10:]))
						print price
						
						cash_reg.append(barcode)
						print cash_reg
						total_price = cash_reg[0]
						total_price+=price
						cash_reg[0] = total_price
						print cash_reg
						
						send_price = '&'
						total_price *= 100
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
						# send_price+='#'
						# #hundred - 28
						# #thousand - 29
						# if (thousands_place):
							# send_price+= str(thousands_place)+'#29#'
						# if (hundreds_place):
							# send_price+= str(hundreds_place)+'#28#'
						# # 20-20 30-21 40-22 50-23 60-24 70-25 80-26 90-27
						# if (tens_place>1):
							# send_price+='2'+str(tens_place-2)+'#'
							# if (ones_place):
								# send_price+=str(ones_place)+'#'
						# elif tens_place==1:	
							# send_price+=str(ones_place+1)+'#'
							
						# # and x cents
						# if (point_1_place>1):
							# send_price+='2'+str(point_1_place-2)+'#'
							# if (point_2_place):
								# send_price+=str(point_2_place)+'#'
						# elif point_1_place==1:	
							# send_price+=str(point_2_place+1)+'#'
						# else:
							# send_price+='0#'
						
						# send_price = send_price[:-1]
						send_price+='/'
						print send_price
						ser.write(send_price)
						
						ack_flag = 1
						ack_rec = 0 
						ack_end = 0
						while ack_flag:
							ack = ser.read()
							if ack == '@' :
								ack_rec = 1
							if (ack_rec == 1 and ack =='0'):
								ack_end = 1
								ack_rec = 0
							if ack_end == 1 and ack =='/':
								ack_flag = 0
						break
					else:
						#barcode doesnt exist
						barcode_ne_msg = '&!/'
						ser.write(barcode_ne_msg)
						ack_flag = 1
						ack_rec = 0 
						ack_end = 0
						while ack_flag:
							ack = ser.read()
							if ack == '@' :
								ack_rec = 1
							if (ack_rec == 1 and ack =='0'):
								ack_end = 1
								ack_rec = 0
							if ack_end == 1 and ack =='/':
								ack_flag = 0
						break
				
				else:
					time.sleep(2)
					break
					
			if buffer == '@' :
				start_rec = 1
			
			if (start_rec == 1 and buffer =='0'):
				print 'No data'
				
		start_rec = 0
		wrong_id = 0
		flag = 1
		start_count = 0
		barcode = ''