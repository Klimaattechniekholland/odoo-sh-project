import logging
from collections import defaultdict
from odoo import _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class WarningManager:
    LEVEL_MAP = {
        "debug": 0,
        "info": 1,
        "notice": 2,
        "warning": 3,
        "error": 4,
        "critical": 5
    }

    INT_TO_LEVEL = {v: k for k, v in LEVEL_MAP.items()}

    def __init__(self):
        self._warnings = []

    def add(self, level, message, log=True):
        """
        Add a warning message. Accepts level as str or int.
        Automatically logs to Odoo logger if log=True.
        """
        if isinstance(level, int):
            if level not in self.INT_TO_LEVEL:
                raise ValueError(f"Unknown numeric level: {level}")
            level = self.INT_TO_LEVEL[level]
        level = level.lower()

        if level not in self.LEVEL_MAP:
            raise ValueError(f"Unknown level: {level}")

        self._warnings.append({
            "level": level,
            "severity": self.LEVEL_MAP[level],
            "message": str(message)
        })

        if log:
            self._log_to_odoo(level, message)

    def _log_to_odoo(self, level, message):
        """
        Send the message to Odoo logger at appropriate level.
        """
        log_func = getattr(_logger, level, _logger.warning)
        log_func(message)

    def raise_errors(self):
        """
        Raise an Odoo UserError if any 'error' or higher warnings exist.
        """
        threshold = self.LEVEL_MAP["error"]
        messages = [w["message"] for w in self._warnings if w["severity"] >= threshold]
        if messages:
            raise UserError("\n".join(messages))

    def display_up_to(self, max_level):
        """
        Display warnings up to the given level (inclusive).
        Accepts level name or numeric value.
        Returns an Odoo-style {'warning': {'title': ..., 'message': ...}} dict.
        """
        max_sev = self._resolve_level(max_level)
        messages = [w["message"] for w in self._warnings if w["severity"] <= max_sev]

        if messages:
            title = _("Warnings up to %s") % self._localize_level(max_sev)
            return {
                'warning': {
                    'title': f"-- {title} --",
                    'message': "\n".join(messages)
                }
            }
        return {}

    def display_from(self, min_level):
        """
        Display warnings from the given level (inclusive).
        """
        min_sev = self._resolve_level(min_level)
        messages = [w["message"] for w in self._warnings if w["severity"] >= min_sev]

        if messages:
            title = _("Warnings from %s and above") % self._localize_level(min_sev)
            return {
                'warning': {
                    'title': f"-- {title} --",
                    'message': "\n".join(messages)
                }
            }
        return {}

    def _resolve_level(self, level):
        """
        Normalize level name or number to integer severity.
        """
        if isinstance(level, str):
            level = level.lower()
            if level not in self.LEVEL_MAP:
                raise ValueError(f"Unknown level: {level}")
            return self.LEVEL_MAP[level]
        elif isinstance(level, int):
            if level not in self.INT_TO_LEVEL:
                raise ValueError(f"Unknown numeric level: {level}")
            return level
        else:
            raise TypeError("Level must be str or int")

    def _localize_level(self, level_int):
        """
        Return a localized level name from its severity number.
        """
        level = self.INT_TO_LEVEL.get(level_int, str(level_int))
        return _(level.capitalize())
