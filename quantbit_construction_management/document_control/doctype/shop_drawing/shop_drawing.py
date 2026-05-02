# Copyright (c) 2026, QTPL and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from quantbit_construction_management.utils import generate_unique_8_digit_number


class ShopDrawing(Document):
	
	def before_insert(self):

		if not self.sd_no:

			self.sd_no = generate_unique_8_digit_number(
				"Shop Drawing",
				"sd_no"
			)

	def validate(self):

		self.validate_rejection_comments()


	def validate_rejection_comments(self):

		if self.review_action == "Rejected" and not self.comments:

			frappe.throw(
				"Review comments are required when rejecting."
			)