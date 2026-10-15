#!/usr/bin/python3
"""State model."""

from models.base_model import BaseModel


class State(BaseModel):
    """Represent a geographic state or region."""

    name = ""

    def __init__(self, *args, **kwargs):
        """Initialize a state with a name."""
        super().__init__(*args, **kwargs)
        self.name = getattr(self, "name", "")
