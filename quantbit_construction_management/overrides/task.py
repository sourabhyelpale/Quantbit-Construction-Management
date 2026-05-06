import frappe
from frappe import _
from erpnext.projects.doctype.task.task import Task
from frappe.desk.form.assign_to import close_all_assignments


class CustomTask(Task):

    def validate_status(self):

        # Removed Template conditions

        if self.status != self.get_db_value("status") and self.status == "Completed":

            for d in self.depends_on:
                if frappe.db.get_value("Task", d.task, "status") not in ("Completed", "Cancelled"):
                    frappe.throw(
                        _(
                            "Cannot complete task {0} as its dependant task {1} are not completed / cancelled."
                        ).format(frappe.bold(self.name), frappe.bold(d.task))
                    )

            close_all_assignments(self.doctype, self.name)