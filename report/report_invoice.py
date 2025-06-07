from odoo import models

class ReportInvoice(models.AbstractModel):
    _name = 'report.mini_store.report_invoice_pdf_template'

    def _get_report_values(self, docids, data=None):
        docs = self.env['mini_store.invoice'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'mini_store.invoice',
            'docs': docs,
        }
