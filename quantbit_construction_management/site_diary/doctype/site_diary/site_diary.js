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
