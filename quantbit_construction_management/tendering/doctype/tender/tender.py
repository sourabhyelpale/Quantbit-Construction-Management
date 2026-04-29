# Copyright (c) 2026, QTPL and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Tender(Document):
	def before_submit(self):
		project= frappe.get_doc({
			'doctype':'Project',
			'project_name':self.name,
			'status':'Open',
			'is_active':'Yes',
			'customer':self.party_name,
			'expected_start_date':self.expected_start_date,
			'expected_end_date':self.expected_end_date


		})
		project.insert(ignore_permissions=True)
 