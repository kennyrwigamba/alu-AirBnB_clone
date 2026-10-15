#!/usr/bin/python3
"""Review model."""

from models.base_model import BaseModel


class Review(BaseModel):
    """Represent a review written for a place."""

    place_id = ""
    user_id = ""
    text = ""

    def __init__(self, *args, **kwargs):
        """Initialize a review with its author, place, and text."""
        super().__init__(*args, **kwargs)
        self.place_id = getattr(self, "place_id", "")
        self.user_id = getattr(self, "user_id", "")
        self.text = getattr(self, "text", "")
