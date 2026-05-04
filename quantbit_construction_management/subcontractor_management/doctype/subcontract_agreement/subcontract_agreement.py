# Copyright (c) 2026, QTPL and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from quantbit_construction_management.utils import generate_unique_8_digit_number


class SubcontractAgreement(Document):

    def before_insert(self):

        if not self.sca_no:

            self.sca_no = generate_unique_8_digit_number(
                "Subcontract Agreement",
                "sca_no"
            )