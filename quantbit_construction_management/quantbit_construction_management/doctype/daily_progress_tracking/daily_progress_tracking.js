// Copyright (c) 2026, Quantbit Technology and contributors
// For license information, please see license.txt


frappe.ui.form.on("Daily Progress Tracking", {

	setup(frm) {

		frm.set_query("task", "task_template", function (doc, cdt, cdn) {

			return {
				filters: {
					custom_is_stage: 1,
					is_group: 1,
					project: doc.project
				}
			};

		});

	},

	after_save(frm) {

		if (!frm.doc.project) return;

		// 🔥 notify project screen
		frappe.publish_realtime("project_progress_refresh", {
			project: frm.doc.project
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
    let achieved_today = row.achieved_today || 0;

    let previous_today = row._previous_achieved_today || 0;
    let base_achieved = (row.total_achieved || 0) - previous_today;

    let remaining_qty = total_qty - base_achieved;

    let entered_value = row[fieldname] || 0;

    if (entered_value > remaining_qty) {

        frappe.msgprint({
            title: "Invalid Entry",
            message: `${fieldname.replace("_", " ")} cannot exceed remaining quantity (${remaining_qty})`,
            indicator: "red"
        });

        return;
    }
}


function update_progress(frm, cdt, cdn) {

    let row = locals[cdt][cdn];

    let total_qty = row.total_qty || 0;
    let achieved_today = row.achieved_today || 0;

    // 🔥 remove previous today value
    let previous_today = row._previous_achieved_today || 0;

    let base_achieved = (row.total_achieved || 0) - previous_today;

    let new_total = base_achieved + achieved_today;

    // 🚨 VALIDATION
    if (new_total > total_qty) {

        frappe.msgprint({
            title: "Invalid Entry",
            message: "Total achieved cannot exceed total quantity",
            indicator: "red"
        });

        // reset today's value
        row.achieved_today = 0;

        // restore previous correct total
        row.total_achieved = base_achieved;

        // reset tracker
        row._previous_achieved_today = 0;

    } else {

        // ✅ valid case
        row.total_achieved = new_total;
        row._previous_achieved_today = achieved_today;

    }

    // % calculation
    if (total_qty > 0) {
        row.percent_completed = (row.total_achieved / total_qty) * 100;
    } else {
        row.percent_completed = 0;
    }

    frm.refresh_field("dpr_activity_progress");
}