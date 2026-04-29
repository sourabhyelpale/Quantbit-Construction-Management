// Copyright (c) 2026, QTPL and contributors
// For license information, please see license.txt


frappe.ui.form.on("Tender", {
    
    total_ctc: function(frm) {
        calculate_contract_values(frm);
    },

    profit_on_ctc: function(frm) {
        calculate_contract_values(frm);
    }
});

function calculate_contract_values(frm) {
    if (frm.doc.total_ctc && frm.doc.profit_on_ctc) {

        let contract_value = frm.doc.total_ctc * (1 + (frm.doc.profit_on_ctc / 100));
        let profit_margin = contract_value - frm.doc.total_ctc;
        let net_profit_margin = contract_value
            ? (profit_margin / contract_value) * 100
            : 0;

        frm.set_value("contract_value", contract_value);
        frm.set_value("profit_margin", profit_margin);
        frm.set_value("net_profit_margin", net_profit_margin);

    } else {
        frm.set_value("contract_value", 0);
        frm.set_value("profit_margin", 0);
        frm.set_value("net_profit_margin", 0);
    }
}
