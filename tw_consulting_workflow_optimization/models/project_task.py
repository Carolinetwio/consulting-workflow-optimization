# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.osv import expression
from odoo.addons.project.models.project_task import PROJECT_TASK_READABLE_FIELDS

PROJECT_TASK_READABLE_FIELDS.update({
    'tw_currency_id',
    'tw_initially_planned_budget',
    'tw_budget_spent',
    'tw_remaining_budget',
    'tw_budget_progress',
})

class ProjectTask(models.Model):
    _inherit = 'project.task'

    tw_initially_planned_budget = fields.Float(
        string='Initially Planned Budget',
        compute='_compute_budget',
        store=True,
        help="This value is composed of the Initially Allocated Hours and the Unit Price on the Sales Order Lines."
    )

    tw_currency_id = fields.Many2one(
        related='sale_line_id.currency_id',
        string='Currency'
    )

    tw_budget_spent = fields.Float(
        string='Budget Spent',
        compute='_compute_budget',
        store=True,
        help="This value is composed of the hours booked and the Unit Price on the Sales Order Lines."
    )

    tw_remaining_budget = fields.Float(
        string='Remaining Budget',
        compute='_compute_budget',
        store=True,
        help="This value is composed of the diefference between the Initially Planned Budget and the Budget Spent."
    )

    tw_budget_progress = fields.Float(
        string='Budget Status',
        compute='_compute_budget',
        store=True,
    )

    tw_total_allocated_hours = fields.Float(string="Total Allocated Time", compute="_compute_total_allocated_hours")

    tw_total_remaining_hours = fields.Float(string="Total Remaining Hours", compute="_compute_total_remaining_hours")

    @api.depends('allocated_hours', 'effective_hours', 'sale_line_id.price_unit', 'sale_line_id.discount')
    def _compute_budget(self):
        for task in self:
            initially_planned_budget = 0.00
            budget_spent = 0.00
            sale_line_id = task.sale_line_id

            if (sale_line_id and
                sale_line_id.product_uom.category_id.id == self.env.ref('uom.uom_categ_wtime').id):

                uom_type = sale_line_id.product_uom.uom_type

                for timesheet in task.timesheet_ids.filtered(lambda analytic_line: analytic_line.so_line == sale_line_id):
                    budget_spent_hours = timesheet.unit_amount * sale_line_id.price_unit * (1.0 - sale_line_id.discount / 100.0)
                    # Reference (days), should then divide by 8
                    if uom_type == 'reference':
                        budget_spent += budget_spent_hours / 8
                    # Smaller reference: hours, should then just multiple
                    elif uom_type == 'smaller':
                        budget_spent += budget_spent_hours
                    # Bigger reference: e.g weeks, should then do divided by the ratio
                    elif uom_type == 'bigger':
                        budget_spent += budget_spent_hours / sale_line_id.product_uom.ratio

                planned_budget_hours = task.allocated_hours * sale_line_id.price_unit * (1.0 - sale_line_id.discount / 100.0)
                # Reference (days), should then divide by 8
                if uom_type == 'reference':
                    initially_planned_budget = planned_budget_hours / 8
                # Smaller reference: hours, should then just multiple
                elif uom_type == 'smaller':
                    initially_planned_budget = planned_budget_hours
                # Bigger reference: e.g weeks, should then do divided by the ratio
                elif uom_type == 'bigger':
                    initially_planned_budget = planned_budget_hours / sale_line_id.product_uom.ratio

            task.tw_initially_planned_budget = initially_planned_budget
            task.tw_budget_spent = budget_spent
            task.tw_remaining_budget = initially_planned_budget - budget_spent
            task.tw_budget_progress = (budget_spent / initially_planned_budget) * 100 if initially_planned_budget > 0 else 0.00

    @api.depends('allocated_hours', 'subtask_allocated_hours')
    def _compute_total_allocated_hours(self):
        for task in self:
            task.tw_total_allocated_hours = task.allocated_hours + task.subtask_allocated_hours

    @api.depends('tw_total_allocated_hours', 'total_hours_spent')
    def _compute_total_remaining_hours(self):
        for task in self:
            task.tw_total_remaining_hours = task.tw_total_allocated_hours - task.total_hours_spent
