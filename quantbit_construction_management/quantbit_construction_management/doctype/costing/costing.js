
frappe.ui.form.on("Costing", {

    setup(frm) {

        frm.set_query("task", "task", function () {

            return {
                filters: {
                    is_group: 1,
                    custom_is_stage: 0
                }
            };

        });

        frm.set_query("parent_task", "costing_task", function () {

            return {
                filters: {
                    is_group: 1,
                    custom_is_stage: 0
                }
            };

        });
    },

    get_costing(frm) {

        frappe.call({

            method:
            "quantbit_construction_management.quantbit_construction_management.doctype.costing.costing.get_costing",

            args: {
                doc: frm.doc
            },

            freeze: true,

            callback(r) {

                if (!r.message) return;

                frm.set_value("worker_costing", r.message.worker_costing || []);
                frm.set_value("equipment_costing", r.message.equipment_costing || []);
                frm.set_value("material_costing", r.message.material_costing || []);

                frm.refresh_field("worker_costing");
                frm.refresh_field("equipment_costing");
                frm.refresh_field("material_costing");

                calculate_worker_total(frm);
                calculate_equipment_total(frm);
                calculate_material_total(frm);
                calculate_total_cost(frm);

            }

        });

    },

    get_data(frm) {

        frm.clear_table("worker_costing");
        frm.clear_table("equipment_costing");
        frm.clear_table("material_costing");

        frm.set_value("worker_total_cost", 0);
        frm.set_value("equipment_total_cost", 0);
        frm.set_value("material_total_cost", 0);
        frm.set_value("total_cost", 0);

        frm.refresh_field("worker_costing");
        frm.refresh_field("equipment_costing");
        frm.refresh_field("material_costing");


        frappe.call({

            method:
            "quantbit_construction_management.quantbit_construction_management.doctype.costing.costing.get_costing_work_details_from_costing_task",

            args: {
                doc: frm.doc
            },

            callback(r) {

                if (!r.message) return;

                frm.set_value(
                    "costing_work_details",
                    r.message.costing_work_details
                );

                frm.refresh_field("costing_work_details");

            }

        });

    }

});

frappe.ui.form.on("Costing Task", {

    parent_task(frm, cdt, cdn) {

        let row = locals[cdt][cdn];

        row.task = "";
        frm.refresh_field("costing_task");

    }

});


frappe.ui.form.on("Costing", {

    onload(frm) {

        frm.set_query("task", "costing_task", function(doc, cdt, cdn) {

            let row = locals[cdt][cdn];

            if (!row.parent_task) {
                return {};
            }

            return {
                query:
                "quantbit_construction_management.quantbit_construction_management.doctype.costing.costing.get_child_tasks",

                filters: {
                    parent_task: row.parent_task
                }
            };

        });

    }

});

frappe.ui.form.on("Task Summary", {

    task(frm) {
        load_costing_task(frm);
    },

    task_remove(frm) {
        load_costing_task(frm);
    }

});


function load_costing_task(frm) {

    frappe.call({

        method:
        "quantbit_construction_management.quantbit_construction_management.doctype.costing.costing.update_costing_task_table",

        args: {
            doc: frm.doc
        },

        callback(r) {

            if (!r.message) return;

            frm.set_value(
                "costing_task",
                r.message.costing_task || []
            );

            frm.set_value(
                "costing_work_details",
                r.message.costing_work_details || []
            );

            frm.refresh_field("costing_task");
            frm.refresh_field("costing_work_details");

            frm.clear_table("worker_costing");
            frm.clear_table("equipment_costing");
            frm.clear_table("material_costing");

            frm.set_value("worker_total_cost", 0);
            frm.set_value("equipment_total_cost", 0);
            frm.set_value("material_total_cost", 0);

            frm.refresh_field("worker_costing");
            frm.refresh_field("equipment_costing");
            frm.refresh_field("material_costing");

        }

    });

}

frappe.ui.form.on("Worker Costing", {

    qty: update_worker_row,
    rate: update_worker_row,
    total_work: update_worker_row

});


function update_worker_row(frm, cdt, cdn) {

    let row = locals[cdt][cdn];

    let qty = row.qty || 0;
    let work = row.total_work || 0;
    let rate = row.rate || 0;

    row.total_amount = qty * work * rate;

    if (qty > 0) {
        let total_minutes = work;
        row.time = total_minutes / (qty * 60);
    } else {
        row.time = 0;
    }

    frm.refresh_field("worker_costing");

    calculate_worker_total(frm);
    calculate_total_cost(frm);
}


frappe.ui.form.on("Equipment Costing", {

    qty: update_equipment_row,
    rate: update_equipment_row,
    total_work: update_equipment_row

});


function update_equipment_row(frm, cdt, cdn) {

    let row = locals[cdt][cdn];

    let qty = row.qty || 0;
    let work = row.total_work || 0;
    let rate = row.rate || 0;

    row.total_amount = qty * work * rate;

    // dynamic time calculation
    if (qty > 0) {
        let total_minutes = work;
        row.time = total_minutes / (qty * 60);
    } else {
        row.time = 0;
    }

    frm.refresh_field("equipment_costing");

    calculate_equipment_total(frm);
    calculate_total_cost(frm);
}


frappe.ui.form.on("Material Costing", {

    rate: update_material_row,
    total_qty: update_material_row

});

function update_material_row(frm, cdt, cdn) {

    let row = locals[cdt][cdn];

    row.total_amount = (row.rate || 0) * (row.total_qty || 0);

    frm.refresh_field("material_costing");

    calculate_material_total(frm);
    calculate_total_cost(frm);
}

function calculate_worker_total(frm) {

    let total = 0;

    (frm.doc.worker_costing || []).forEach(row => {

        total += row.total_amount || 0;

    });

    frm.set_value("worker_total_cost", total);

}


function calculate_equipment_total(frm) {

    let total = 0;

    (frm.doc.equipment_costing || []).forEach(row => {

        total += row.total_amount || 0;

    });

    frm.set_value("equipment_total_cost", total);

}


function calculate_material_total(frm) {

    let total = 0;

    (frm.doc.material_costing || []).forEach(row => {

        total += row.total_amount || 0;

    });

    frm.set_value("material_total_cost", total);

}

function calculate_total_cost(frm) {

    let total =
        (frm.doc.worker_total_cost || 0) +
        (frm.doc.equipment_total_cost || 0) +
        (frm.doc.material_total_cost || 0);

    frm.set_value("total_cost", total);
}

frappe.ui.form.on("Worker Costing", {

    worker_costing_remove(frm) {

        calculate_worker_total(frm);
        calculate_total_cost(frm);

    }

});

frappe.ui.form.on("Equipment Costing", {

    equipment_costing_remove(frm) {

        calculate_equipment_total(frm);
        calculate_total_cost(frm);

    }

});

frappe.ui.form.on("Material Costing", {

    material_costing_remove(frm) {

        calculate_material_total(frm);  
        calculate_total_cost(frm);

    }

});