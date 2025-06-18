from pydantic import BaseModel, field_validator
from typing import Literal


class WarningInfo(BaseModel):
    level: Literal['none', 'medium', 'high', 'critical']
    message: str

    @classmethod
    @field_validator('message')
    def validate_message(cls, value, values):
        if values.get('level') != 'none' and not value.strip():
            raise ValueError("Message is required when level is not 'none'")
        return value

    def format(self) -> str:
        return f"[{self.level.upper()}] {self.message}"

    def get_odoo_warning(self) -> dict:
        """Return Odoo-friendly warning dict."""
        return {
            'title': f"Warning: {self.level.capitalize()}",
            'message': self.format(),
            'type': self._map_type(),
        }

    def _map_type(self) -> str:
        """Map level to Odoo warning type."""
        return {
            'critical': 'danger',
            'high': 'danger',
            'medium': 'info',
            'none': 'info',
        }.get(self.level, 'info')
