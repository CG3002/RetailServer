from retailserver import database

prices=database.PriceDisplayUnit.query.all()
for price in prices:
	print " price = %.2f" price.price()