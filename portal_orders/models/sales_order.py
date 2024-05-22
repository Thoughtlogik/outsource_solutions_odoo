# -*- coding: utf-8 -*-

#import of odoo
from odoo import api, fields, models
import base64

#inheriting the TAX model
class Tax(models.Model):
    
    _inherit = 'account.tax'
    
    children_tax_ids = fields.Many2many('account.tax',
        'account_tax_filiation_rel', 'parent_tax', 'child_tax',
        check_company=True,
        string='Children Taxes')

#Inherit the sale order
class SaleOrder(models.Model):
    
    _inherit = 'sale.order'

    def action_get_attachment(self):
        """ This method is used to generate attachment for pdf report"""
        docs = self.env['sale.order'].search([])
        print("docs->",docs)
        data = {'partner_statement': docs}
        # if not docs:
        #     notification = self.error()
        #     return notification
        #
        if data:
            template = self.env.ref('portal_orders.certification_report_template')
            print("template->", template)
            if template:
                pdf_report = self.env['ir.actions.report'].sudo()._render_qweb_pdf(
                    'portal_orders.action_print_pdf',
                    self, data=data)
                name = "Certification Report.pdf"
                print("pdf_report->", pdf_report)
                pdf_data = base64.b64encode(pdf_report[0])
                print("pdf_data->", pdf_data)
                # Create an attachment for the PDF report
                attachment = self.env['ir.attachment'].create({
                    'name': 'Certification.pdf',
                    'type': 'binary',
                    'datas': pdf_data,
                    'store_fname': name,
                    'res_id': self.id,
                    'res_model': 'sale.order',
                    'mimetype': 'application/pdf',
                })
                print("attachment->", attachment)
                return attachment

    @api.onchange('option')
    def _onchange_status(self):
        if self.option in ['fail', 'pass']:
            self.portal_state = 'testing_complete'
        else:
            self.portal_state = 'new'

    option = fields.Selection([
        ('fail', 'Fail'),
        ('pass', 'Pass')],
        'Test Result', default='')

    portal_state = fields.Selection([
        ('new', 'New'),
        ('sample_received', 'Sample Received'),
        ('test_in_progress', 'Test In Progress'),
        ('testing_complete', 'Test Completed'),
    ], string='Status', default='new')

    sam_test_com_date = fields.Date("Production date")
    sam_received_date = fields.Date("Use By Date")
    sample_booking_date = fields.Date("Analysis Request Date")

    por_description = fields.Text("Sample Description")
    # por_type = fields.Char("Type")
    por_batch_number = fields.Char("Batch Number")
    por_analysis_type = fields.Char("Analysis type")
    analysis_start = fields.Datetime(string="Analysis Start")
    analysis_finish = fields.Datetime("Analysis Finish")
    # relevent_temperatures = fields.decimal()
    analyst_name = fields.Many2one('hr.employee', string='Analyst Name')
    test_parameter_1 = fields.Text(string='Test Parameter 1')
    test_parameter_2 = fields.Text(string='Test Parameter 2')
    test_parameter_3 = fields.Text(string='Test Parameter 3')
    test_parameter_4 = fields.Text(string='Test Parameter 4')
    test_parameter_5 = fields.Text(string='Test Parameter 5')
    test_parameter_6 = fields.Text(string='Test Parameter 6')
    test_parameter_7 = fields.Text(string='Test Parameter 7')
    test_parameter_8 = fields.Text(string='Test Parameter 8')
    test_parameter_9 = fields.Text(string='Test Parameter 9')
    test_parameter_10 = fields.Text(string='Test Parameter 10')
    relevant_temperatures = fields.Float(string="Relevant Temperatures")

    collection_or_delivery = fields.Selection([('collection', 'Collection'),
                                               ('delivery', 'Delivery')], string='Collection/Delivery')

    collection_address = fields.Char(string='Collection Address')

    # def get_the_price_list(self,partner):
    #     partner_id = self.env['res.partner'].search([('name', '=', partner)])
    #     price_name = partner_id.property_product_pricelist.id
    #     return price_name


    def generate_certification_pdf(self):
        return self.env.ref('portal_orders.action_print_pdf').report_action(self)

    @api.model
    def export_sale_order_data(self):
        # Retrieve the sale.order data
        sale_orders = self.search([])  # Example: Retrieve all sale orders
        # Perform any additional processing if needed
        return sale_orders

# # Inherit the sale order
# class Lead(models.Model):
#
#     _inherit = 'crm.lead'
#
#     preferred_call_back_date = fields.Date("Preferred Callback Date")
#     call_back_time_from_new_float = fields.Float("Callback time from")
#     # call_back_time_to = fields.Float("Callback time to")

