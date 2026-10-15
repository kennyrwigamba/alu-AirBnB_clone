#!/usr/bin/python3
"""User model."""

from models.base_model import BaseModel


class User(BaseModel):
    """Represent a user of the application."""

    email = ""
    password = ""
    first_name = ""
    last_name = ""

    def __init__(self, *args, **kwargs):
        """Initialize a user with common account fields."""
        super().__init__(*args, **kwargs)
        self.email = getattr(self, "email", "")
        self.password = getattr(self, "password", "")
        self.first_name = getattr(self, "first_name", "")
        self.last_name = getattr(self, "last_name", "")
