# -*- coding: utf-8 -*-
"""
Main controller for receiving leads from WordPress via Forminator.
"""

import json
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs

from werkzeug.wrappers import Response

from odoo import http
from odoo.http import request


def _j(payload, status=200):
    """Return a JSON response with a given status."""
    return Response(
        json.dumps(payload, ensure_ascii=False),
        status=status,
        content_type="application/json; charset=utf-8",
    )


class KTHLeadAPI(http.Controller):
    """HTTP controller that accepts leads from Forminator/WordPress."""

    @http.route(
        "/api/web_leads",
        type="json",
        auth="none",
        csrf=False,
        methods=["POST"],
    )
    def web_leads(self, **kwargs):
        """
        Accept a JSON payload and create a lead in the CRM.
        """

        # --- Enforce HTTPS ---
        proto = (
            request.httprequest.headers.get("X-Forwarded-Proto")
            or request.httprequest.scheme
        )
        if proto != "https":
            return _j({"error": "HTTPS required"}, status=400)

        # --- Token authentication ---
        # 1) Try Authorization header
        auth_header = request.httprequest.headers.get("Authorization") or ""
        provided_token = ""
        if auth_header.startswith("Bearer "):
            provided_token = auth_header[7:].strip()

        # 2) Fallback to query param (?token=...) for clients unable to set headers
        if not provided_token:
            qs = parse_qs(urlparse(request.httprequest.full_path).query or "")
            provided_token = (qs.get("token") or [""])[0].strip()

        # Compare against configured token
        conf_token = (
            request.env["ir.config_parameter"].sudo().get_param(
                "kth_web_bridge.api_token"
            )
            or ""
        )
        if not provided_token or provided_token != conf_token:
            return _j({"error": "Invalid or missing token"}, status=401)

        # --- Parse payload ---
        payload = request.jsonrequest or {}

        # Try to resolve field aliases commonly used by Forminator
        # full_name: 'full_name', 'name', 'first_name'+'last_name'
        full_name = (
            (payload.get("full_name") or payload.get("name") or "").strip()
            or " ".join(
                filter(
                    None,
                    [
                        str(payload.get("first_name") or "").strip(),
                        str(payload.get("last_name") or "").strip(),
                    ],
                )
            ).strip()
        )
        # email: 'email', 'email_address'
        email = (
            (payload.get("email") or payload.get("email_address") or "")
            .strip()
        )
        # message: 'message', 'comments', 'textarea', or first string starting with 'textarea'
        message = (
            (payload.get("message")
             or payload.get("comments")
             or payload.get("textarea")
             or "")
        )
        if isinstance(message, str):
            message = message.strip()
        else:
            message = ""
        # Attempt fallback: find a key starting with 'textarea'
        if not message:
            for k, v in payload.items():
                if isinstance(v, str) and k.lower().startswith("textarea"):
                    message = v.strip()
                    break

        if not (full_name and email and message):
            return _j(
                {
                    "error": "Required fields missing: full_name (or name), email, message",
                },
                status=400,
            )

        # Optional fields
        phone = (
            (payload.get("phone") or payload.get("telephone") or "")
            .strip()
        )
        page_url = (
            (payload.get("page_url") or payload.get("source_url") or "")
            .strip()
        )
        gdpr_consent = bool(payload.get("gdpr_consent"))
        utm_source = (payload.get("utm_source") or "").strip()
        utm_medium = (payload.get("utm_medium") or "").strip()
        utm_campaign = (payload.get("utm_campaign") or "").strip()

        # --- Duplicate check ---
        Lead = request.env["crm.lead"].sudo()
        since = datetime.utcnow() - timedelta(hours=24)
        existing = Lead.search(
            [
                ("email_from", "ilike", email),
                ("description", "=", message),
                ("create_date", ">", since),
            ],
            limit=1,
        )
        if existing:
            return _j(
                {
                    "status": "deduplicated",
                    "lead_id": existing.id,
                    "lead_name": existing.name,
                },
                status=409,
            )

        # --- Partner linking ---
        Partner = request.env["res.partner"].sudo()
        partner = Partner.search([("email", "ilike", email)], limit=1)

        # Create (or fetch) the 'Website' tag
        Tag = request.env["crm.tag"].sudo()
        tag = Tag.search([("name", "=", "Website")], limit=1)
        if not tag:
            tag = Tag.create({"name": "Website"})

        # Build lead values
        vals = {
            "type": "lead",
            "name": f"{full_name} - Website Inquiry",
            "contact_name": full_name,
            "email_from": email,
            "phone": phone or False,
            "description": message,
            "website": page_url or False,
            "x_gdpr_consent": gdpr_consent,
            "utm_source": utm_source or False,
            "utm_medium": utm_medium or False,
            "utm_campaign": utm_campaign or False,
            "tag_ids": [(6, 0, [tag.id])],
        }
        if partner:
            vals["partner_id"] = partner.id

        lead = Lead.create(vals)
        return _j(
            {
                "status": "created",
                "lead_id": lead.id,
                "lead_name": lead.name,
            },
            status=201,
        )