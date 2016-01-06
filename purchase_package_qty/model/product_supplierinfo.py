# -*- encoding: utf-8 -*-
##############################################################################
#
#    Purchase - Package Quantity Module for Odoo
#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from lxml import etree

from openerp import models, fields, api, SUPERUSER_ID, _
from openerp.osv.orm import setup_modifiers
from openerp.addons import decimal_precision as dp


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    @api.model
    def fields_view_get(
            self, view_id=None, view_type='form',
            toolbar=False, submenu=False):
#        context = context and context or {}
        res = super(ProductSupplierinfo, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=False)
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            nodes = doc.xpath("//field[@name='package_qty']")
            if nodes:
                nodes[0].set('required', '1')
                setup_modifiers(nodes[0], res['fields']['package_qty'])
                res['arch'] = etree.tostring(doc)
        return res

    # Columns section
    package_qty = fields.Float(
        'Package Qty', digits_compute=dp.get_precision('Product UoM'),
        help="""The quantity of products in the supplier package."""
        """ You will always have to buy a multiple of this quantity.""",
        default=1)
    indicative_package = fields.Boolean(
        'Indicative Package',
        help="""If checked, the system will not force you to purchase"""
        """a strict multiple of package quantity""",
        default=False)

    # Constraints section
    @api.multi
    @api.constrains('package_qty')
    def _check_package_qty(self):
        for psi in self:
            if psi.package_qty == 0:
                raise ValueError(_('The package quantity cannot be 0.'))

    # Init section
    #TODO
    def _init_package_qty(self, cr, uid, ids=None, context=None):
        psi_ids = self.search(cr, SUPERUSER_ID, [], context=context)
        for psi in self.browse(cr, SUPERUSER_ID, psi_ids, context=context):
            package_qty = max(psi.min_qty, 1)
            self.write(
                cr, SUPERUSER_ID, psi.id, {'package_qty': package_qty},
                context=context)
        return psi_ids
