# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from collections import OrderedDict
from odoo.addons.payment.controllers import portal as payment_portal
from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from operator import itemgetter
from odoo.tools import groupby as groupbyelem
from odoo.osv.expression import OR, AND
from odoo.osv.expression import OR
from datetime import datetime



class CustomerPortal(payment_portal.PaymentPortal):


    def portal_my_orders(self, **kwargs):
        super(CustomerPortal, self).portal_my_orders()
        values = self._prepare_sale_portal_rendering_values(quotation_page=False, **kwargs)
        print("values final sales->",values)
        request.session['my_orders_history'] = values['orders'].ids[:100]
        groupby = values.get('groupby')
        print("base groupby1111->", groupby)
        if groupby != 'none':
            return request.render("portal_orders.portal_tasks_list_sale_groupby", values)
        return request.render("sale.portal_my_orders", values)

    def _prepare_sale_portal_rendering_values(
            self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='content',
            groupby=None, quotation_page=False, **kwargs
    ):
        print("custom def2-->")
        super(CustomerPortal, self)._prepare_sale_portal_rendering_values()
        if not groupby:
            groupby = 'none'
        SaleOrder = request.env['sale.order']
        groupby_list = {
            'none': {'input': 'none', 'label': _('None'), 'order': 1},
            'sam_received_date': {'input': 'sam_received_date', 'label': _('Use By Date'), 'order': 1},
            'option': {'input': 'option', 'label': _('Test Result'), 'order': 1},
            'date_order': {'input': 'date_order', 'label': _('Order Date'), 'order': 1},
            'amount_total': {'input': 'amount_total', 'label': _('Amount Total'), 'order': 1},
            'por_batch_number': {'input': 'por_batch_number', 'label': _('Batch Number'), 'order': 1},
        }
        date_order_group_by = groupby_list.get(groupby, {}).get("input", "")

        searchbar_filters = self._get_my_tasks_searchbar_filters_new()
        if not sortby:
            sortby = 'date'

        if not filterby:
            filterby = 'all'
        domain = searchbar_filters.get(filterby, searchbar_filters.get('all'))['domain']
        values = self._prepare_tasks_values_new(page, date_begin, date_end, sortby, search, search_in, groupby,
                                                domain=domain)
        print("valuesGRP->", values)
        partner = request.env.user.partner_id

        if quotation_page:
            url = "/my/quotes"
            domain = self._prepare_quotations_domain(partner)
        else:
            url = "/my/orders"
            domain = self._prepare_orders_domain(partner)

        searchbar_sortings = self._get_sale_searchbar_sortings()

        if search and search_in:
            search_domain = self._sale_get_search_domain(search_in, search)
            domain += search_domain

        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        sales_url = '/my/orders'
        pager_values = portal_pager(
            url=sales_url,
            total=SaleOrder.search_count(domain),
            page=page,
            step=self._items_per_page,
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby,
                      'filterby': filterby, 'groupby': groupby},
        )
        print("pager_values sale->", pager_values)
        orders = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager_values['offset'], )
        print("orders sale->", orders)

        if filterby != 'all':
            domain = searchbar_filters[filterby]['domain']
            orders = request.env['sale.order'].search(domain or [])

        if date_order_group_by == 'date_order':
            grouped_orders = []
            for key, group in groupbyelem(orders, key=lambda x: x.date_order.date()):
                date_group = {'date_order': key.strftime('%Y-%m-%d'), 'orders': list(group)}
                grouped_orders.append(date_group)
            date_order_list = grouped_orders
        elif date_order_group_by == 'amount_total':
            grouped_orders = []
            for key, group in groupbyelem(orders, key=lambda x: x.amount_total):
                amount_group = {'amount_total': key, 'orders': list(group)}
                grouped_orders.append(amount_group)
            date_order_list = grouped_orders
        elif date_order_group_by == 'por_batch_number':
            grouped_orders = []
            for key, group in groupbyelem(orders, key=lambda x: x.por_batch_number):
                batch_group = {'por_batch_number': key, 'orders': list(group)}
                grouped_orders.append(batch_group)
            date_order_list = grouped_orders
        elif date_order_group_by == 'sam_received_date':
            grouped_orders = []
            for key, group in groupbyelem(orders, key=lambda x: x.sam_received_date):
                batch_group = {'sam_received_date': key, 'orders': list(group)}
                grouped_orders.append(batch_group)
            date_order_list = grouped_orders
        elif date_order_group_by == 'option':
            grouped_orders = []
            for key, group in groupbyelem(orders, key=lambda x: x.option):
                batch_group = {'option': key, 'orders': list(group)}
                grouped_orders.append(batch_group)
            date_order_list = grouped_orders
        else:
            if groupby == 'none':
                date_order_list = [{'group_by_value': 'None', 'orders': [order]} for order in orders]
            else:
                date_order_list = [{'group_by_value': getattr(order, groupby), 'orders': [order]} for order in orders]
        print('------------------date_order_list', date_order_list)
        values.update({
            'date': date_begin,
            'quotations': orders.sudo() if quotation_page else SaleOrder,
            'orders': orders.sudo() if not quotation_page else SaleOrder,
            'page_name': 'quote' if quotation_page else 'order',
            'pager': pager_values,
            'default_url': url,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_groupby': groupby_list,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'searchbar_inputs': self._sale_get_searchbar_inputs(),  # Add search bar inputs
            'grouped_tasks': date_order_list,
        })
        print("orders values update->", values)
        return values


    def _sale_get_searchbar_inputs(self):
        values = {
            'all': {'input': 'all', 'label': _('Search in All'), 'order': 1},
            'name': {'input': 'name', 'label': _('Search in Name'), 'order': 2},
            'customer': {'input': 'customer', 'label': _('Search in Customer'), 'order': 3},
            'date': {'input': 'date', 'label': _('Search in Collection Date'), 'order': 4},
            'batch_number': {'input': 'batch_number', 'label': _('Search in Batch Number'), 'order': 5},
            'product': {'input': 'product', 'label': _('Search in Product Description'), 'order': 6},
            'result': {'input': 'result', 'label': _('Search in Test Result'), 'order': 7},
            'use_by': {'input': 'use_by', 'label': _('Search in Use By Date'), 'order': 8},
            'po_number': {'input': 'po_number', 'label': _('Search in PO Number'), 'order': 9},
        }
        return dict(sorted(values.items(), key=lambda item: item[1]["order"]))

    def _sale_get_search_domain(self, search_in, search):
        search_domain = []

        def is_valid_date(date_str):
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
                return True
            except ValueError:
                return False

        if search_in in ('name', 'all'):
            search_domain.append([('name', 'ilike', search)])
        if search_in in ('customer', 'all'):
            search_domain.append([('partner_id.name', 'ilike', search)])
        if search_in in ('date', 'all'):
            if is_valid_date(search):
                search_domain.append([('sam_test_com_date', '=', search)])
        if search_in in ('batch_number', 'all'):
            search_domain.append([('product_ids.batch_num', 'ilike', search)])
        if search_in in ('result', 'all'):
            search_domain.append([('order_line.result_pass_fail', 'ilike', search)])
        if search_in in ('product', 'all'):
            search_domain.append([('order_line.name', 'ilike', search)])
        if search_in in ('use_by', 'all'):
            if is_valid_date(search):
                search_domain.append([('product_ids.use_by_date_line', '=', search)])
        if search_in in ('po_number', 'all'):
            search_domain.append([('po_number', 'ilike', search)])

        return OR(search_domain)
    def _get_my_tasks_searchbar_filters_new(self, project_domain=None, task_domain=None):
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('name', '!=', False)]},
            'por_batch_number': {'label': _('Batch Number'), 'domain': [('product_ids.batch_num', '!=', False)]},
            'option_pass': {'label': _('Test Result: Pass'), 'domain': [('order_line.result_pass_fail', '=', 'pass')]},
            'option_fail': {'label': _('Test Result: Fail'), 'domain': [('order_line.result_pass_fail', '=', 'fail')]},
            'sam_received_date': {'label': _('Use By Date'), 'domain': [('product_ids.use_by_date_line', '!=', False)]},
            'date_order': {'label': _('Order Date'), 'domain': [('date_order', '!=', False)]},
        }
        print("custom def3")
        print("searchbar_filters", searchbar_filters)
        projects = request.env['sale.order'].search(project_domain or [])
        print("projects", projects)
        for project in projects:
            searchbar_filters.update({
                str(project.id): {'label': project.name, 'domain': [('name', '=', project.name)]}
            })
        print("searchbar_filters1", searchbar_filters)
        return searchbar_filters




    def _prepare_tasks_values_new(self, page, date_begin, date_end, sortby, search, search_in, groupby, url="/my/tasks", domain=None, su=False, project=False):
        values = self._prepare_portal_layout_values()


        return values