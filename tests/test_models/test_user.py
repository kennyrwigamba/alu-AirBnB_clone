#!/usr/bin/python3
"""Validate the User model and its inherited behavior."""

from models.user import User
from tests.test_models import test_base_model


class TestUser(test_base_model.TestBaseModel):
    """Check User defaults and common model operations."""

    model_class = User
    defaults = {
        'email': '',
        'password': '',
        'first_name': '',
        'last_name': '',
    }
