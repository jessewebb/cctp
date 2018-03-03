cctp
====

Credit Card Transaction Parser

1. Copy transactions from online banking
2. Save in a new file  
`./transactions.txt`
3. Run the program  
`python cctp.py`
4. The program generates a new tab-delimited file  
`./output.txt`

Example Input:
```
Feb 4, 2018	PAYMENT THANK YOU/PAIEMEN T MERCI 
4500********1234	
$200.00
Jan 3, 2018	Foreign Currency Transactions TAXI SVC LAS VEGAS LAS VEGAS, NV 8.70 USD @ 1.234567 
4500********1234	
−$10.74
Jan 2, 2018	Retail and Grocery SOBEYS #5555 CITY, SK 
4500********5678	
−$98.76
Jan 1, 2018	Personal & Household Expenses Amazon.ca AMAZON.CA, CA 
4500********1234	
−$100.23
```

Example Output:
```
Transactions
============
date	amount	card	location	category	conversion
2018-01-01	100.23	4500********1234	Amazon.ca AMAZON.CA, CA	Personal & Household Expenses	
2018-01-02	98.76	4500********5678	SOBEYS #5555 CITY, SK	Retail and Grocery	
2018-01-03	10.74	4500********1234	TAXI SVC LAS VEGAS, NV	Foreign Currency Transactions	8.70 USD @ 1.234567

Payments
========
date	amount	card
2018-02-04	200.0	4500********1234
```
