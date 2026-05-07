import random
import frappe


def generate_unique_8_digit_number(doctype, fieldname):

    while True:

        number = str(random.randint(10000000, 99999999))

        exists = frappe.db.exists(
            doctype,
            {fieldname: number}
        )

        if not exists:
            return number


@frappe.whitelist()
def convert_uom_or_warn(from_uom, to_uom, value):

    if not from_uom or not to_uom:
        frappe.msgprint("Check the UOM")
        return None

    from_uom = str(from_uom).strip()
    to_uom = str(to_uom).strip()

    if from_uom.lower() == "hrs" or to_uom.lower() == "hrs":
        return float(value or 0)

    if from_uom == to_uom:
        return float(value or 0)

    conversion = frappe.db.sql("""
        SELECT conversion_factor
        FROM `tabUOM Conversion Table`
        WHERE uom=%s AND conversion_uom=%s
        LIMIT 1
    """, (from_uom, to_uom))

    if conversion:
        return float(value) * float(conversion[0][0])

    reverse_conversion = frappe.db.sql("""
        SELECT conversion_factor
        FROM `tabUOM Conversion Table`
        WHERE uom=%s AND conversion_uom=%s
        LIMIT 1
    """, (to_uom, from_uom))

    if reverse_conversion:
        return float(value) / float(reverse_conversion[0][0])

    frappe.msgprint(
        f"Check the UOM conversion between {from_uom} and {to_uom}"
    )

    return None
