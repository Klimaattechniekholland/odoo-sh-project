import logging
from pydantic import BaseModel, ValidationError

_logger = logging.getLogger(__name__)

class PydanticMixin:
    """Reusable helper for integrating Pydantic validation into Odoo models."""

    def validate_with_pydantic(self, model: type[BaseModel], data: dict, silent: bool = False) -> BaseModel | None:
        """
        Validate dict data using a Pydantic model class.
        - model: a Pydantic BaseModel class
        - data: dictionary to validate
        - silent: if True, suppress errors and log instead of raising

        Returns:
            Pydantic model instance or None on failure (if silent)
        """
        try:
            return model.model_validate(data)
        except ValidationError as e:
            if not silent:
                _logger.warning("Pydantic validation failed: %s", e)
                return None
            raise