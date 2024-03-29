# coding: utf-8
""" Credit Card Transaction Parser """

from dateutil import parser as date_parser
import csv
import re


TRANSACTIONS_FILE = "transactions.txt"
OUTPUT_FILE = "output.txt"


class Transaction(object):
    def __init__(self, date, card, category, location, amount, conversion):
        self.date = date
        self.card = card
        self.category = category
        self.location = location
        self.amount = amount
        self.conversion = conversion

    def __eq__(self, other):
        if not isinstance(other, Transaction):
            return False
        return (self.date == other.date and
                self.card == other.card and
                self.category == other.category and
                self.location == other.location and
                self.amount == other.amount and
                self.conversion == other.conversion)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        my_attrs = sorted(vars(self).items())
        my_attrs = ("{0}={1}".format(attr_name, attr_val) for attr_name, attr_val in my_attrs)
        return "Transaction({attrs})".format(attrs=",".join(my_attrs))

    def __str__(self):
        return repr(self)


CATEGORIES = [
    "PAYMENT",
    "Foreign Currency Transactions",
    "Home & Office Improvement",
    "Personal & Household Expenses",
    "Professional and Financial Services",
    "Hotels, Entertainment, and Recreation",
    "Restaurants",
    "Retail and Grocery",
    "Transportation",
    "Health & Education",
    "CASH BACK AWARDED",
    "CASH INTEREST",
    "PURCHASE INTEREST",
    "INTEREST REVERSAL",
]


def parse(tx_input):
    tx_input = tx_input.strip()

    # hack for CASH BACK 2020
    tx_input = tx_input.replace("Other TransactionsCASHBACK/REMISE EN ARGENT", "CASH BACK AWARDED")

    line1, line2, line3 = tx_input.split("\n")
    line1 = line1.strip()
    line2 = line2.strip()
    line3 = line3.strip()

    # date
    date_str, line1 = line1.split("\t")
    date = date_parser.parse(date_str).date()

    # category
    category = next((c for c in CATEGORIES if line1.startswith(c)), None)
    if not category:
        raise Exception("Unknown Category!\n"
                        "Input: '{0}'".format(line1))
    line1 = line1[len(category):].lstrip()

    # conversion
    conversion = None
    if category == "Foreign Currency Transactions":
        conversion_pattern = re.compile(r"(?P<conversion>(\d{1,3},)*\d{1,3}\.\d+ [A-Z]+ @ \d+\.\d+)$")
        conversion_match = conversion_pattern.search(line1)
        if not conversion_match:
            raise Exception("Input does not match RegEx!\n"
                            "Input: '{0}'\nRegEx: '{1}'".format(line1, conversion_pattern.pattern))
        conversion = conversion_match.group("conversion")
        line1 = line1[0:len(line1) - len(conversion) - 1]

    # location
    location = line1 if category not in ("PAYMENT", "CASH BACK AWARDED", "CASH INTEREST", "PURCHASE INTEREST", "INTEREST REVERSAL") else None

    # card
    card = line2

    # amount
    amount_pattern = re.compile(r"(?P<amount>(\d{1,3},)*\d{1,3}\.\d+)")
    amount_match = amount_pattern.search(line3)
    if not amount_match:
        raise Exception("Input does not match RegEx!\n"
                        "Input: '{0}'\nRegEx: '{1}'".format(line3, amount_pattern.pattern))
    amount_str = amount_match.group("amount")
    amount_str = amount_str.replace(",", "")
    if category != "PAYMENT" and category != "CASH BACK AWARDED"\
            and not (line3.startswith("-") or line3.startswith("−")):
        amount_str = "-" + amount_str
    amount = float(amount_str)

    return Transaction(date, card, category, location, amount, conversion)


def parse_file(filepath):
    tx_lines = []
    transactions = []
    payments = []
    with open(filepath, "r", encoding="utf-8") as f:
        line = f.readline()
        while line:
            tx_lines.append(line)

            tx_text = "".join(tx_lines)
            tx_text = re.sub(r"""\s*ELIGIBLE FOR INSTALLMENTS\s*""", "\t", tx_text, flags=re.MULTILINE)
            is_complete_tx_text = tx_text.strip().count('\n') == 2

            if is_complete_tx_text:
                tx = parse(tx_text)
                if tx.category == "PAYMENT" or tx.category == "CASH BACK AWARDED":
                    payments.append(tx)
                else:
                    transactions.append(tx)
                tx_lines = []
            line = f.readline()

    return reversed(transactions), reversed(payments)


def write_transactions_tab_delimited_to_file(transactions, filepath):
    with open(filepath, "a") as f:
        fieldnames = ["date", "amount", "card", "location", "category", "conversion"]
        writer = csv.DictWriter(f, delimiter='\t', lineterminator='\n', fieldnames=fieldnames)
        tx_dicts = [{a: v for a, v in sorted((a, v) for a, v in vars(t).items() if a in fieldnames)}
                    for t in transactions]

        writer.writeheader()
        for tx_dict in tx_dicts:
            writer.writerow(tx_dict)


def write_payments_tab_delimited_to_file(payments, filepath):
    with open(filepath, "a") as f:
        fieldnames = ["date", "amount", "card"]
        writer = csv.DictWriter(f, delimiter='\t', lineterminator='\n', fieldnames=fieldnames)
        p_dicts = [{a: v for a, v in sorted((a, v) for a, v in vars(p).items() if a in fieldnames)} for p in payments]

        writer.writeheader()
        for p_dict in p_dicts:
            writer.writerow(p_dict)


def main():
    transactions, payments = parse_file(TRANSACTIONS_FILE)

    with open(OUTPUT_FILE, "w") as f:
        f.write("Transactions\n")
        f.write("============\n")
    write_transactions_tab_delimited_to_file(transactions, OUTPUT_FILE)
    with open(OUTPUT_FILE, "a") as f:
        f.write("\n")

    with open(OUTPUT_FILE, "a") as f:
        f.write("Payments\n")
        f.write("========\n")
    write_payments_tab_delimited_to_file(payments, OUTPUT_FILE)


if __name__ == "__main__":
    main()
