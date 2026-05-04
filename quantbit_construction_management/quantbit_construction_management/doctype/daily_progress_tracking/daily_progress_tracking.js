// Copyright (c) 2026, Quantbit Technology and contributors
// For license information, please see license.txt


frappe.ui.form.on("Daily Progress Tracking", {

	setup(frm) {

		frm.set_query("task", "task_template", function (doc, cdt, cdn) {

			return {
				filters: {
					status: "Template",
					project: doc.project
				}
			};

		});

	}

});


frappe.ui.form.on("Task Summary", {

	task(frm) {

		load_dpr_activity_progress(frm);

	},

	task_remove(frm) {

		load_dpr_activity_progress(frm);

	}

});


function load_dpr_activity_progress(frm) {

	if (!frm.doc.task_template.length) {

		frm.set_value("dpr_activity_progress", []);

		return;

	}


	frappe.call({

		method:

		"quantbit_construction_management.quantbit_construction_management.doctype.daily_progress_tracking.daily_progress_tracking.update_daily_activity_progress_table",

		args: {

			doc: frm.doc

		},

		callback(r) {

			if (!r.message) return;


			frm.set_value(

				"dpr_activity_progress",

				r.message.dpr_activity_progress

			);

		}

	});

}


frappe.ui.form.on("DPR Activity Progress", {

    planned_today(frm, cdt, cdn) {

        validate_progress_limits(frm, cdt, cdn, "planned_today");

    },

	achieved_today(frm, cdt, cdn) {

		update_progress(frm, cdt, cdn);
        validate_progress_limits(frm, cdt, cdn, "achieved_today");

	},

	total_qty(frm, cdt, cdn) {

		update_progress(frm, cdt, cdn);

	}

});


function validate_progress_limits(frm, cdt, cdn, fieldname) {

    let row = locals[cdt][cdn];

    let total_qty = row.total_qty || 0;

    let total_achieved = row.total_achieved || 0;

    let remaining_qty = total_qty - total_achieved;

    let entered_value = row[fieldname] || 0;


    if (entered_value > remaining_qty) {

        frappe.msgprint({

            title: "Invalid Entry",

            message:
            `${fieldname.replace("_", " ")} cannot be greater than remaining quantity (${remaining_qty})`,

            indicator: "red"

        });

        row[fieldname] = remaining_qty > 0 ? remaining_qty : 0;

        frm.refresh_field("dpr_activity_progress");

    }

}


function update_progress(frm, cdt, cdn) {

	let row = locals[cdt][cdn];


	let total_qty = row.total_qty || 0;

	let achieved_today = row.achieved_today || 0;

	let total_previous = row.total_achieved || 0;


	row.total_achieved = total_previous + achieved_today;


	if (total_qty > 0) {

		row.percent_completed =

		(row.total_achieved / total_qty) * 100;

	}

	else {

		row.percent_completed = 0;

	}


	frm.refresh_field("dpr_activity_progress");

}