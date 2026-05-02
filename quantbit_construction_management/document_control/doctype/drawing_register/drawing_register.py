# Copyright (c) 2026, QTPL and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from quantbit_construction_management.utils import generate_unique_8_digit_number


class DrawingRegister(Document):

	def before_insert(self):

		if not self.drawing_no:

			self.drawing_no = generate_unique_8_digit_number(
				"Drawing Register",
				"drawing_no"
			)

	def validate(self):

		self.validate_unique_drawing_no()
		self.validate_ifc_file_required()
		self.prevent_edit_if_superseded()
		self.validate_revision_table()
		self.update_current_revision()


	def validate_unique_drawing_no(self):

		existing = frappe.db.exists(
			"Drawing Register",
			{
				"project": self.project,
				"drawing_no": self.drawing_no,
				"name": ["!=", self.name]
			}
		)

		if existing:
			frappe.throw(
				f"Drawing number {self.drawing_no} already exists in this project."
			)


	def validate_ifc_file_required(self):

		if self.status == "Issued for Construction" and not self.file:
			frappe.throw(
				"Please attach drawing file before issuing IFC drawing."
			)


	def prevent_edit_if_superseded(self):

		if self.status == "Superseded" and not self.is_new():
			frappe.throw(
				"Superseded drawings are read-only. Create a new revision."
			)


	def validate_revision_table(self):

		revision_list = []
		last_date = None

		for row in self.revisions:

			if row.revision in revision_list:
				frappe.throw(
					f"Revision '{row.revision}' already exists for this drawing."
				)

			revision_list.append(row.revision)

			if last_date and row.revision_date < last_date:
				frappe.throw(
					"Revision date cannot be earlier than previous revision."
				)

			last_date = row.revision_date

			
	def update_current_revision(self):

		if self.revisions:

			latest_revision = sorted(
				self.revisions,
				key=lambda x: x.revision_date
			)[-1]

			self.current_rev = latest_revision.revision