import random
import frappe


def generate_unique_8_digit_number(doctype, fieldname):

    while True:

        number = str(random.randint(10000000, 99999999))

        exists = frappe.db.exists(
            doctype,
            {fieldname: number}
        )

        if not exists:
            return number