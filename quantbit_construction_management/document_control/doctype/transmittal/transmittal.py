# Copyright (c) 2026, QTPL and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from quantbit_construction_management.utils import generate_unique_8_digit_number


class Transmittal(Document):
	
	def before_insert(self):

		if not self.transmittal_no:

			self.transmittal_no = generate_unique_8_digit_number(
				"Transmittal",
				"transmittal_no"
			)

	def before_save(self):

		self.validate_response_due_date()


	def before_submit(self):

		self.validate_drawings_exist()
		self.status = "Sent"


	def validate_response_due_date(self):

		if self.response_due and self.response_due <= self.date:

			frappe.throw(
				"Response due date must be after transmittal date."
			)


	def validate_drawings_exist(self):

		if not self.drawings:

			frappe.throw(
				"Add at least one drawing/document to the transmittal."
			)