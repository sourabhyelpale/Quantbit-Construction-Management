import frappe


def on_update(doc, method):

    if doc.workflow_state != "Tender created":
        return

    try:
        tender = frappe.get_doc({
            "doctype": "Tender",
            "opportunity": doc.name,
            "customer": doc.party_name,
            "company": doc.company,
            "tender_notification_date": doc.custom_tender_notification_date,
            "transaction_date": doc.transaction_date,
            "opportunity_owner": doc.opportunity_owner,
            "opportunity_from": doc.opportunity_from,
            "party_name": doc.party_name,
            "opportunity_type": doc.opportunity_type,
            "sales_stage": doc.sales_stage,
            "probability": doc.probability,
            "no_of_employees": doc.no_of_employees,
            "annual_revenue": doc.annual_revenue,
            "country": doc.country,
            "currency": doc.currency,
            "opportunity_amount": doc.opportunity_amount,
            "industry": doc.industry,
            "market_segment": doc.market_segment,
            "city": doc.city,
            "state": doc.state,
            "territory": doc.territory,
            "contact_person": doc.contact_person,
            "contact_email": doc.contact_email,
            "contact_mobile": doc.contact_mobile,
            "whatsapp": doc.whatsapp,
            "phone": doc.phone,
            "phone_ext": doc.phone_ext,
            "tenderrfp_number": doc.custom_tenderrfp_number,
            "tender_reference": doc.custom_tender_reference,
            "tender_submission_date": doc.custom_tender_submission_date,
            "project_duration": doc.custom_project_duration,
            "jvconsortium": doc.custom_jvconsortium,
            "tender_fee_exempted": doc.custom_tender_fee_exempted,
            "tender_fee": doc.custom_tender_fee,
            "tender_category": doc.custom_tender_category,
            "tender_type": doc.custom_tender_type,
            "emd_exempted": doc.custom_emd_exempted,
            "earnest_money_deposit": doc.custom_earnest_money_deposit,
            "next_activity_deadline": doc.custom_next_activity_deadline,
            "next_activity_summary": doc.custom_next_activity_summary,
            "scope_of_work": doc.custom_scope_of_work,
            "bid_evaluation_criteriacommerical": doc.custom_bid_evaluation_criteriacommercial,
            "bid_evaluation_criteriatechnical": doc.custom_bid_evaluation_criteriatechnical,
            "total": doc.total,
            "items": []
        })

        for row in doc.items:
            tender.append("items", {
                "item_code": row.item_code,
                "item_name": row.item_name,
                "qty": row.qty,
                "uom": row.uom,
                "rate": row.rate or 0,
                "amount": row.amount or 0,
                "base_rate": row.base_rate or row.rate or 0,
                "base_amount": row.base_amount or row.amount or 0,
                "description": row.description
            })

        tender.insert(ignore_permissions=True)

        doc.db_set("custom_tender_created", tender.name)

        frappe.msgprint(f"Tender {tender.name} created successfully.")

    except Exception:
        frappe.db.rollback()

        doc.db_set("workflow_state", "Go For Bid")

        frappe.log_error(
            frappe.get_traceback(),
            f"Tender Creation Failed for Opportunity {doc.name}"
        )

        frappe.throw(
            "Tender creation failed due to an internal error. Workflow has been reverted to 'Go For Bid'. Please contact administrator."
        )