#!/usr/bin/python3
"""Validate the State model and its inherited behavior."""

from models.state import State
from tests.test_models import test_base_model


class TestState(test_base_model.TestBaseModel):
    """Check State defaults and common model operations."""

    model_class = State
    defaults = {
        'name': '',
    }
