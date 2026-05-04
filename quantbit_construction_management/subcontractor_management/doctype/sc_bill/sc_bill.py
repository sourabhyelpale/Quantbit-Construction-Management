# Copyright (c) 2026, QTPL and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from quantbit_construction_management.utils import generate_unique_8_digit_number


class SCBill(Document):

    def before_insert(self):

        if not self.bill_no:

            self.bill_no = generate_unique_8_digit_number(
                "SC Bill",
                "bill_no"
            )