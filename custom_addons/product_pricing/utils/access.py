import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


def _split_xml_id(xml_id):
    if '.' not in xml_id:
        return None, None
    return xml_id.split('.', 1)


def safe_env_ref(env, xml_id):
    try:
        return env.ref(xml_id)
    
    except Exception:
        module, name = _split_xml_id(xml_id)
        if not module:
            return None
        
        rec = env['ir.model.data'].sudo().search([
            ('module', '=', module),
            ('name', '=', name)
        ], limit=1)
        if rec:
            return env[rec.model].browse(rec.res_id)
	    
    return None


def safe_get_or_create_group(env, xml_id, name="Unnamed Group", category_id=None):
    group = safe_env_ref(env, xml_id)
    if group:
        return group

    module, xml_name = _split_xml_id(xml_id)
    if not module or not xml_name:
        raise ValidationError(f"Invalid XML ID format: {xml_id}")

    group = env['res.groups'].sudo().create({
        'name': name,
        'category_id': category_id.id if category_id else None,
    })

    env['ir.model.data'].sudo().create({
        'name': xml_name,
        'module': module,
        'model': 'res.groups',
        'res_id': group.id,
        'noupdate': True,
    })

    _logger.info(f"✅ Created group: {name} ({xml_id})")
    return group
