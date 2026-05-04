# Copyright (c) 2026, QTPL and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from quantbit_construction_management.utils import generate_unique_8_digit_number


class SCWorkOrder(Document):

    def before_insert(self):

        if not self.wo_no:

            self.wo_no = generate_unique_8_digit_number(
                "SC Work Order",
                "wo_no"
            )