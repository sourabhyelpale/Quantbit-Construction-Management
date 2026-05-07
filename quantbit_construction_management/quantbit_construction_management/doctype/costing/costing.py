# Copyright (c) 2026
# License: MIT

import frappe
from frappe.model.document import Document
from quantbit_construction_management.utils import convert_uom_or_warn


class Costing(Document):
    pass


@frappe.whitelist()
def update_costing_task_table(doc):

    doc = frappe.get_doc(frappe.parse_json(doc))

    existing_values = {}

    for row in doc.costing_work_details:
        key = (row.construction_type, row.uom)
        existing_values[key] = row.value


    doc.costing_task = []

    for parent_row in doc.task:

        if not parent_row.task:
            continue

        parent_task = frappe.get_doc("Task", parent_row.task)

        for sub in parent_task.depends_on:

            if not sub.task:
                continue

            sub_task = frappe.get_doc("Task", sub.task)

            doc.append("costing_task", {
                "parent_task": parent_row.task,
                "task": sub.task,
                "construction_type": sub_task.custom_construction_type,
                "uom": sub_task.custom_uom
            })


    new_rows = []
    seen = set()

    for row in doc.costing_task:

        if not row.construction_type:
            continue

        key = (row.construction_type, row.uom)

        if key in seen:
            continue

        seen.add(key)

        new_rows.append({
            "construction_type": row.construction_type,
            "uom": row.uom,
            "value": existing_values.get(key, 0)
        })

    doc.set("costing_work_details", new_rows)

    return doc


@frappe.whitelist()
def get_costing_work_details_from_costing_task(doc):

    doc = frappe.get_doc(frappe.parse_json(doc))

    doc.set("costing_work_details", [])

    seen = set()

    for row in doc.costing_task:

        if not row.construction_type:
            continue

        key = (row.construction_type, row.uom)

        if key in seen:
            continue

        seen.add(key)

        doc.append("costing_work_details", {
            "construction_type": row.construction_type,
            "uom": row.uom,
            "value": 0
        })

    return doc


@frappe.whitelist()
def get_costing(doc):

    doc = frappe.get_doc(frappe.parse_json(doc))

    doc.worker_costing = []
    doc.equipment_costing = []
    doc.material_costing = []


    worker_counts = {}

    workers = frappe.get_all(
        "Worker Master",
        fields=["worker_type"]
    )

    for w in workers:
        if w.worker_type:
            worker_counts[w.worker_type] = worker_counts.get(w.worker_type, 0) + 1


    worker_summary = {}

    worker_types = frappe.get_all("Worker Type", pluck="name")


    for work_row in doc.costing_work_details:

        construction_type = work_row.construction_type
        qty_required = float(work_row.value or 0)


        for worker in worker_types:

            worker_doc = frappe.get_doc("Worker Type", worker)

            for detail in worker_doc.work_details:

                if detail.construction_type != construction_type:
                    continue


                converted_qty = convert_uom_or_warn(
                    work_row.uom,
                    detail.uom,
                    qty_required
                )

                if converted_qty is None:
                    continue


                minutes_per_unit = float(detail.time or 0)
                rate = float(detail.rate or 0)

                worker_count = worker_counts.get(worker, 0)

                if worker_count == 0:
                    continue


                total_minutes = converted_qty * minutes_per_unit
                actual_minutes = total_minutes / worker_count
                hours = actual_minutes / 60
                total_amount = converted_qty * rate


                if worker not in worker_summary:

                    display_qty = convert_uom_or_warn(
                        detail.uom,
                        work_row.uom,
                        converted_qty
                    )

                    worker_summary[worker] = {
                        "qty": worker_count,
                        "rate": rate,
                        "time": hours,
                        "total_work": display_qty,
                        "total_amount": total_amount
                    }

                else:

                    worker_summary[worker]["time"] += hours
                    worker_summary[worker]["total_work"] += convert_uom_or_warn(
                        detail.uom,
                        work_row.uom,
                        converted_qty
                    )
                    worker_summary[worker]["total_amount"] += total_amount


    for worker, data in worker_summary.items():

        doc.append("worker_costing", {

            "worker_type": worker,
            "qty": data["qty"],
            "rate": data["rate"],
            "time": round(data["time"], 2),
            "total_work": round(data["total_work"], 2),
            "total_amount": round(data["total_amount"], 2)

        })


    equipment_summary = {}

    equipment_list = frappe.get_all("Equipment", pluck="name")


    for work_row in doc.costing_work_details:

        construction_type = work_row.construction_type
        qty_required = float(work_row.value or 0)


        for equipment in equipment_list:

            equipment_doc = frappe.get_doc("Equipment", equipment)

            for detail in equipment_doc.work_details:

                if detail.construction_type != construction_type:
                    continue


                converted_qty = convert_uom_or_warn(
                    work_row.uom,
                    detail.uom,
                    qty_required
                )

                if converted_qty is None:
                    continue


                minutes_per_unit = float(detail.time or 0)
                rate = float(detail.rate or 0)


                total_minutes = converted_qty * minutes_per_unit
                hours = total_minutes / 60
                total_amount = converted_qty * rate


                if equipment not in equipment_summary:

                    display_qty = convert_uom_or_warn(
                        detail.uom,
                        work_row.uom,
                        converted_qty
                    )

                    equipment_summary[equipment] = {

                        "qty": 1,
                        "rate": rate,
                        "time": hours,
                        "total_work": display_qty,
                        "total_amount": total_amount

                    }

                else:

                    equipment_summary[equipment]["time"] += hours
                    equipment_summary[equipment]["total_work"] += convert_uom_or_warn(
                        detail.uom,
                        work_row.uom,
                        converted_qty
                    )
                    equipment_summary[equipment]["total_amount"] += total_amount


    for equipment, data in equipment_summary.items():

        doc.append("equipment_costing", {

            "equipment": equipment,
            "qty": data["qty"],
            "rate": data["rate"],
            "time": round(data["time"], 2),
            "total_work": round(data["total_work"], 2),
            "total_amount": round(data["total_amount"], 2)

        })


    material_summary = {}


    for work_row in doc.costing_work_details:

        construction_type = work_row.construction_type
        qty_required = float(work_row.value or 0)


        if not construction_type:
            continue


        construction_doc = frappe.get_doc(
            "Construction Type",
            construction_type
        )


        for material in construction_doc.material_details:


            converted_qty = convert_uom_or_warn(
                material.construction_uom,
                work_row.uom,
                float(material.qty or 0) * qty_required
            )


            if converted_qty is None:
                continue


            item = material.item


            if not item:
                continue


            item_rate = frappe.db.get_value(
                "Item Price",
                {
                    "item_code": item,
                    "price_list": "Construction Price",
                    "uom": material.item_uom
                },
                "price_list_rate"
            ) or 0


            total_amount = float(converted_qty) * float(item_rate)


            if item not in material_summary:

                material_summary[item] = {

                    "item": item,
                    "item_name": material.item_name,
                    "total_qty": converted_qty,
                    "rate": item_rate,
                    "total_amount": total_amount
                }

            else:

                material_summary[item]["total_qty"] += converted_qty
                material_summary[item]["total_amount"] += total_amount


    for row in material_summary.values():

        doc.append("material_costing", row)


    return {
        "worker_costing": doc.worker_costing,
        "equipment_costing": doc.equipment_costing,
        "material_costing": doc.material_costing
    }


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_child_tasks(doctype, txt, searchfield, start, page_len, filters):

    parent_task = filters.get("parent_task")

    if not parent_task:
        return []

    return frappe.db.sql(
        """
        SELECT name, subject
        FROM `tabTask`
        WHERE parent_task = %(parent_task)s
        AND status = 'Template'
        AND name LIKE %(txt)s
        ORDER BY subject
        LIMIT %(start)s, %(page_len)s
        """,
        {
            "parent_task": parent_task,
            "txt": f"%{txt}%",
            "start": start,
            "page_len": page_len,
        },
    )