# Copyright (c) 2026, QTPL and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from quantbit_construction_management.utils import generate_unique_8_digit_number


class RFI(Document):
	
	def before_insert(self):

		if not self.rfi_number:

			self.rfi_number = generate_unique_8_digit_number(
				"RFI",
				"rfi_number"
			)

	def validate(self):

		self.validate_required_by_date()
		self.validate_close_without_response()

	def validate_required_by_date(self):

		if self.required_by and self.required_by < self.raised_date:

			frappe.throw(
				"Response Required By date must be after Raised date."
			)

	def validate_close_without_response(self):

		if self.status == "Closed" and not self.response:

			frappe.throw(
				"RFI cannot be closed without a response."
			)

	def on_submit(self):

		if self.priority in ["High", "Urgent"]:

			frappe.msgprint(
				f"High priority RFI {self.name} submitted."
			)