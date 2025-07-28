from odoo import models, fields, api
from markupsafe import escape

class SiteVisitBreadcrumbMixin(models.AbstractModel):
    _name = "site.visit.breadcrumb.mixin"
    _description = "Breadcrumb mixin using path traversal"

    breadcrumb_html = fields.Html(
        string="Breadcrumb:", compute="_compute_breadcrumb_html", store=False
    )

    @api.depends()
    def _compute_breadcrumb_html(self):
        for rec in self:
            chain = rec._get_breadcrumb_chain()
            crumbs = []
            current = rec

            for field_name, name_field in chain:
                chain_related = getattr(current, field_name, None)
                if chain_related and chain_related.exists():
                    crumbs.insert(0, {
                        "name": getattr(chain_related, name_field),
                        "model": chain_related._name,
                        "id": chain_related.id,
                    })
                    current = chain_related
                else:
                    break  # Stop if any part of the chain is missing

            # Add self
            crumbs.append({
                "name": getattr(rec, "name", "Unnamed"),
                "model": rec._name,
                "id": rec.id,
            })

            # Build HTML breadcrumb
            parts = []
            for i, crumb in enumerate(crumbs):
                label = escape(crumb["name"])
                parts.append(f"<span>{label}</span>")
                if i < len(crumbs) - 1:
                    parts.append(" &raquo; ")

            rec.breadcrumb_html = "".join(parts)

    def _get_breadcrumb_chain(self):
        """Return a list of (field_name, field_display_name) from current to root."""
        return []
