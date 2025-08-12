
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Partner(models.Model):
    _inherit = 'res.partner'

    @api.constrains('parent_id')
    def _check_parent_not_child(self):
        """Ensure the parent is not in the partner's descendants.

        Using the ``child_ids`` relationship on partners, we walk up the
        hierarchy and check that the chosen parent isn't already in
        the current partner's children.  If it is, we raise an
        exception to avoid the recursive loop that can occur during
        display name computation【360600524898825†L1641-L1649】.
        """
        for partner in self:
            if partner.parent_id:
                # Build a set of all child partner ids using recursion
                children = set()

                def _collect_children(p):
                    for child in p.child_ids:
                        if child.id not in children:
                            children.add(child.id)
                            _collect_children(child)

                _collect_children(partner)
                if partner.parent_id.id in children:
                    raise ValidationError(_(
                        'You cannot assign a parent that is a child of this contact. '
                        'Selecting this parent would create a recursive loop.'
                    ))