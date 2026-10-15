#!/usr/bin/python3
"""Amenity model."""

from models.base_model import BaseModel


class Amenity(BaseModel):
    """Represent an amenity available at a place."""

    name = ""

    def __init__(self, *args, **kwargs):
        """Initialize an amenity with a name."""
        super().__init__(*args, **kwargs)
        self.name = getattr(self, "name", "")
