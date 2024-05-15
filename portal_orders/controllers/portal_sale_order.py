# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request, route, Controller
from odoo.exceptions import AccessError
import math
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
import csv
from io import StringIO, BytesIO
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class PortalSaleOrder(http.Controller):
    #URL Re directed to sale order
    @http.route(['/orders'], type='http', auth="user", website=True)
    def sent_details_to_portal(self, **kw):
        values = {}
        user_id = request.session.uid
        customer_id = request.env['res.partner'].sudo().search([])
        payment_id = request.env['account.payment.term'].sudo().search([])
        product_uom_id = request.env['uom.uom'].sudo().search([])
        # price_id = request.env['product.pricelist'].sudo().search([])
        product_id = request.env['product.product'].sudo().search([])
        analytic_id = request.env['account.analytic.account'].sudo().search([])
        children_tax_ids = request.env['account.tax'].sudo().search([])
        values['customer_id'] = customer_id
        values['payment_id'] = payment_id
        # values['price_id'] = price_id
        values['product_id'] = product_id
        values['product_uom_id'] = product_uom_id
        values['analytic_id'] = analytic_id
        values['children_tax_ids'] = children_tax_ids
        values['page_name'] = 'quotation'
        return request.render('portal_orders.sale_order_design',values)
    
#get the values from sale order and create the new sale order
    @http.route('/create_sale_order', type='http', auth="user", website=True)
    def get_values_and_create(self, **post):
        print("post-->",post)
        des = ''
        type = ''
        sale = ''
        product_id = ''
        expiration_date = ''
        quotation_date = ''
        product_ids = ''
        payment_ids = ''
        pricelist_id = ''
        batch_number_input = ''
        analytic_ids = ''
        product_info = {}
        requested_by_id = post.get('requested_by')

        # Fetch the partner record from the database
        partner = request.env['res.partner'].sudo().browse(int(requested_by_id))
        print("requested_by_name->", partner)
        # Get the name of the partner
        requested_by_name = partner.name
        print("requested_by_name->",requested_by_name)
        for key, value in post.items():
            if key.startswith('product_name_'):
                idx = key.split('_')[2]
                product_info[idx] = {'name': value,
                                     'description': post.get(f'description_{idx}'),
                                     'quantity': post.get(f'qty_{idx}'),
                                     'unit': post.get(f'product_uom_{idx}'),
                                     'unit_price': post.get(f'price_unit_{idx}'),
                                     'tax_ids': post.get(f'tax_emp_{idx}'),
                                     'discount': post.get(f'discount_{idx}'),
                                     'subtotal': post.get(f'price_subtotal_{idx}'),
                                      'tax_ids': post.get(f'tax_emp_{idx}')}
        order_lines = []
        if product_info:
            for idx, item in product_info.items():
                split =item['name'].split(' ')
                product_ref = split[0]
                tax = []
                lst = ''
                if item['tax_ids']:
                    tax_rep = item['tax_ids']
                    tax.append(tax_rep)
                    tax_cat = tax[0]
                    li = list(tax_cat.split(",")) 
                    lst = [int(x) if x.isdigit() else float(x) for x in li]
                product_id = request.env['product.product'].sudo().search([('default_code', '=', product_ref)])
                uom_id = request.env['uom.uom'].sudo().search([('name', '=', item['unit'])])
                description = item['name'].split('{')
                order_line = {
                    'product_id': product_id.id,
                    'name': description[0],
                    'product_uom_qty': float(item['quantity']),
                    'product_uom': uom_id.id,
                    'price_unit': float(item['unit_price']),
                    'discount': float(item['discount']) if item['discount'] else 0.0,
                    'tax_id': [(6, 0,lst)],
                    'price_subtotal': float(item['subtotal']),
                }
                # order_lines.append((0, 0, order_line))
                order_lines.append((0,0,order_line))
        partner_name = post.get('partner')
        customer_id = request.env['res.partner'].sudo().search([('name', '=', partner_name)])
        price_name = post.get('price')
        if price_name:
            pricelist = request.env['product.pricelist'].search([('id', '=', price_name)])
            pricelist_id = pricelist.id
        payment = post.get('payment')
        if payment:
            payment_id = request.env['account.payment.term'].search([('name', '=', payment)])
            payment_ids = payment_id.id
        product = post.get('product')
        quantity = post.get('qty')
        analytic = post.get('analytic')
        if analytic:
            analytic_id = request.env['account.analytic.account'].search([('name', '=', analytic)])
            analytic_ids = analytic_id.id
        subtotal = post.get('price_subtotal')
        product_uom = post.get('product_uom')
        uom = request.env['uom.uom'].search([('name', '=', product_uom)])
        if product:
            product_id = request.env['product.product'].search([('default_code', '=', product.split("'")[1])])
            product_ids = product_id.id
        if partner_name:
            sale = request.env['sale.order'].sudo().create({
                'partner_id': customer_id.id,
                'payment_term_id': payment_ids,
                # 'pricelist_id': pricelist_id,
                'analytic_account_id': analytic_ids,
                'state':'sale',

                })
            # if  post.get('expiration'):
            #     sale.update({'validity_date': post.get('expiration')})
            if  post.get('sample_description'):
                sale.update({'por_description': post.get('sample_description')})
            if  post.get('type'):
                sale.update({'por_type': post.get('type')})
            if  post.get('batch_number'):
                sale.update({'por_batch_number': post.get('batch_number')})
            if  post.get('use_by_date'):
                sale.update({'sam_received_date': post.get('use_by_date')})
            if  post.get('production_date'):
                sale.update({'sam_test_com_date': post.get('production_date')})
            if post.get('test_result'):
                sale.update({'option': post.get('test_result')})
            if post.get('collection_delivery'):
                sale.update({'collection_or_delivery': post.get('collection_delivery')})
            if post.get('test_parameter_1'):
                sale.update({'test_parameter_1': post.get('test_parameter_1')})
            if post.get('test_parameter_2'):
                sale.update({'test_parameter_2': post.get('test_parameter_2')})
            if post.get('test_parameter_3'):
                sale.update({'test_parameter_3': post.get('test_parameter_3')})
            if post.get('test_parameter_4'):
                sale.update({'test_parameter_4': post.get('test_parameter_4')})
            if post.get('test_parameter_5'):
                sale.update({'test_parameter_5': post.get('test_parameter_5')})
            if post.get('test_parameter_6'):
                sale.update({'test_parameter_6': post.get('test_parameter_6')})
            if post.get('test_parameter_7'):
                sale.update({'test_parameter_7': post.get('test_parameter_7')})
            if post.get('test_parameter_8'):
                sale.update({'test_parameter_8': post.get('test_parameter_8')})
            if post.get('test_parameter_9'):
                sale.update({'test_parameter_9': post.get('test_parameter_9')})
            if post.get('test_parameter_10'):
                sale.update({'test_parameter_10': post.get('test_parameter_10')})
            if partner:
                sale.update({'partner_id': partner})
            # if requested_by_name:
            #     sale.update({'partner_id': requested_by_name})
            if post.get('Analysis_Request_Date'):
                sale.update({'sample_booking_date': post.get('Analysis_Request_Date')})
            # if post.get('quotation'):
            #     sale.update({'date_order': post.get('quotation')})
            if order_lines:   
                sale.update({'order_line': order_lines})
        return request.redirect('my/orders#')

    # @http.route('/export/timesheets/records', methods=['POST'], type='http',
    #             auth='user', website=True, csrf=False)
    # def export_record(self, **kw):
    #     print("POST->", kw)
    #     timesheet_ids = kw.get('checked')  # Assuming 'checked' contains a list of IDs
    #     print("timesheet_ids->", timesheet_ids)
    #
    #     # # Convert IDs to integers
    #     # timesheet_ids = [int(id) for id in timesheet_ids]
    #
    #
    #     # Use the search method to retrieve Sale Orders based on the IDs
    #     sale_orders = http.request.env['sale.order'].search([('id', '=', timesheet_ids)])
    #     print("sale_orders:", sale_orders)
    #
    #     # Extract name field value of each sale order
    #     # sale_order_names = [order.name for order in sale_orders]
    #     # print("Sale Order Names:", sale_order_names)
    #
    #     if sale_orders:
    #         csv_data = StringIO()
    #         csv_writer = csv.writer(csv_data)
    #         csv_writer.writerow(['Order Number', 'Order Date', 'Test Result','Total'])
    #
    #         for order in sale_orders:
    #             csv_writer.writerow([order.name, order.date_order, order.amount_total])
    #
    #         csv_data.seek(0)
    #         csv_content = csv_data.getvalue()
    #         csv_data.close()
    #
    #         return request.make_response(
    #             csv_content,
    #             headers=[
    #                 ('Content-Type', 'text/csv'),
    #                 ('Content-Disposition', 'attachment; filename="sale_orders.csv"'),
    #             ]
    #         )
    #     else:
    #         return request.redirect("/my/orders")

    @http.route('/portal/export_sale_orders', type='http', auth="user", website=True)
    def export_sale_orders(self, **kw):
        orders = request.env['sale.order'].sudo().search(
            ['&', ('partner_id', '=', request.env.user.partner_id.id), ('state', '=', 'sale')])
        print(orders)
        if orders:
            csv_data = StringIO()
            csv_writer = csv.writer(csv_data)
            csv_writer.writerow(['Order Number', 'Order Date', 'Test Result', 'Batch Number', 'Description', 'Sample Booking Date', 'Sample Received Date', 'Sample Test Completion Date', 'Total'])

            for order in orders:
                csv_writer.writerow([order.name, order.date_order, order.option, order.por_batch_number, order.por_description, order.sample_booking_date, order.sam_received_date, order.sam_test_com_date, order.amount_total])

            csv_data.seek(0)
            csv_content = csv_data.getvalue()
            csv_data.close()

            return request.make_response(
                csv_content,
                headers=[
                    ('Content-Type', 'text/csv'),
                    ('Content-Disposition', 'attachment; filename="sale_orders.csv"'),
                ]
            )
        else:
            return request.redirect("/my/orders")

    @http.route('/portal/export_sale_order/button', type='http', auth="user", website=True)
    def export_sale_order(self, order_id=None, **kw):
        order = request.env['sale.order'].sudo().browse(int(order_id))

        if order:
            csv_data = StringIO()
            csv_writer = csv.writer(csv_data)
            csv_writer.writerow(['Order Number', 'Order Date', 'Test Result', 'Batch Number', 'Description', 'Sample Booking Date', 'Sample Received Date', 'Sample Test Completion Date', 'Total'])
            csv_writer.writerow([order.name, order.date_order, order.option, order.por_batch_number, order.por_description, order.sample_booking_date, order.sam_received_date, order.sam_test_com_date, order.amount_total])

            csv_data.seek(0)
            csv_content = csv_data.getvalue()
            csv_data.close()

            return request.make_response(
                csv_content,
                headers=[
                    ('Content-Type', 'text/csv'),
                    ('Content-Disposition', 'attachment; filename="sale_order_{}.csv"'.format(order.name)),
                ]
            )
        else:
            return request.redirect("/my/orders")

    # @http.route('/portal/print_report', type='http', auth="user", website=True)
    # def print_report(self,  **kw):
    #     data = {
    #         'form_data': request.env['sale.order'].search([]),
    #     }
    #     pdf, _ = request.env.ref('portal_orders.action_print_pdf').report_action(self, data=data)
    #
    #     return request.make_response(
    #         pdf,
    #         headers=[
    #             ('Content-Type', 'application/pdf'),
    #             ('Content-Disposition', 'attachment; filename=report.pdf'),
    #         ]
    #     )

    @http.route('/portal/print_report', type='http', auth="user", website=True)
    def print_report(self, **kw):
        active_id = request.env.context.get('active_id')
        report_ref = 'portal_orders.certification_report_template'
        report = request.env['ir.actions.report']._get_report_from_name(report_ref)
        pdf, _ = report._render(report_ref, res_ids=[active_id], data={})

        return request.make_response(
            pdf,
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', 'attachment; filename=Certification.pdf'),
            ]
        )

    @http.route('/portal/export_invoices/button', type='http', auth="user", website=True)
    def export_invoice(self, invoice_id=None, **kw):
        invoice = request.env['account.move'].sudo().browse(int(invoice_id))

        if invoice:
            # Determine the status of the invoice
            if invoice.state == 'posted' and invoice.payment_state not in ('in_payment', 'paid', 'reversed'):
                status = 'Waiting for Payment'
            elif invoice.state == 'posted' and invoice.payment_state in ('paid', 'in_payment'):
                status = 'Paid'
            elif invoice.state == 'posted' and invoice.payment_state == 'reversed':
                status = 'Reversed'
            elif invoice.state == 'cancel':
                status = 'Cancelled'
            else:
                status = 'Unknown'

            csv_data = StringIO()
            csv_writer = csv.writer(csv_data)
            csv_writer.writerow(['Invoice', 'Invoice Date', 'Due Date', 'Status', 'Amount Due'])
            csv_writer.writerow(
                [invoice.name, invoice.invoice_date, invoice.invoice_date_due, status, invoice.amount_residual])

            csv_data.seek(0)
            csv_content = csv_data.getvalue()
            csv_data.close()

            return request.make_response(
                csv_content,
                headers=[
                    ('Content-Type', 'text/csv'),
                    ('Content-Disposition', 'attachment; filename="invoice_{}.csv"'.format(invoice.name)),
                ]
            )
        else:
            return request.redirect("/my/orders")

    @http.route('/portal/export_invoices', type='http', auth="user", website=True)
    def export_invoices_doc(self, **kw):
        invoices = request.env['account.move'].sudo().search(
            ['&', ('partner_id', '=', request.env.user.partner_id.id), ('move_type', '=', 'out_invoice')])
        if invoices:
            csv_data = StringIO()
            csv_writer = csv.writer(csv_data)
            csv_writer.writerow(['Invoice', 'Invoice Date', 'Due Date', 'Status', 'Amount Due'])

            for invoice in invoices:
                # Determine the status of the invoice
                if invoice.state == 'posted' and invoice.payment_state not in ('in_payment', 'paid', 'reversed'):
                    status = 'Waiting for Payment'
                elif invoice.state == 'posted' and invoice.payment_state in ('paid', 'in_payment'):
                    status = 'Paid'
                elif invoice.state == 'posted' and invoice.payment_state == 'reversed':
                    status = 'Reversed'
                elif invoice.state == 'cancel':
                    status = 'Cancelled'
                else:
                    status = 'Unknown'

                csv_writer.writerow(
                    [invoice.name, invoice.invoice_date, invoice.invoice_date_due, status, invoice.amount_residual])

            csv_data.seek(0)
            csv_content = csv_data.getvalue()
            csv_data.close()

            return request.make_response(
                csv_content,
                headers=[
                    ('Content-Type', 'text/csv'),
                    ('Content-Disposition', 'attachment; filename="invoices.csv"'),
                ]
            )
        else:
            return request.redirect("/my/orders")

    @http.route(['/my/orders','/my/orders/page/<int:page>'], type='http',website=True)
    def weblearnsStudentListView(self,page=1, sortby='id', search="", search_in="All", **kw):
        search_list = {
            'All': {'label':'All','input':'all','domain':[]},
            'Name': {'label': 'Sale Order', 'input': 'Sale Order','domain':[('name','ilike',search)]},

        }
        search_domain = search_list[search_in]['domain']

        order_obj = request.env['sale.order']
        total_orders = order_obj.search_count(search_domain)

        pager = portal_pager(
            url="/my/orders",
            url_args={'search_in':search_in,'search':search},
            total=total_orders,
            page=page,
            step=5
        )
        orders = order_obj.search(search_domain, limit=5, offset=pager['offset'])

        vals =({
            'order':orders,
            'pager': pager,
            'search_in': search_in,
            'searchbar_inputs': search_list,
            'search':search
        })
        return vals




