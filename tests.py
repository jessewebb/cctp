# coding: utf-8
""" Tests for Module: cctp """

import datetime
import unittest

import cctp


class TransactionTests(unittest.TestCase):

    def test_eq(self):
        tx1 = cctp.Transaction(datetime.date(1999, 10, 31), "7890********1111", "PAYMENT", None, 123.45, None)
        tx2 = cctp.Transaction(datetime.date(1999, 10, 31), "7890********1111", "PAYMENT", None, 123.45, None)
        self.assertEqual(tx1, tx2)

        tx1 = cctp.Transaction(datetime.date(2018, 2, 14), "7890********2222", "Foreign Currency Transactions", "TEST FOREIGN LOCATION", 1234.56, "999.99 USD @ 1.234567")
        tx2 = cctp.Transaction(datetime.date(2018, 2, 14), "7890********2222", "Foreign Currency Transactions", "TEST FOREIGN LOCATION", 1234.56, "999.99 USD @ 1.234567")
        self.assertEqual(tx1, tx2)

        tx1 = cctp.Transaction(datetime.date(2018, 1, 13), "7890********3333", "Home & Office Improvement", "TEST LOCATION", 1.23, None)
        tx2 = cctp.Transaction(datetime.date(2018, 1, 13), "7890********3333", "Home & Office Improvement", "TEST LOCATION", 1.23, None)
        self.assertEqual(tx1, tx2)

    def test_not_eq(self):
        tx1 = cctp.Transaction(datetime.date(2000, 1, 23), "1234********5678", "Test Category", "TEST LOCATION", 123.45, "100.23 USD @ 1.234567")
        tx2 = None
        self.assertNotEqual(tx1, tx2)

        tx1 = cctp.Transaction(datetime.date(2000, 1, 23), "1234********5678", "Test Category", "TEST LOCATION", 123.45, "100.23 USD @ 1.234567")
        tx2 = "Not a Transaction"
        self.assertNotEqual(tx1, tx2)

        tx1 = cctp.Transaction(datetime.date(2000, 1, 23), "1234********5678", "Test Category", "TEST LOCATION", 123.45, "100.23 USD @ 1.234567")
        tx2 = cctp.Transaction(datetime.date(2001, 2, 24), "1234********5678", "Test Category", "TEST LOCATION", 123.45, "100.23 USD @ 1.234567")
        self.assertNotEqual(tx1, tx2)  # different date

        tx1 = cctp.Transaction(datetime.date(2000, 1, 23), "1234********5678", "Test Category", "TEST LOCATION", 123.45, "100.23 USD @ 1.234567")
        tx2 = cctp.Transaction(datetime.date(2000, 1, 23), "1234********6789", "Test Category", "TEST LOCATION", 123.45, "100.23 USD @ 1.234567")
        self.assertNotEqual(tx1, tx2)  # different card

        tx1 = cctp.Transaction(datetime.date(2000, 1, 23), "1234********5678", "Test Category", "TEST LOCATION", 123.45, "100.23 USD @ 1.234567")
        tx2 = cctp.Transaction(datetime.date(2000, 1, 23), "1234********5678", "Other Category", "TEST LOCATION", 123.45, "100.23 USD @ 1.234567")
        self.assertNotEqual(tx1, tx2)  # different category

        tx1 = cctp.Transaction(datetime.date(2000, 1, 23), "1234********5678", "Test Category", "TEST LOCATION", 123.45, "100.23 USD @ 1.234567")
        tx2 = cctp.Transaction(datetime.date(2000, 1, 23), "1234********5678", "Test Category", "ANOTHER LOCATION", 123.45, "100.23 USD @ 1.234567")
        self.assertNotEqual(tx1, tx2)  # different location

        tx1 = cctp.Transaction(datetime.date(2000, 1, 23), "1234********5678", "Test Category", "TEST LOCATION", 123.45, "100.23 USD @ 1.234567")
        tx2 = cctp.Transaction(datetime.date(2000, 1, 23), "1234********5678", "Test Category", "TEST LOCATION", 543.21, "100.23 USD @ 1.234567")
        self.assertNotEqual(tx1, tx2)  # different amount

        tx1 = cctp.Transaction(datetime.date(2000, 1, 23), "1234********5678", "Test Category", "TEST LOCATION", 123.45, "100.23 USD @ 1.234567")
        tx2 = cctp.Transaction(datetime.date(2000, 1, 23), "1234********5678", "Test Category", "TEST LOCATION", 123.45, "98.76 USD @ 2.345678")
        self.assertNotEqual(tx1, tx2)  # different conversion

    def test_repr(self):
        tx = cctp.Transaction(datetime.date(2018, 9, 18), "4321********0987", "PAYMENT", None, 1.23, None)
        expected = "Transaction(amount=1.23,card=4321********0987,category=PAYMENT,conversion=None,date=2018-09-18,location=None)"
        self.assertEqual(repr(tx), expected)

        tx = cctp.Transaction(datetime.date(2018, 9, 18), "4321********0987", "FTCs", "TEST LOCATION, CA", 1234.00, "1,000.00 USD @ 1.234567")
        expected = "Transaction(amount=1234.0,card=4321********0987,category=FTCs,conversion=1,000.00 USD @ 1.234567,date=2018-09-18,location=TEST LOCATION, CA)"
        self.assertEqual(repr(tx), expected)


class ParseTests(unittest.TestCase):

    def test_payment(self):
        tx_input = """
            Dec 31, 2017	PAYMENT THANK YOU/PAIEMEN T MERCI 
            4567********1234	
            $5.00
            """
        result = cctp.parse(tx_input)
        self.assertEqual(result.date, datetime.date(2017, 12, 31))
        self.assertEqual(result.category, "PAYMENT")
        self.assertIsNone(result.location)
        self.assertEqual(result.card, "4567********1234")
        self.assertEqual(result.amount, 5.00)
        self.assertIsNone(result.conversion)

    def test_restaurant(self):
        tx_input = """
            Jan 1, 2018	Restaurants TEST RESTAURANT #321 SASKATOON, SK 
            4567********1234	
            −$123.45
            """
        result = cctp.parse(tx_input)
        self.assertEqual(result.date, datetime.date(2018, 1, 1))
        self.assertEqual(result.category, "Restaurants")
        self.assertEqual(result.location, "TEST RESTAURANT #321 SASKATOON, SK")
        self.assertEqual(result.card, "4567********1234")
        self.assertEqual(result.amount, 123.45)
        self.assertIsNone(result.conversion)

    def test_personal_and_household_expense(self):
        tx_input = """
            Jan 2, 2018	Personal & Household Expenses Amazon.ca AMAZON.CA, XX 
            4567********1234	
            −$2,345.67
            """
        result = cctp.parse(tx_input)
        self.assertEqual(result.date, datetime.date(2018, 1, 2))
        self.assertEqual(result.category, "Personal & Household Expenses")
        self.assertEqual(result.location, "Amazon.ca AMAZON.CA, XX")
        self.assertEqual(result.card, "4567********1234")
        self.assertEqual(result.amount, 2345.67)
        self.assertIsNone(result.conversion)

    def test_professional_and_financial_services(self):
        tx_input = """
            Jan 3, 2018	Professional and Financial Services GOOGLE *Google Music 123-456-7890, YZ 
            4567********1234	
            −$8.99
            """
        result = cctp.parse(tx_input)
        self.assertEqual(result.date, datetime.date(2018, 1, 3))
        self.assertEqual(result.category, "Professional and Financial Services")
        self.assertEqual(result.location, "GOOGLE *Google Music 123-456-7890, YZ")
        self.assertEqual(result.card, "4567********1234")
        self.assertEqual(result.amount, 8.99)
        self.assertIsNone(result.conversion)

    def test_retail_and_grocery(self):
        tx_input = """
            Jan 4, 2018	Retail and Grocery SOBEYS #4321 SASKATOON, SK 
            4567********1234	
            −$98.76
            """
        result = cctp.parse(tx_input)
        self.assertEqual(result.date, datetime.date(2018, 1, 4))
        self.assertEqual(result.category, "Retail and Grocery")
        self.assertEqual(result.location, "SOBEYS #4321 SASKATOON, SK")
        self.assertEqual(result.card, "4567********1234")
        self.assertEqual(result.amount, 98.76)
        self.assertIsNone(result.conversion)

    def test_transportation(self):
        tx_input = """
            Jan 5, 2018	Transportation SHELL 0123 TEST AVENUE SASKATOON, SK 
            4567********1234	
            −$38.80
            """
        result = cctp.parse(tx_input)
        self.assertEqual(result.date, datetime.date(2018, 1, 5))
        self.assertEqual(result.category, "Transportation")
        self.assertEqual(result.location, "SHELL 0123 TEST AVENUE SASKATOON, SK")
        self.assertEqual(result.card, "4567********1234")
        self.assertEqual(result.amount, 38.80)
        self.assertIsNone(result.conversion)

    def test_home_and_office_improvement(self):
        tx_input = """
            Jan 6, 2018	Home & Office Improvement BEST BUY #987 SASKATOON, SK 
            4567********1234	
            −$321.98
            """
        result = cctp.parse(tx_input)
        self.assertEqual(result.date, datetime.date(2018, 1, 6))
        self.assertEqual(result.category, "Home & Office Improvement")
        self.assertEqual(result.location, "BEST BUY #987 SASKATOON, SK")
        self.assertEqual(result.card, "4567********1234")
        self.assertEqual(result.amount, 321.98)
        self.assertIsNone(result.conversion)

    def test_foreign_currency_transaction(self):
        tx_input = """
            Feb 1, 2018	Foreign Currency Transactions TESTSTORECOM http://www.test, CA 98.76 USD @ 1.234567 
            4567********1234	
            −$123.45
            """
        result = cctp.parse(tx_input)
        self.assertEqual(result.date, datetime.date(2018, 2, 1))
        self.assertEqual(result.category, "Foreign Currency Transactions")
        self.assertEqual(result.location, "TESTSTORECOM http://www.test, CA")
        self.assertEqual(result.card, "4567********1234")
        self.assertEqual(result.amount, 123.45)
        self.assertEqual(result.conversion, "98.76 USD @ 1.234567")

    def test_hotels_entertainment_and_recreation(self):
        tx_input = """
            Feb 2, 2018	Hotels, Entertainment, and Recreation STEAMGAMES.COM 425-952-2985
            4567********1234
            −$100.00
            """
        result = cctp.parse(tx_input)
        self.assertEqual(result.date, datetime.date(2018, 2, 2))
        self.assertEqual(result.category, "Hotels, Entertainment, and Recreation")
        self.assertEqual(result.location, "STEAMGAMES.COM 425-952-2985")
        self.assertEqual(result.card, "4567********1234")
        self.assertEqual(result.amount, 100.00)
        self.assertIsNone(result.conversion)

    def test_health_and_education(self):
        tx_input = """
            May 17, 2018	Health & Education PHARMACY NUMBER ONE SASKATOON, SK
            4567********1234
            −$53.21
            """
        result = cctp.parse(tx_input)
        self.assertEqual(result.date, datetime.date(2018, 5, 17))
        self.assertEqual(result.category, "Health & Education")
        self.assertEqual(result.location, "PHARMACY NUMBER ONE SASKATOON, SK")
        self.assertEqual(result.card, "4567********1234")
        self.assertEqual(result.amount, 53.21)
        self.assertIsNone(result.conversion)

    def test_credit(self):
        tx_input = """
            Apr 10, 2018	Restaurants MCDONALD'S #40485 SASKATOON, SK
            4567********1234
            $4.56
            """
        result = cctp.parse(tx_input)
        self.assertEqual(result.date, datetime.date(2018, 4, 10))
        self.assertEqual(result.category, "Restaurants")
        self.assertEqual(result.location, "MCDONALD'S #40485 SASKATOON, SK")
        self.assertEqual(result.card, "4567********1234")
        self.assertEqual(result.amount, -4.56)
        self.assertIsNone(result.conversion)

    def test_cash_back(self):
        tx_input = """
            Dec 25, 2018	CASH BACK AWARDED
            4567********1234
            $543.21
            """
        result = cctp.parse(tx_input)
        self.assertEqual(result.date, datetime.date(2018, 12, 25))
        self.assertEqual(result.category, "CASH BACK AWARDED")
        self.assertIsNone(result.location)
        self.assertEqual(result.card, "4567********1234")
        self.assertEqual(result.amount, 543.21)
        self.assertIsNone(result.conversion)
