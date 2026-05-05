# Copyright (c) 2026, Quantbit Technology and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DailyProgressTracking(Document):
	
	def before_save(self):

		self.validate_dpr_date()

		updated_tasks = set()

		for row in self.dpr_activity_progress:

			if not row.task or not row.total_qty:
				continue

			percent = (row.total_achieved / row.total_qty) * 100

			frappe.db.set_value("Task", row.task, "progress", percent)

			updated_tasks.add(row.task)

		for task in updated_tasks:
			update_parent_progress(task)


	def validate_dpr_date(self):

		existing = frappe.db.exists(
			"Daily Progress Tracking",
			{
				"project": self.project,
				"date": self.date,
				"name": ["!=", self.name]
			}
		)

		if existing:
			frappe.throw(
				f"A DPR already exists for date {self.date} for project {self.project}"
			)


@frappe.whitelist()
def update_daily_activity_progress_table(doc):

	doc = frappe.get_doc(frappe.parse_json(doc))

	new_rows = []

	seen = set()
	
	for parent_row in doc.task_template:

		if not parent_row.task:
			continue

		parent_task = frappe.get_doc("Task", parent_row.task)

		for sub in parent_task.depends_on:

			if not sub.task:
				continue

			key = (parent_row.task, sub.task)

			if key in seen:
				continue

			seen.add(key)

			sub_task = frappe.get_doc("Task", sub.task)


			previous = frappe.db.sql("""
				SELECT total_qty, total_achieved, percent_completed
				FROM `tabDPR Activity Progress`
				WHERE parent_task=%s
				AND task=%s
				ORDER BY creation DESC
				LIMIT 1
			""", (
				parent_row.task,
				sub.task,
			), as_dict=True)
		

			total_achieved = 0
			percent_completed = 0
			total_qty = 0

			if previous:
				total_qty = previous[0].total_qty
				total_achieved = previous[0].total_achieved
				percent_completed = previous[0].percent_completed


			new_rows.append({

				"parent_task": parent_row.task,
				"task": sub.task,
				"construction_type": sub_task.custom_construction_type,
				"total_qty": total_qty,
				"uom": sub_task.custom_uom,
				"total_achieved": total_achieved,
				"percent_completed": percent_completed

			})


	doc.set("dpr_activity_progress", new_rows)

	return doc


@frappe.whitelist()
def update_task_progress_from_dpr(task, achieved_qty, total_qty):

	if not total_qty:
		return

	percent = (achieved_qty / total_qty) * 100

	frappe.db.set_value("Task", task, "progress", percent)

	update_parent_progress(task)

	
def update_parent_progress(task):

    parent = frappe.db.get_value("Task", task, "parent_task")

    if not parent:
        return

    children = frappe.get_all(
        "Task",
        filters={"parent_task": parent},
        fields=["progress", "task_weight"]
    )

    if not children:
        return

    weighted_total = 0

    for c in children:
        progress = c.progress or 0
        weight = c.task_weight or 0

        weighted_total += (progress * weight) / 100

    frappe.db.set_value("Task", parent, "progress", weighted_total)

    # 🔁 recursive update
    update_parent_progress(parent)