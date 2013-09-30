import time

actual = []
amount_paid = '8BBBBB9:'
digit_flag = 1
val = 7
final =''
while val>=0:
	actual.append(str(amount_paid[val]))
	val-=1
carry_over = 0
for digit in actual:
	actdigit = ord(digit)-48
	print digit+' '+str(actdigit)
	if actdigit>=10:
		if carry_over ==1:
			actdigit+=1
		stringact = str(actdigit)
		final+=stringact[1]
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
print final

if (int(time.strftime("%H")) >21):
	print 'works'
quantity=''
if quantity!='':
	quan_check = int(quantity)
	print quan_check