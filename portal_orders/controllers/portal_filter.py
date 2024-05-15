# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from collections import OrderedDict
from odoo.addons.payment.controllers import portal as payment_portal
from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortal(payment_portal.PaymentPortal):

    # def _prepare_sale_portal_rendering_values(
    #         self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='content',
    #         groupby=None, quotation_page=False, **kwargs
    # ):
    #     print("custom def2-->")
    #     super(CustomerPortal, self)._prepare_sale_portal_rendering_values()
    #     SaleOrder = request.env['sale.order']
    #     searchbar_filters = self._get_my_tasks_searchbar_filters_new()
    #     if not sortby:
    #         sortby = 'date'
    #
    #     if not filterby:
    #         filterby = 'all'
    #     domain = searchbar_filters.get(filterby, searchbar_filters.get('all'))['domain']
    #     values = self._prepare_tasks_values(page, date_begin, date_end, sortby, search, search_in, groupby,
    #                                         domain=domain)
    #     partner = request.env.user.partner_id
    #     # values = self._prepare_portal_layout_values()
    #
    #     if quotation_page:
    #         url = "/my/quotes"
    #         domain = self._prepare_quotations_domain(partner)
    #     else:
    #         url = "/my/orders"
    #         domain = self._prepare_orders_domain(partner)
    #
    #     searchbar_sortings = self._get_sale_searchbar_sortings()
    #
    #     sort_order = searchbar_sortings[sortby]['order']
    #
    #     if date_begin and date_end:
    #         domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
    #
    #     pager_values = portal_pager(
    #         url=url,
    #         total=SaleOrder.search_count(domain),
    #         page=page,
    #         step=self._items_per_page,
    #         url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby},
    #     )
    #     print("pager_values sale->", pager_values)
    #     orders = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager_values['offset'], )
    #     print("orders sale->", orders)
    #     if filterby != 'all':
    #         domain = [('id', '=', filterby)]
    #         orders = request.env['sale.order'].search(domain or [])
    #
    #     values.update({
    #         'date': date_begin,
    #         'quotations': orders.sudo() if quotation_page else SaleOrder,
    #         'orders': orders.sudo() if not quotation_page else SaleOrder,
    #         'page_name': 'quote' if quotation_page else 'order',
    #         'pager': pager_values,
    #         'default_url': url,
    #         'searchbar_sortings': searchbar_sortings,
    #         'sortby': sortby,
    #         'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
    #         'filterby': filterby,
    #     })
    #     print("orders values update->", values)
    #     return values

    def _get_my_tasks_searchbar_filters_new(self, project_domain=None, task_domain=None):
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('name', '!=', False)]},
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

    def _prepare_sale_portal_rendering_values(
            self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='content',
            groupby=None, quotation_page=False, **kwargs
    ):
        SaleOrder = request.env['sale.order']
        searchbar_filters = self._get_my_tasks_searchbar_filters_new()
        if not sortby:
            sortby = 'date'
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters.get(filterby, searchbar_filters.get('all'))['domain']
        if groupby:
            # Adjust domain based on group by field
            groupby_mapping = self._task_get_groupby_mapping()
            groupby_field = groupby_mapping.get(groupby)
            if groupby_field:
                if groupby_field == 'date':  # Handle special case for grouping by date
                    domain += [('create_date', '!=', False)]
                else:
                    domain += [(groupby_field, '!=', False)]
        partner = request.env.user.partner_id
        if quotation_page:
            url = "/my/quotes"
            domain = self._prepare_quotations_domain(partner)
        else:
            url = "/my/orders"
            domain += self._prepare_orders_domain(partner)
        searchbar_sortings = self._get_sale_searchbar_sortings()
        sort_order = searchbar_sortings[sortby]['order']
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        pager_values = portal_pager(
            url=url,
            total=SaleOrder.search_count(domain),
            page=page,
            step=self._items_per_page,
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'groupby': groupby},
        )
        orders = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager_values['offset'])
        if filterby != 'all':
            domain = [('id', '=', filterby)]
            orders = request.env['sale.order'].search(domain or [])
        values = {
            'date': date_begin,
            'quotations': orders.sudo() if quotation_page else SaleOrder,
            'orders': orders.sudo() if not quotation_page else SaleOrder,
            'page_name': 'quote' if quotation_page else 'order',
            'pager': pager_values,
            'default_url': url,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'groupby': groupby,
        }
        return values


    # def _prepare_tasks_values(self, page, date_begin, date_end, sortby, search, search_in, groupby, url="/my/tasks", domain=None, su=False, project=False):
    #     values = self._prepare_portal_layout_values()
    #     print("valuesp-->",values)
    #     Task = request.env['project.task']
    #     milestone_domain = AND([domain, [('allow_milestones', '=', 'True')]])
    #     milestones_allowed = Task.sudo().search_count(milestone_domain, limit=1) == 1
    #     searchbar_sortings = dict(sorted(self._task_get_searchbar_sortings(milestones_allowed, project).items(),
    #                                      key=lambda item: item[1]["sequence"]))
    #     searchbar_inputs = self._task_get_searchbar_inputs(milestones_allowed, project)
    #     searchbar_groupby = self._task_get_searchbar_groupby(milestones_allowed, project)
    #
    #     if not domain:
    #         domain = []
    #     if not su and Task.check_access_rights('read'):
    #         domain = AND([domain, request.env['ir.rule']._compute_domain(Task._name, 'read')])
    #     Task_sudo = Task.sudo()
    #
    #     # default sort by value
    #     if not sortby or (sortby == 'milestone' and not milestones_allowed):
    #         sortby = 'date'
    #     order = searchbar_sortings[sortby]['order']
    #
    #     # default group by value
    #     if not groupby or (groupby == 'milestone' and not milestones_allowed):
    #         groupby = 'project'
    #
    #     if date_begin and date_end:
    #         domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
    #
    #     # search reset if needed
    #     if not milestones_allowed and search_in == 'milestone':
    #         search_in = 'all'
    #     # search
    #     if search and search_in:
    #         domain += self._task_get_search_domain(search_in, search)
    #
    #     # content according to pager and archive selected
    #     order = self._task_get_order(order, groupby)