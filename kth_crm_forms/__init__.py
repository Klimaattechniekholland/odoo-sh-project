# -*- coding: utf-8 -*-
"""
Initialization of the KTH CRM Forms module.  This file ensures that Python
packages within the module are imported so that Odoo can correctly
register models and controllers on installation.
"""

from . import models  # noqa: F401
from . import controllers  # noqa: F401