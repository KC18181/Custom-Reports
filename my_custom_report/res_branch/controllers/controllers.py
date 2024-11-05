# -*- coding: utf-8 -*-
# from odoo import http


# class ResBranch(http.Controller):
#     @http.route('/res_branch/res_branch/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/res_branch/res_branch/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('res_branch.listing', {
#             'root': '/res_branch/res_branch',
#             'objects': http.request.env['res_branch.res_branch'].search([]),
#         })

#     @http.route('/res_branch/res_branch/objects/<model("res_branch.res_branch"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('res_branch.object', {
#             'object': obj
#         })
