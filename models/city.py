#!/usr/bin/python3
"""City model."""

from models.base_model import BaseModel


class City(BaseModel):
    """Represent a city within a state."""

    state_id = ""
    name = ""

    def __init__(self, *args, **kwargs):
        """Initialize a city with its state and name."""
        super().__init__(*args, **kwargs)
        self.state_id = getattr(self, "state_id", "")
        self.name = getattr(self, "name", "")
