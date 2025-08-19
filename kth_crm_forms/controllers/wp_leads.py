# -*- coding: utf-8 -*-
import json, logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

def _get(data, *keys):
    """Return first non-empty value among keys; accepts -/_ variants."""
    for k in keys:
        for cand in (k, k.replace('-', '_'), k.replace('_', '-')):
            v = data.get(cand)
            if isinstance(v, str):
                v = v.strip()
            if v:
                return v
    return None

class SimpleFormOpportunitiesController(http.Controller):

    @http.route(
        ["/api/web_leads", "/api/web_leads/"],
        type="http", auth="public", csrf=False,
        methods=["GET", "POST", "OPTIONS"],
    )
    def api_web_leads(self, **_kw):
        method = request.httprequest.method
        _logger.info(">>> Webhook called with method: %s", method)

        if method == "OPTIONS":
            resp = request.make_json_response({"ok": True}, status=204)
            resp.headers["Access-Control-Allow-Origin"] = "*"
            resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
            resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            return resp

        if method == "GET":
            resp = request.make_json_response({"ok": True, "message": "Webhook ready"}, status=200)
            resp.headers["Access-Control-Allow-Origin"] = "*"
            return resp

        # ----- POST -----
        ctype = (request.httprequest.headers.get("Content-Type") or "").lower()
        _logger.info(">>> POST Content-Type: %s", ctype)

        if "application/json" in ctype:
            try:
                raw = request.httprequest.get_data() or b"{}"
                data = json.loads(raw.decode("utf-8"))
                if not isinstance(data, dict):
                    data = {}
            except Exception as e:
                _logger.error(">>> JSON parse error: %s", e)
                data = {}
        else:
            data = dict(request.params or {})

        _logger.info(">>> Payload: %s", data)
        request.env["ir.config_parameter"].sudo().set_param(
            "kth.last_webhook_payload", json.dumps(data, ensure_ascii=False)
        )

        first_name = _get(data, "name-1", "name_1", "name", "full_name") or "Web Opportunity"
        email      = _get(data, "email-1", "email_1", "email")
        phone      = _get(data, "phone-1", "phone_1", "phone")
        message    = _get(data, "textarea-1", "textarea_1", "message", "notes")

        if isinstance(first_name, dict):
            first = _get(first_name, "first-name", "first_name") or ""
            last  = _get(first_name, "last-name", "last_name") or ""
            first_name = (first + " " + last).strip() or "Web Opportunity"

        vals = {
            "type": "opportunity",
            "name": first_name,          
            "contact_name": first_name,
            "email_from": email,
            "phone": phone,
            "description": message,
        }
        _logger.info(">>> Creating crm.lead with vals: %s", vals)
        lead = request.env["crm.lead"].sudo().create(vals)
        _logger.info(">>> Created Opportunity ID: %s (name=%s)", lead.id, lead.name)

        resp = request.make_json_response(
            {"ok": True, "id": lead.id, "name": lead.name, "type": lead.type},
            status=201,
        )
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp
