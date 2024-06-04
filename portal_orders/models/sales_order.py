# -*- coding: utf-8 -*-

#import of odoo
from odoo import api, fields, models, _
import base64
from datetime import datetime

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
        """ This method is used to generate an attachment for a PDF report"""
        self.ensure_one()
        sale_order = self

        # Prepare the data for the report
        data = {'docs': [sale_order]}

        # Get the report template
        report_ref = 'portal_orders.certification_test_report_template'
        report = self.env['ir.actions.report']._get_report_from_name(report_ref)

        if report:
            # Render the PDF
            pdf_content, _ = report._render(report_ref, res_ids=[sale_order.id], data=data)
            name = f"Certification_{sale_order.name}.pdf"
            pdf_data = base64.b64encode(pdf_content)

            # Create an attachment for the PDF report
            attachment = self.env['ir.attachment'].create({
                'name': name,
                'type': 'binary',
                'datas': pdf_data,
                'store_fname': name,
                'res_id': sale_order.id,
                'res_model': 'sale.order',
                'mimetype': 'application/pdf',
            })

            return attachment

    # def action_get_attachment(self):
    #     """ This method is used to generate attachment for pdf report"""
    #     docs = self.env['sale.order'].search([])
    #     print("docs->",docs)
    #     data = {'partner_statement': docs}
    #     # if not docs:
    #     #     notification = self.error()
    #     #     return notification
    #     #
    #     if data:
    #         template = self.env.ref('portal_orders.certification_test_report_template')
    #         print("template->", template)
    #         if template:
    #             pdf_report = self.env['ir.actions.report'].sudo()._render_qweb_pdf(
    #                 'portal_orders.action_print_pdf',
    #                 self, data=data)
    #             name = "Certification Report.pdf"
    #             print("pdf_report->", pdf_report)
    #             pdf_data = base64.b64encode(pdf_report[0])
    #             print("pdf_data->", pdf_data)
    #             # Create an attachment for the PDF report
    #             attachment = self.env['ir.attachment'].create({
    #                 'name': 'Certification.pdf',
    #                 'type': 'binary',
    #                 'datas': pdf_data,
    #                 'store_fname': name,
    #                 'res_id': self.id,
    #                 'res_model': 'sale.order',
    #                 'mimetype': 'application/pdf',
    #             })
    #             print("attachment->", attachment)
    #             return attachment

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

    sam_test_com_date = fields.Date("Collection Date")
    po_number = fields.Char("PO Number")
    special_requirements = fields.Text("Special Requirements")
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

    sample_delivery_date = fields.Date(string="Sample Delivery Date")
    sample_start_date = fields.Date(string="Sample Start Date")
    sample_ref = fields.Char(string="Sample Reference")
    date_of_result = fields.Date(string="Date of Result")

    product_ids = fields.One2many('product.line', 'order_id', string="Product")

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

    @api.depends('state')
    def _compute_type_name(self):
        for record in self:
            if record.state in ('draft', 'sent', 'cancel'):
                record.type_name = _("Quotation")
            else:
                record.type_name = _("Work Order")

class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    # # Pricing fields
    # tax_id = fields.Many2many(
    #     comodel_name='account.tax',
    #     string="Taxes",
    #     compute='_compute_tax_id',
    #     store=True,
    #     readonly=False,
    #     precompute=True,
    #     context={'active_test': False},
    #     check_company=True,
    #     default=lambda self: self.env['account.tax'].search(
    #         [('amount', '=', 20), ('type_tax_use', 'in', ['sale', 'purchase'])], limit=1)
    # )
    product_name = fields.Char(string="Product Name")

    test_result_type = fields.Selection([('pass_fail', 'Pass/Fail'),
                                         ('numerical', 'Numerical')], string='Test Result Type')
    test_result_nu = fields.Integer(string="Result")
    test_result_unit = fields.Text(string="Test Result Unit")
    result_pass_fail = fields.Selection([
        ('fail', 'Fail'),
        ('pass', 'Pass')],
        'Test Result', default='')


class PortalProduct(models.Model):
    _name = 'product.line'

    @api.model
    def create(self, vals):
        # Generate a sequence number with current date
        current_date = datetime.now().strftime('%m%d')
        sequence_number = self.env['ir.sequence'].next_by_code('product.line') or '/'
        vals['sequence'] = f'{current_date}{sequence_number}'

        return super(PortalProduct, self).create(vals)

    order_id = fields.Many2one(
        comodel_name='sale.order',
        string="Order Reference",
        required=True, ondelete='cascade', index=True, copy=False)

    sequence = fields.Char(string="OSL Sample Number")
    osl_sample_number = fields.Text(string="Sample Number")
    product_name_line = fields.Text(string="Product Name")
    use_by_date_line = fields.Date(string="Use By Date")
    sample_description = fields.Text(string="Sample Description")
    product_description = fields.Text(string="Product Description")
    batch_num = fields.Char(string="Batch Number")
    production_date = fields.Date(string="Production Date")
    test_parameter_1 = fields.Text(string="Test Parameter 1")
    test_parameter_2 = fields.Text(string="Test Parameter 2")
    test_parameter_3 = fields.Text(string="Test Parameter 3")
    test_parameter_4 = fields.Text(string="Test Parameter 4")
    test_parameter_5 = fields.Text(string="Test Parameter 5")
    test_parameter_6 = fields.Text(string="Test Parameter 6")
    test_parameter_7 = fields.Text(string="Test Parameter 7")
    test_parameter_8 = fields.Text(string="Test Parameter 8")
    test_parameter_9 = fields.Text(string="Test Parameter 9")
    test_parameter_10 = fields.Text(string="Test Parameter 10")


