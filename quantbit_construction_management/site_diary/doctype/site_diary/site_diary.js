frappe.ui.form.on("Site Diary", {

	setup(frm) {

		frm.set_query("task", "task", function (doc, cdt, cdn) {

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

    if (!frm.doc.task || !frm.doc.task.length) {
        frm.set_value("activity_progress", []);
        return;
    }

    frappe.call({
        method: "quantbit_construction_management.site_diary.doctype.site_diary.site_diary.update_daily_activity_progress_table",
        args: {
            doc: frm.doc
        },
        callback(r) {

            if (!r.message) return;

            let new_data = r.message.activity_progress || [];
            let existing = frm.doc.activity_progress || [];

            let updated_rows = [];

            // 🔹 Step 1: Keep only rows whose parent_task still exists
            let valid_parent_tasks = frm.doc.task.map(t => t.task);

            existing.forEach(row => {
                if (valid_parent_tasks.includes(row.parent_task)) {
                    updated_rows.push(row);
                }
            });

            // 🔹 Step 2: Add missing new subtasks
            new_data.forEach(new_row => {

                let exists = updated_rows.find(r =>
                    r.parent_task === new_row.parent_task &&
                    r.task === new_row.task
                );

                if (!exists) {
                    updated_rows.push(new_row);
                }

            });

            // 🔹 Step 3: Set merged data
            frm.set_value("activity_progress", updated_rows);

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
    let previous_today = row._previous_achieved_today || 0;
    let base_achieved = (row.total_achieved || 0) - previous_today;
    let new_total = base_achieved + achieved_today;

    if (new_total > total_qty) {

        frappe.msgprint({
            title: "Invalid Entry",
            message: "Total achieved cannot exceed total quantity",
            indicator: "red"
        });

        row.achieved_today = 0;
        row.total_achieved = base_achieved;
        row._previous_achieved_today = 0;

    } else {
        row.total_achieved = new_total;
        row._previous_achieved_today = achieved_today;
    }

    if (total_qty > 0) {
        row.percent_completed = (row.total_achieved / total_qty) * 100;
    } else {
        row.percent_completed = 0;
    }

    frm.refresh_field("activity_progress");
}


frappe.ui.form.on("Manpower Log", {

    skilled: function(frm, cdt, cdn) {
        calculate_total(frm, cdt, cdn);
    },

    unskilled: function(frm, cdt, cdn) {
        calculate_total(frm, cdt, cdn);
    },

    supervisors: function(frm, cdt, cdn) {
        calculate_total(frm, cdt, cdn);
    },

    hours_worked: function(frm, cdt, cdn) {
        validate_hours(frm, cdt, cdn);
    },

    overtime_hours: function(frm, cdt, cdn) {
        validate_hours(frm, cdt, cdn);
    }

});


function calculate_total(frm, cdt, cdn) {

    let row = locals[cdt][cdn];

    let total =
        (row.skilled || 0) +
        (row.unskilled || 0) +
        (row.supervisors || 0);

    frappe.model.set_value(cdt, cdn, "total", total);

    update_parent_total(frm);
}


function validate_hours(frm, cdt, cdn) {

    let row = locals[cdt][cdn];

    let total_hours =
        (row.hours_worked || 0) +
        (row.overtime_hours || 0);

    if (total_hours > 16) {

        frappe.msgprint(
            "Working Hours + Overtime Hours must be between 0 and 16"
        );

        frappe.model.set_value(cdt, cdn, "hours_worked", 8);
        frappe.model.set_value(cdt, cdn, "overtime_hours", 0);
    }
}
