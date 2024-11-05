from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # Related field for the Manager of the user (connected via user_id)
    parent_id = fields.Many2one('hr.employee', string="Manager", readonly=True)

    # Related field for the Coach of the user (connected via user_id)
    coach_id = fields.Many2one('hr.employee', string="Coach", readonly=True)

    @api.onchange('user_id')
    def _onchange_user_id(self):
        """Onchange method to update parent_id and coach_id based on the selected user."""
        if self.user_id and self.user_id.employee_ids:
            employee = self.user_id.employee_ids[0]
            # Update the manager (parent_id) and coach based on the selected user
            self.parent_id = employee.parent_id.id if employee.parent_id else False
            self.coach_id = employee.coach_id.id if employee.coach_id else False

    # def write(self, vals):
    #     """Override write method to update the coach_id and parent_id whenever the purchase order is updated."""
    #     # Get the user updating the record
    #     user = self.env['res.users'].browse(self._uid)
        
    #     if user and user.employee_ids:
    #         employee = user.employee_ids[0]
    #         # Update the coach_id and parent_id from the employee's record
    #         vals['coach_id'] = employee.coach_id.id if employee.coach_id else False
    #         vals['parent_id'] = employee.parent_id.id if employee.parent_id else False

    #     # Call the original write method with updated values
    #     return super(PurchaseOrder, self).write(vals)